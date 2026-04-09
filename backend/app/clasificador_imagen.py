import numpy as np
from pathlib import Path
from PIL import Image
import io

CATEGORIAS = [
    "arte",
    "autos",
    "bebes",
    "comida",
    "deportes",
    "educacion",
    "mascotas",
    "motos",
    "mujeres",
    "musica",
    "naturaleza",
    "peliculas",
    "salud",
    "trabajo",
    "viajes",
]

CATEGORIAS_MODERADAS = {"bebes"}

UMBRAL_CONFIANZA = 40.0

IMG_SIZE = (128, 128)
MODEL_PATH = Path(__file__).parent.parent / "ml_models" / "modelo_clasificador.h5"

_model = None

def get_model():
    global _model
    if _model is None:
        import tensorflow as tf
        _model = tf.keras.models.load_model(str(MODEL_PATH))
    return _model

def _predecir_frame(img_rgb: np.ndarray) -> np.ndarray:
    img = Image.fromarray(img_rgb).resize(IMG_SIZE, Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)
    return get_model().predict(arr, verbose=0)[0]

def _construir_resultado(promedio: np.ndarray, frames_analizados: int) -> dict:
    indice = int(np.argmax(promedio))
    categoria = CATEGORIAS[indice]
    confianza = round(float(promedio[indice]) * 100, 2)

    return {
        "categoria": categoria,
        "confianza": confianza,
        "es_moderada": categoria in CATEGORIAS_MODERADAS and confianza >= UMBRAL_CONFIANZA,
        "confianza_suficiente": confianza >= UMBRAL_CONFIANZA,
        "frames_analizados": frames_analizados,
    }

def clasificar_imagen(archivo) -> dict:
    try:
        contenido = archivo.read()
        archivo.seek(0)

        img = Image.open(io.BytesIO(contenido)).convert("RGB")
        img_arr = np.array(img)

        prediccion = _predecir_frame(img_arr)
        return _construir_resultado(prediccion, frames_analizados=1)

    except Exception as e:
        print(f"[clasificador] Error al clasificar imagen: {e}")
        return None
    
def clasificar_video(video_path: str) -> dict | None:
    try:
        import cv2

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames == 0 or fps == 0:
            cap.release()
            print("[clasificador] Video vacio o sin FPS")
            return None
        
        duracion = total_frames / fps
        frames_a_extraer = max(10, min(20, int(duracion)))
        step = max(1, total_frames // frames_a_extraer)

        predicciones = []
        count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if count % step == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                prediccion = _predecir_frame(frame_rgb)
                predicciones.append(prediccion)

            count += 1

        cap.release()

        if not predicciones:
            print("[clasificador] No se pudieron extraer frames del video")
            return None
        
        promedio = np.mean(predicciones, axis=0)
        return _construir_resultado(promedio, frames_analizados=len(predicciones))
    
    except Exception as e:
        print(f"[clasificador] Error al clasificar video: {e}")
        return None