# Smart-LPR-Deep-Learning-Traffic-Monitor

**Smart-LPR-Deep-Learning-Traffic-Monitor** es un sistema de monitorización de tráfico inteligente diseñado para detectar vehículos, clasificar su carrocería, identificar su color y leer matrículas en tiempo real. 

Este proyecto nace con la filosofía de la **"Tortuga Sabia"**: maximizar la precisión de la Inteligencia Artificial mediante técnicas avanzadas de procesamiento de imagen, permitiendo que funcione de forma robusta incluso en entornos sin tarjeta gráfica (Solo CPU).

---

## 🚀 Características Principales

- **Detección de doble etapa:** Utiliza **YOLOv8 (Medium)** para localizar vehículos y un modelo de clasificación dedicado para identificar el tipo de carrocería.
- **Visión Adaptativa (CLAHE):** Implementa ecualización de histograma adaptativa y filtros de nitidez para "rescatar" matrículas de las sombras o el exceso de brillo.
- **Procesamiento Multi-pasada:** El sistema analiza cada placa bajo tres filtros distintos (CLAHE, Sharpening y Otsu Binarization) para asegurar el éxito del OCR.
- **Arquitectura Dockerizada:** Separación de servicios en contenedores (Capturador + Analizador) para una mejor gestión de recursos.
- **Validación DGT:** Lógica integrada para corregir y validar el formato de matrículas españolas (1234BBB).
- **Registro de Datos:** Exportación automática de avistamientos a `Info_Coches/registro_trafico.csv`.

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.9
* **IA/ML:** YOLOv8 (Ultralytics), EasyOCR.
* **Visión Artificial:** OpenCV (Filtros CLAHE, Lanczos4 Interpolation).
* **Infraestructura:** Docker & Docker Compose.
* **S.O. Recomendado:** Linux / WSL2.

---

## 📁 Estructura del Proyecto

```text
.
├── Analizador/
│   ├── brain.py          # El "Cerebro" con la lógica de IA y Visión
│   └── Dockerfile        # Entorno con PyTorch y dependencias
├── Capturador/
│   ├── capturador.py     # Servicio de extracción de frames de streaming
│   └── Dockerfile        # Entorno ligero de captura
├── capturas/             # Volumen compartido de intercambio de imágenes
│   └── Info_Coches/      # Destino final de los reportes CSV
└── docker-compose.yml    # Orquestación de los contenedores
