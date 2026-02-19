import os
import time
import cv2
import easyocr
import re
import csv
import numpy as np
from datetime import datetime
from ultralytics import YOLO

# --- NUEVA CONFIGURACIÓN DE RUTA ---
# Se guarda dentro de la carpeta compartida para que lo veas desde fuera de Docker
CARPETA_INFO = "/app/capturas/Info_Coches"
CSV_FILE = os.path.join(CARPETA_INFO, "registro_trafico.csv")

def guardar_en_csv(datos):
    """Guarda una fila en el CSV dentro de la carpeta Info_Coches."""
    # Creamos la carpeta si no existe
    if not os.path.exists(CARPETA_INFO):
        os.makedirs(CARPETA_INFO)
        print(f"📁 Carpeta creada: {CARPETA_INFO}")

    archivo_existe = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f)
        if not archivo_existe:
            # Cabecera del Excel
            escritor.writerow(["Fecha", "Hora", "Archivo", "Tipo", "Color", "Matricula"])
        escritor.writerow(datos)

def obtener_nombre_color(bgr):
    colores = {
        "Blanco": [240, 240, 240], "Negro": [20, 20, 20],
        "Gris": [120, 120, 120], "Rojo": [60, 60, 200],
        "Azul": [180, 100, 50], "Plata": [190, 190, 190],
        "Oscuro": [40, 40, 40]
    }
    b, g, r = bgr
    min_dist = float('inf')
    color_nombre = "Desconocido"
    for nombre, valores in colores.items():
        dist = np.sqrt((r-valores[2])**2 + (g-valores[1])**2 + (b-valores[0])**2)
        if dist < min_dist:
            min_dist = dist
            color_nombre = nombre
    return color_nombre

def corregir_matricula_espana(texto):
    texto = re.sub(r'[^A-Z0-9]', '', texto.upper())
    if len(texto) < 7: return None
    num_a_letra = {'0': 'O', '1': 'I', '2': 'Z', '5': 'S', '8': 'B'}
    letra_a_num = {'O': '0', 'I': '1', 'Z': '2', 'S': '5', 'B': '8'}
    parte_num, parte_let = texto[:4], texto[-3:]
    for l, n in letra_a_num.items(): parte_num = parte_num.replace(l, n)
    for n, l in num_a_letra.items(): parte_let = parte_let.replace(n, l)
    final = parte_num + parte_let
    if re.match(r'^\d{4}[BCDFGHJKLMNPQRSTVWXYZ]{3}$', final):
        return final
    return None

def generar_pasadas_imagen(img_recorte):
    gray = cv2.cvtColor(img_recorte, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    v1 = clahe.apply(gray)
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    v2 = cv2.filter2D(v1, -1, kernel)
    _, v3 = cv2.threshold(v2, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return [v1, v2, v3]

def procesar_imagenes():
    print(f"🐢 'Tortuga Sabia' guardando en: {CARPETA_INFO}")
    model_det = YOLO('yolov8m.pt') 
    model_cls = YOLO('yolov8m-cls.pt') 
    reader = easyocr.Reader(['es'], gpu=False)
    
    ruta_capturas = "/app/capturas"
    whitelist_vehiculos = ['car', 'van', 'truck', 'jeep', 'wagon', 'racer', 'cab', 'bus', 'vehicle', 'minivan', 'pickup']

    while True:
        archivos = sorted([f for f in os.listdir(ruta_capturas) if f.endswith(('.png', '.jpg'))])
        if not archivos:
            time.sleep(2); continue

        archivo = archivos[0]
        ruta_foto = os.path.join(ruta_capturas, archivo)
        time.sleep(1.0)
        img = cv2.imread(ruta_foto)
        if img is None:
            if os.path.exists(ruta_foto): os.remove(ruta_foto)
            continue

        results = model_det(img, conf=0.45, verbose=False)

        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) in [2, 5, 7]:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    recorte_coche = img[max(0, y1-10):y2+10, max(0, x1-10):x2+10]
                    if recorte_coche.size == 0: continue

                    # 1. CLASIFICACIÓN TIPO
                    res_cls = model_cls(recorte_coche, verbose=False)
                    info_vehiculo = "Vehiculo Generico"
                    probs = res_cls[0].probs
                    for idx in probs.top5:
                        nombre_clase = res_cls[0].names[idx].lower()
                        if any(v in nombre_clase for v in whitelist_vehiculos) and probs.data[idx] > 0.3:
                            info_vehiculo = nombre_clase.replace('_', ' ').title()
                            break

                    # 2. COLOR
                    h_c, w_c, _ = recorte_coche.shape
                    zona_color = recorte_coche[int(h_c*0.5):int(h_c*0.7), int(w_c*0.4):int(w_c*0.6)]
                    color_name = obtener_nombre_color(np.mean(zona_color, axis=(0, 1))) if zona_color.size > 0 else "N/A"

                    # 3. MATRÍCULA
                    zona_placa = recorte_coche[int(h_c*0.6):, :]
                    matricula_final = "No detectada"
                    if zona_placa.size > 0:
                        pasadas = generar_pasadas_imagen(zona_placa)
                        for img_pasada in pasadas:
                            img_ready = cv2.resize(img_pasada, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_LANCZOS4)
                            res_ocr = reader.readtext(img_ready, detail=0, beamWidth=10, contrast_ths=0.1)
                            for t in res_ocr:
                                validada = corregir_matricula_espana(t)
                                if validada:
                                    matricula_final = validada; break
                            if matricula_final != "No detectada": break

                    # --- GUARDAR DATOS EN LA NUEVA CARPETA ---
                    ahora = datetime.now()
                    fecha = ahora.strftime("%Y-%m-%d")
                    hora = ahora.strftime("%H:%M:%S")
                    
                    fila = [fecha, hora, archivo, info_vehiculo, color_name, matricula_final]
                    guardar_en_csv(fila)
                    
                    print(f"✅ Registro limpio en Info_Coches: {matricula_final} | {info_vehiculo}")

        if os.path.exists(ruta_foto): os.remove(ruta_foto)
        time.sleep(1.5)

if __name__ == "__main__":
    procesar_imagenes()