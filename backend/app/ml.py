import os
import tensorflow as tf
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

modelo_completo = tf.keras.models.load_model(
    os.path.join(BASE_DIR, 'ml_models/modelo_sentimientos_completo.keras'),
    custom_objects={'TextVectorization': tf.keras.layers.TextVectorization}
)

vectorizer = modelo_completo.layers[0]
modelo = modelo_completo.layers[1]

def analizar_comentario(texto):
    try:
        datos = vectorizer([texto])
        prediccion = modelo.predict(datos, verbose=0)[0]
        clases = ['negative', 'neutral', 'positive']
        sentimiento = clases[prediccion.argmax()]
        confianza = round(prediccion.max() * 100, 2)
        print(f"Sentimiento: {sentimiento}, Confianza: {confianza}%")
        return sentimiento, confianza
    except Exception as e:
        print(f"Error al analizar comentario: {e}")
        return 'neutral', 0.0