import pandas as pd
import os

# Ruta base de los archivos de parámetros y preguntas
BASE_PATH = os.path.join(os.path.dirname(__file__), "data")

# Cargar archivos base
PREGUNTAS_P4 = pd.read_excel(os.path.join(BASE_PATH, "preguntas_pilar4.xlsx"))
PARAMETROS_P4 = pd.read_excel(os.path.join(BASE_PATH, "parametros_pilar4.xlsx"))
PARAMETROS_P5 = pd.read_excel(os.path.join(BASE_PATH, "parametros_pilar5.xlsx"))

def analizar_respuestas_p4(df_respuestas):
    """
    Evalúa las respuestas del Pilar 4 incluso si no tiene columna 'ID'.
    Detecta columnas 'Respuesta 1', 'Respuesta 2', etc., y las cruza con preguntas y parámetros.
    """
    df = df_respuestas.copy()

    # Detectar columnas tipo 'Respuesta X'
    columnas_respuesta = [col for col in df.columns if "Respuesta" in col]

    if not columnas_respuesta:
        raise ValueError("No se encontraron columnas con 'Respuesta 1', 'Respuesta 2', etc.")

    # Pasar a formato largo
    df_largo = df.melt(
        id_vars=[col for col in df.columns if col not in columnas_respuesta],
        value_vars=columnas_respuesta,
        var_name="ID",
        value_name="Texto"
    )

    # Asegurar que ID coincida con los del Excel base
    df_largo["ID"] = df_largo["ID"].str.strip()

    # Agregar pregunta desde archivo base
    preguntas_dict = dict(zip(PREGUNTAS_P4["ID"], PREGUNTAS_P4["Pregunta"]))
    df_largo["Pregunta"] = df_largo["ID"].map(preguntas_dict)

    # Unir con parámetros del Pilar 4
    df_largo = df_largo.merge(PARAMETROS_P4, how="left", on="ID")

    return df_largo

def analizar_respuestas_p5(df_respuestas, df_p4_previamente_procesado):
    """
    Evalúa las respuestas del Pilar 5 y permite cruzarlas con resultados anteriores del Pilar 4.
    Por ahora, solo agrega evaluación base desde los parámetros.
    """
    df = df_respuestas.copy()
    df = df.merge(PARAMETROS_P5, how="left", on="ID")
    return df
