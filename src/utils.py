import pandas as pd
import os

# Ruta base de los archivos
BASE_PATH = os.path.join(os.path.dirname(__file__), "data")

# Cargar archivos base una vez
PREGUNTAS_P4 = pd.read_excel(os.path.join(BASE_PATH, "preguntas_pilar4.xlsx"))
PARAMETROS_P4 = pd.read_excel(os.path.join(BASE_PATH, "parametros_pilar4.xlsx"))
PARAMETROS_P5 = pd.read_excel(os.path.join(BASE_PATH, "parametros_pilar5.xlsx"))

def analizar_respuestas_p4(df_respuestas):
    """Agrega las preguntas del Pilar 4 y evalúa según los parámetros."""
    df = df_respuestas.copy()

    # Agregar texto de pregunta
    preguntas_dict = dict(zip(PREGUNTAS_P4["ID"], PREGUNTAS_P4["Pregunta"]))
    df["Pregunta"] = df["ID"].map(preguntas_dict)

    # Evaluación básica (ejemplo con Nivel de logro)
    df = df.merge(PARAMETROS_P4, how="left", left_on="ID", right_on="ID")

    return df

def analizar_respuestas_p5(df_respuestas, df_p4_previamente_procesado):
    """Evalúa las respuestas del Pilar 5 y las cruza con las del Pilar 4."""
    df = df_respuestas.copy()

    # Evaluación base según parámetros del Pilar 5
    df = df.merge(PARAMETROS_P5, how="left", on="ID")

    # Acá podés agregar lógica de cruce con P4 (por ejemplo, por ID de estudiante)
    # Esto se puede ajustar a medida que se define el formato final de ambas entregas

    return df
