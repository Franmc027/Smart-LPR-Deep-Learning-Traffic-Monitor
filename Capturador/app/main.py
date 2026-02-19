import cv2
import yt_dlp
import time
import os

def capturar_frames(url_youtube, intervalo=10):
    # Opciones más permisivas para evitar bloqueos
    ydl_opts = {
        'format': 'bestvideo[height<=1080][vcodec^=avc1]/best[height<=1080]/best',
        'quiet': True,
        'no_warnings': True,
        # Añadimos un User-Agent para que parezca un navegador real
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Conectando a YouTube: {url_youtube}")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_youtube, download=False)
            
            # Intentamos obtener la URL de varias formas posibles
            url_stream = None
            if 'url' in info:
                url_stream = info['url']
            elif 'formats' in info:
                # Buscamos el primer formato que tenga URL
                for f in info['formats']:
                    if f.get('url'):
                        url_stream = f['url']
                        break
            
            if not url_stream:
                raise KeyError("No se encontró una URL de stream válida en los metadatos")
                
    except Exception as e:
        print(f"Error crítico al extraer la URL: {e}")
        return

    cap = cv2.VideoCapture(url_stream)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print("Error: OpenCV no pudo abrir el stream.")
        return

    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Captura iniciada. Resolución: {ancho}x{alto}")

    ultima_captura = 0
    try:
        while True:
            for _ in range(5): cap.grab()
            ret, frame = cap.retrieve()
            if not ret: break

            tiempo_actual = time.time()
            if tiempo_actual - ultima_captura >= intervalo:
                nombre_foto = f"/app/capturas/frame_{int(tiempo_actual)}.png"
                cv2.imwrite(nombre_foto, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                print(f"Foto guardada: {nombre_foto} ({ancho}x{alto})")
                ultima_captura = tiempo_actual
    finally:
        cap.release()

if __name__ == "__main__":
    URL = "https://www.youtube.com/watch?v=C911U_Fo-QU"
    capturar_frames(URL)