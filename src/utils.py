import pandas as pd
import os

# Ruta base de los archivos de parámetros y preguntas
BASE_PATH = os.path.join(os.path.dirname(__file__), "data")

# Archivos base
PREGUNTAS_P4 = pd.read_excel(os.path.join(BASE_PATH, "preguntas_pilar4.xlsx"))
PARAMETROS_P4 = pd.read_excel(os.path.join(BASE_PATH, "parametros_pilar4.xlsx"))
PARAMETROS_P5 = pd.read_excel(os.path.join(BASE_PATH, "parametros_pilar5.xlsx"))

# Columnas posibles para identificar al usuario
POSIBLES_COLUMNAS_ID = [
    'ID', 'Id', 'id',
    'Nombre de usuario', 'Usuario', 'User',
    'Correo electrónico', 'Email', 'Correo',
    'Estudiante', 'Participante',
    'Identificador', 'identificador'
]

def limpiar_datos(df):
    if 'Estado' in df.columns:
        df = df[df['Estado'].str.lower() != 'en curso'].copy()
    columnas_respuesta = [col for col in df.columns if 'respuesta' in col.lower()]
    if columnas_respuesta:
        df = df.dropna(subset=columnas_respuesta, how='all')
    return df

def detectar_columnas_respuesta(df):
    patrones = ['respuesta', 'pregunta', 'answer']
    columnas_respuesta = [col for col in df.columns if any(p in col.lower() for p in patrones)]
    columnas_respuesta.sort(key=lambda c: int(''.join(filter(str.isdigit, c)) or 999))
    return columnas_respuesta

def convertir_a_formato_largo(df):
    df_limpio = limpiar_datos(df)
    columna_id = next((col for col in POSIBLES_COLUMNAS_ID if col in df_limpio.columns), None)
    if not columna_id:
        df_limpio["Usuario_Temporal"] = [f"Usuario_{i+1}" for i in range(len(df_limpio))]
        columna_id = "Usuario_Temporal"

    columnas_respuesta = detectar_columnas_respuesta(df_limpio)
    if not columnas_respuesta:
        return {"error": "No se encontraron columnas de respuesta"}

    registros = []
    for idx, fila in df_limpio.iterrows():
        identificador = fila.get(columna_id, f"Usuario_{idx+1}")
        correo = fila.get('Correo electrónico', fila.get('Email', ''))
        for i, col_resp in enumerate(columnas_respuesta, start=1):
            respuesta = str(fila.get(col_resp, '')).strip()
            if respuesta and respuesta != "-":
                registros.append({
                    'ID_Usuario': identificador,
                    'Correo': correo,
                    'ID': i,
                    'Respuesta': respuesta
                })

    if not registros:
        return {"error": "No se encontraron respuestas válidas"}
    return pd.DataFrame(registros)

def contar_palabras_smart(r):
    if pd.isna(r): return 0
    texto = str(r).lower()
    claves = ['específico', 'medible', 'alcanzable', 'relevante', 'tiempo',
              'indicador', 'meta', 'cronograma', 'objetivo']
    return sum(1 for p in claves if p in texto)

def contar_palabras_evidencia(r):
    if pd.isna(r): return 0
    texto = str(r).lower()
    claves = ['evidencia', 'documento', 'datos', 'archivo', 'fotografía', 'registro']
    return sum(1 for p in claves if p in texto)

def categorizar_respuesta(n):
    if n > 200: return 'Completa'
    elif n > 50: return 'Parcial'
    return 'Insuficiente'

def categorizar_evidencia(n):
    if n > 150: return 'Rica en detalles'
    elif n > 75: return 'Moderada'
    return 'Básica'

def analizar_respuestas_p4(df):
    if df.empty:
        return {"error": "El archivo está vacío"}
    if 'ID' not in df.columns or 'Respuesta' not in df.columns:
        df = convertir_a_formato_largo(df)
        if isinstance(df, dict): return df

    df['Longitud_Respuesta'] = df['Respuesta'].apply(lambda r: len(str(r)))
    df['Palabras_Clave_SMART'] = df['Respuesta'].apply(contar_palabras_smart)
    df['Categoria_Respuesta'] = df['Longitud_Respuesta'].apply(categorizar_respuesta)

    if not PREGUNTAS_P4.empty and 'ID' in PREGUNTAS_P4.columns:
        df['Pregunta'] = df['ID'].map(dict(zip(PREGUNTAS_P4['ID'], PREGUNTAS_P4['Pregunta'])))
    else:
        df['Pregunta'] = df['ID'].apply(lambda i: f"Pregunta {i}")

    if not PARAMETROS_P4.empty:
        df = df.merge(PARAMETROS_P4, how='left', on='ID')
    return df

def analizar_respuestas_p5(df):
    if df.empty:
        return {"error": "El archivo está vacío"}
    if 'ID' not in df.columns or 'Respuesta' not in df.columns:
        df = convertir_a_formato_largo(df)
        if isinstance(df, dict): return df

    df['Longitud_Respuesta'] = df['Respuesta'].apply(lambda r: len(str(r)))
    df['Tiene_Evidencia'] = df['Longitud_Respuesta'].apply(lambda l: 'Sí' if l > 20 else 'No')
    df['Palabras_Evidencia'] = df['Respuesta'].apply(contar_palabras_evidencia)
    df['Categoria_Evidencia'] = df['Longitud_Respuesta'].apply(categorizar_evidencia)

    if not PARAMETROS_P5.empty:
        df = df.merge(PARAMETROS_P5, how='left', on='ID')
    return df
