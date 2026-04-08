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

def clasificar_imagen(archivo) -> dict:
    try:
        contenido = archivo.read()
        archivo.seek(0)

        img = Image.open(io.BytesIO(contenido)).convert("RGB")
        img = img.resize(IMG_SIZE, Image.LANCZOS)

        arr = np.array(img, dtype=np.float32) / 255.0
        arr = np.expand_dims(arr, axis=0)

        modelo      = get_model()
        prediccion  = modelo.predict(arr, verbose=0)[0]

        indice     = int(np.argmax(prediccion))
        categoria  = CATEGORIAS[indice]
        confianza  = float(prediccion[indice]) * 100

        return {
            "categoria":           categoria,
            "confianza":           round(confianza, 2),
            "es_moderada":         categoria in CATEGORIAS_MODERADAS and confianza >= UMBRAL_CONFIANZA,
            "confianza_suficiente": confianza >= UMBRAL_CONFIANZA,
        }

    except Exception as e:
        print(f"[clasificador] Error al clasificar imagen: {e}")
        return None