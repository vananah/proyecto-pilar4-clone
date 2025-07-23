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
    # Mostrar las columnas disponibles para debugging
    print(f"Columnas disponibles en el DataFrame: {list(df.columns)}")
    
    for col in POSIBLES_COLUMNAS_ID:
        if col in df.columns:
            df = df.rename(columns={col: "ID"})
            print(f"Columna '{col}' renombrada a 'ID'")
            return df
    
    # Mensaje de error más descriptivo
    columnas_disponibles = ", ".join(df.columns)
    mensaje_error = f"No se encontró ninguna columna de identificación válida. Columnas esperadas: {POSIBLES_COLUMNAS_ID}. Columnas disponibles: [{columnas_disponibles}]"
    raise ValueError(mensaje_error)

def analizar_respuestas_p4(df_respuestas):
    """
    Agrega las preguntas correspondientes y evalúa cada respuesta según los parámetros del Pilar 4.
    """
    try:
        df = df_respuestas.copy()
        
        # Verificar que el DataFrame no esté vacío
        if df.empty:
            return {"error": "El DataFrame de respuestas está vacío"}
        
        # Mostrar información del DataFrame para debugging
        print(f"Forma del DataFrame: {df.shape}")
        print(f"Columnas: {list(df.columns)}")
        
        df = normalizar_id(df)

        # Verificar que la columna ID tenga valores
        if df['ID'].isna().all():
            return {"error": "La columna ID no contiene valores válidos"}

        # Associar preguntas al ID
        preguntas_dict = dict(zip(PREGUNTAS_P4["ID"], PREGUNTAS_P4["Pregunta"]))
        df["Pregunta"] = df["ID"].map(preguntas_dict)

        # Unir con los parámetros del Pilar 4 (evaluación)
        df = df.merge(PARAMETROS_P4, how="left", on="ID")

        return df
    except Exception as e:
        # Capturar y devolver el error completo
        print(f"Error en analizar_respuestas_p4: {str(e)}")
        return {"error": f"Error al procesar las respuestas del Pilar 4: {str(e)}"}

def analizar_respuestas_p5(df_respuestas, df_p4_previamente_procesado):
    """
    Evalúa las respuestas del Pilar 5 y permite cruzarlas con resultados anteriores del Pilar 4.
    """
    try:
        df = df_respuestas.copy()
        
        # Verificar que el DataFrame no esté vacío
        if df.empty:
            return {"error": "El DataFrame de respuestas está vacío"}
            
        df = normalizar_id(df)

        # Verificar que la columna ID tenga valores
        if df['ID'].isna().all():
            return {"error": "La columna ID no contiene valores válidos"}

        # Unir con los parámetros del Pilar 5
        df = df.merge(PARAMETROS_P5, how="left", on="ID")

        return df
    except Exception as e:
        # Capturar y devolver el error completo
        print(f"Error en analizar_respuestas_p5: {str(e)}")
        return {"error": f"Error al procesar las respuestas del Pilar 5: {str(e)}"}
