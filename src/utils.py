import pandas as pd
import os

# Ruta base de los archivos de parámetros y preguntas
BASE_PATH = os.path.join(os.path.dirname(__file__), "data")

# Cargar archivos base
PREGUNTAS_P4 = pd.read_excel(os.path.join(BASE_PATH, "preguntas_pilar4.xlsx"))
PARAMETROS_P4 = pd.read_excel(os.path.join(BASE_PATH, "parametros_pilar4.xlsx"))
PARAMETROS_P5 = pd.read_excel(os.path.join(BASE_PATH, "parametros_pilar5.xlsx"))

def analizar_respuestas_p4(df_respuestas):
    df = df_respuestas.copy()

    # Detectar columna de ID o nombre
    posibles_columnas_id = ['ID', 'Nombre de usuario', 'Usuario', 'Correo electrónico']
    columna_encontrada = next((col for col in posibles_columnas_id if col in df.columns), None)

    if not columna_encontrada:
        return {"error": "No se encontró una columna identificadora como 'ID', 'Nombre de usuario', etc."}

    df.rename(columns={columna_encontrada: "ID"}, inplace=True)

    # Asociar texto de la pregunta según el número de pregunta
    preguntas_dict = dict(zip(PREGUNTAS_P4["ID"], PREGUNTAS_P4["Pregunta"]))
    df["Pregunta"] = df["ID"].map(preguntas_dict)

    # Evaluar comparando con los parámetros
    df = df.merge(PARAMETROS_P4, how="left", on="ID")
    return df

def analizar_respuestas_p5(df_respuestas, df_p4_previamente_procesado):
    df = df_respuestas.copy()

    posibles_columnas_id = ['ID', 'Nombre de usuario', 'Usuario', 'Correo electrónico']
    columna_encontrada = next((col for col in posibles_columnas_id if col in df.columns), None)

    if not columna_encontrada:
        return {"error": "No se encontró una columna identificadora como 'ID', 'Nombre de usuario', etc."}

    df.rename(columns={columna_encontrada: "ID"}, inplace=True)

    df = df.merge(PARAMETROS_P5, how="left", on="ID")
    return df
