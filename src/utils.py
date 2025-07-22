import pandas as pd
import os

# Ruta base de los archivos de parámetros y preguntas
BASE_PATH = os.path.join(os.path.dirname(__file__), "data")

# Cargar archivos base
PREGUNTAS_P4 = pd.read_excel(os.path.join(BASE_PATH, "preguntas_pilar4.xlsx"))
PARAMETROS_P4 = pd.read_excel(os.path.join(BASE_PATH, "parametros_pilar4.xlsx"))
PARAMETROS_P5 = pd.read_excel(os.path.join(BASE_PATH, "parametros_pilar5.xlsx"))

# Columnas posibles para identificar al usuario
POSIBLES_COLUMNAS_ID = ['ID', 'Nombre de usuario', 'Usuario', 'Correo electrónico']

def normalizar_id(df):
    """
    Renombra cualquier columna de identificación válida a 'ID'
    """
    for col in POSIBLES_COLUMNAS_ID:
        if col in df.columns:
            df = df.rename(columns={col: "ID"})
            return df
    raise ValueError("No se encontró ninguna columna de identificación válida como 'ID', 'Nombre de usuario', etc.")

def analizar_respuestas_p4(df_respuestas):
    """
    Agrega las preguntas correspondientes y evalúa cada respuesta según los parámetros del Pilar 4.
    """
    try:
        df = df_respuestas.copy()
        df = normalizar_id(df)

        # Asociar preguntas al ID
        preguntas_dict = dict(zip(PREGUNTAS_P4["ID"], PREGUNTAS_P4["Pregunta"]))
        df["Pregunta"] = df["ID"].map(preguntas_dict)

        # Unir con los parámetros del Pilar 4 (evaluación)
        df = df.merge(PARAMETROS_P4, how="left", on="ID")

        return df
    except Exception as e:
        return {"error": str(e)}

def analizar_respuestas_p5(df_respuestas, df_p4_previamente_procesado):
    """
    Evalúa las respuestas del Pilar 5 y permite cruzarlas con resultados anteriores del Pilar 4.
    """
    try:
        df = df_respuestas.copy()
        df = normalizar_id(df)

        # Unir con los parámetros del Pilar 5
        df = df.merge(PARAMETROS_P5, how="left", on="ID")

        return df
    except Exception as e:
        return {"error": str(e)}

