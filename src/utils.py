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
    Agrega las preguntas correspondientes y evalúa cada respuesta según los parámetros del Pilar 4.
    Retorna un DataFrame con columnas agregadas de texto de pregunta y evaluación.
    """
    df = df_respuestas.copy()

    # Detectar si la columna clave está como 'Nombre de usuario' y renombrarla a 'ID'
    posibles_columnas_id = ['ID', 'Nombre de usuario', 'Usuario', 'Correo electrónico']
    columna_encontrada = None

    for col in posibles_columnas_id:
        if col in df.columns:
            columna_encontrada = col
            break

    if not columna_encontrada:
        return {"error": "No se encontró una columna identificadora como 'ID' o 'Nombre de usuario'"}

    df.rename(columns={columna_encontrada: "ID"}, inplace=True)

    # Asociar preguntas al ID
    preguntas_dict = dict(zip(PREGUNTAS_P4["ID"], PREGUNTAS_P4["Pregunta"]))
    df["Pregunta"] = df["ID"].map(preguntas_dict)

    # Unir con los parámetros del Pilar 4 (evaluación)
    df = df.merge(PARAMETROS_P4, how="left", on="ID")

    return df

def analizar_respuestas_p5(df_respuestas, df_p4_previamente_procesado):
    """
    Evalúa las respuestas del Pilar 5 y permite cruzarlas con resultados anteriores del Pilar 4.
    Por ahora, solo agrega evaluación base desde los parámetros.
    """
    df = df_respuestas.copy()

    # Detectar si la columna clave está como 'Nombre de usuario' y renombrarla a 'ID'
    posibles_columnas_id = ['ID', 'Nombre de usuario', 'Usuario', 'Correo electrónico']
    columna_encontrada = None

    for col in posibles_columnas_id:
        if col in df.columns:
            columna_encontrada = col
            break

    if not columna_encontrada:
        return {"error": "No se encontró una columna identificadora como 'ID' o 'Nombre de usuario'"}

    df.rename(columns={columna_encontrada: "ID"}, inplace=True)

    # Unir con los parámetros del Pilar 5
    df = df.merge(PARAMETROS_P5, how="left", on="ID")

    return df
