import pandas as pd
import os

# Ruta base de los archivos de parámetros y preguntas
BASE_PATH = os.path.join(os.path.dirname(__file__), "data")

# Cargar archivos base
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
    """Limpia datos del CSV removiendo filas incompletas"""
    # Remover filas donde el estado sea "En curso" o similar
    if 'Estado' in df.columns:
        df = df[df['Estado'] != 'En curso'].copy()
    
    # Remover filas completamente vacías en las respuestas
    columnas_respuesta = [col for col in df.columns if 'respuesta' in col.lower()]
    if columnas_respuesta:
        # Mantener solo filas que tengan al menos una respuesta no vacía
        df = df.dropna(subset=columnas_respuesta, how='all')
    
    return df

def detectar_columnas_respuesta(df):
    """Detecta todas las columnas de respuesta disponibles"""
    # Buscar columnas que contengan 'respuesta' (con o sin espacio)
    patrones = ['respuesta', 'pregunta', 'answer']
    columnas_respuesta = []
    
    for col in df.columns:
        col_lower = col.lower().strip()
        if any(patron in col_lower for patron in patrones):
            columnas_respuesta.append(col)
    
    # Ordenar por número si es posible
    def extraer_numero(col):
        import re
        numeros = re.findall(r'\d+', col)
        return int(numeros[0]) if numeros else 999
    
    columnas_respuesta.sort(key=extraer_numero)
    return columnas_respuesta

def convertir_a_formato_largo(df):
    """Convierte el CSV a formato largo para procesamiento"""
    print(f"DataFrame original - Forma: {df.shape}")
    print(f"Columnas disponibles: {list(df.columns)}")
    
    # Limpiar datos
    df_limpio = limpiar_datos(df)
    print(f"Después de limpiar - Forma: {df_limpio.shape}")
    
    # Encontrar columna de identificación
    columna_id = None
    for col_posible in POSIBLES_COLUMNAS_ID:
        if col_posible in df_limpio.columns:
            columna_id = col_posible
            break
    
    if not columna_id:
        print("No se encontró columna de ID, usando índice")
        df_limpio['Usuario_Temporal'] = [f"Usuario_{i+1}" for i in range(len(df_limpio))]
        columna_id = 'Usuario_Temporal'
    
    # Detectar columnas de respuesta
    columnas_respuesta = detectar_columnas_respuesta(df_limpio)
    print(f"Columnas de respuesta encontradas: {columnas_respuesta}")
    
    if not columnas_respuesta:
        return {"error": "No se encontraron columnas de respuesta en el archivo"}
    
    # Convertir a formato largo
    registros = []
    for idx, fila in df_limpio.iterrows():
        identificador = fila.get(columna_id, f"Usuario_{idx+1}")
        correo = fila.get('Correo electrónico', fila.get('Email', ''))
        
        for i, col_resp in enumerate(columnas_respuesta, start=1):
            respuesta = fila.get(col_resp, '')
            
            # Solo incluir respuestas que no estén vacías
            if pd.notna(respuesta) and str(respuesta).strip() and str(respuesta).strip() != '-':
                registros.append({
                    'ID_Usuario': identificador,
                    'Correo': correo,
                    'ID': i,  # ID de la pregunta
                    'Respuesta': str(respuesta).strip()
                })
    
    if not registros:
        return {"error": "No se encontraron respuestas válidas en el archivo"}
    
    df_largo = pd.DataFrame(registros)
    print(f"Convertido a formato largo: {len(registros)} registros")
    return df_largo

def analizar_respuestas_p4(df_respuestas):
    """
    Analiza respuestas del Pilar 4 adaptado al formato real del CSV
    """
    try:
        df = df_respuestas.copy()
        
        if df.empty:
            return {"error": "El DataFrame de respuestas está vacío"}
        
        # Convertir a formato largo si es necesario
        if 'ID' not in df.columns or 'Respuesta' not in df.columns:
            resultado_conversion = convertir_a_formato_largo(df)
            if isinstance(resultado_conversion, dict) and "error" in resultado_conversion:
                return resultado_conversion
            df = resultado_conversion
        
        print(f"DataFrame procesado - Forma: {df.shape}")
        
        # Verificar que tengamos las columnas necesarias
        if 'ID' not in df.columns:
            return {"error": "No se pudo crear columna 'ID'"}
        
        if 'Respuesta' not in df.columns:
            return {"error": "No se pudo crear columna 'Respuesta'"}
        
        # Asociar preguntas si están disponibles en los parámetros
        if not PREGUNTAS_P4.empty and 'ID' in PREGUNTAS_P4.columns:
            preguntas_dict = dict(zip(PREGUNTAS_P4["ID"], PREGUNTAS_P4["Pregunta"]))
            df["Pregunta"] = df["ID"].map(preguntas_dict)
        else:
            # Crear preguntas genéricas si no hay archivo de preguntas
            df["Pregunta"] = df["ID"].apply(lambda x: f"Pregunta {x}")
        
        # Agregar análisis básico de las respuestas
        df['Longitud_Respuesta'] = df['Respuesta'].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
        df['Palabras_Clave_SMART'] = df['Respuesta'].apply(contar_palabras_smart)
        df['Categoria_Respuesta'] = df['Longitud_Respuesta'].apply(categorizar_respuesta)
        
        # Unir con parámetros si están disponibles
        if not PARAMETROS_P4.empty and 'ID' in PARAMETROS_P4.columns:
            df = df.merge(PARAMETROS_P4, how="left", on="ID")
        
        print(f"Análisis P4 completado: {len(df)} registros")
        return df
        
    except Exception as e:
        print(f"Error detallado en analizar_respuestas_p4: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": f"Error procesando Pilar 4: {str(e)}"}

def analizar_respuestas_p5(df_respuestas, df_p4_previamente_procesado=None):
    """
    Analiza respuestas del Pilar 5 adaptado al formato real del CSV
    """
    try:
        df = df_respuestas.copy()
        
        if df.empty:
            return {"error": "El DataFrame de respuestas está vacío"}
        
        # Convertir a formato largo si es necesario
        if 'ID' not in df.columns or 'Respuesta' not in df.columns:
            resultado_conversion = convertir_a_formato_largo(df)
            if isinstance(resultado_conversion, dict) and "error" in resultado_conversion:
                return resultado_conversion
            df = resultado_conversion
        
        # Análisis específico para evidencias (Pilar 5)
        df['Tiene_Evidencia'] = df['Respuesta'].apply(
            lambda x: 'Sí' if (pd.notna(x) and len(str(x).strip()) > 20) else 'No'
        )
        
        df['Longitud_Respuesta'] = df['Respuesta'].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
        df['Categoria_Evidencia'] = df['Longitud_Respuesta'].apply(categorizar_evidencia)
        df['Palabras_Evidencia'] = df['Respuesta'].apply(contar_palabras_evidencia)
        
        # Unir con parámetros si están disponibles
        if not PARAMETROS_P5.empty and 'ID' in PARAMETROS_P5.columns:
            df = df.merge(PARAMETROS_P5, how="left", on="ID")
        
        print(f"Análisis P5 completado: {len(df)} registros")
        return df
        
    except Exception as e:
        print(f"Error detallado en analizar_respuestas_p5: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": f"Error procesando Pilar 5: {str(e)}"}

def contar_palabras_smart(respuesta):
    """Cuenta palabras clave relacionadas con criterios SMART"""
    if pd.isna(respuesta):
        return 0
    
    texto = str(respuesta).lower()
    palabras_smart = [
        'específico', 'específicamente', 'concreto', 'preciso',
        'medir', 'medible', 'métrica', 'indicador', 'porcentaje', 'número',
        'alcanzable', 'viable', 'factible', 'posible', 'realista',
        'relevante', 'importante', 'necesario', 'objetivo', 'meta',
        'tiempo', 'fecha', 'plazo', 'cronograma', 'cuando', 'durante'
    ]
    
    contador = sum(1 for palabra in palabras_smart if palabra in texto)
    return contador

def contar_palabras_evidencia(respuesta):
    """Cuenta palabras clave relacionadas con evidencias"""
    if pd.isna(respuesta):
        return 0
    
    texto = str(respuesta).lower()
    palabras_evidencia = [
        'evidencia', 'documento', 'archivo', 'registro', 'fotografía',
        'encuesta', 'entrevista', 'datos', 'resultados', 'informe',
        'análisis', 'evaluación', 'seguimiento', 'monitoreo'
    ]
    
    contador = sum(1 for palabra in palabras_evidencia if palabra in texto)
    return contador

def categorizar_respuesta(longitud):
    """Categoriza respuesta según su longitud"""
    if longitud > 200:
        return 'Completa'
    elif longitud > 50:
        return 'Parcial'
    else:
        return 'Insuficiente'

def categorizar_evidencia(longitud):
    """Categoriza evidencia según su longitud"""
    if longitud > 150:
        return 'Rica en detalles'
    elif longitud > 75:
        return 'Moderada'
    else:
        return 'Básica'
