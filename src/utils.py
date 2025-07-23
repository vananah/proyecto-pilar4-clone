import pandas as pd
import os
import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Ruta base de los archivos de parámetros y preguntas
BASE_PATH = os.path.join(os.path.dirname(__file__), "data")

def cargar_archivos_base():
    """Carga los archivos base con manejo de errores"""
    try:
        preguntas_p4 = pd.read_excel(os.path.join(BASE_PATH, "preguntas_pilar4.xlsx"))
        parametros_p4 = pd.read_excel(os.path.join(BASE_PATH, "parametros_pilar4.xlsx"))
        parametros_p5 = pd.read_excel(os.path.join(BASE_PATH, "parametros_pilar5.xlsx"))
        
        logger.info("Archivos base cargados exitosamente")
        return preguntas_p4, parametros_p4, parametros_p5
        
    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {e}")
        raise ValueError(f"No se pudo cargar archivo de configuración: {e}")
    except Exception as e:
        logger.error(f"Error cargando archivos base: {e}")
        raise ValueError(f"Error en archivos de configuración: {e}")

# Cargar archivos base
PREGUNTAS_P4, PARAMETROS_P4, PARAMETROS_P5 = cargar_archivos_base()

# Columnas posibles para identificar al usuario (más opciones)
POSIBLES_COLUMNAS_ID = [
    'ID', 'Id', 'id',
    'Nombre de usuario', 'Usuario', 'User',
    'Correo electrónico', 'Email', 'Correo',
    'Estudiante', 'Participante',
    'Identificador', 'identificador'
]

def detectar_formato_datos(df: pd.DataFrame) -> str:
    """Detecta si los datos están en formato ancho o largo"""
    columnas_respuesta = [col for col in df.columns if 'respuesta' in col.lower()]
    
    if columnas_respuesta:
        return "ancho"  # Una columna por respuesta
    elif 'Respuesta' in df.columns or 'respuesta' in df.columns:
        return "largo"   # Una fila por respuesta
    else:
        return "desconocido"

def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza nombres de columnas para facilitar el procesamiento"""
    df_normalizado = df.copy()
    
    # Diccionario de mapeo para normalizar nombres
    mapeo_columnas = {
        'correo electrónico': 'Correo',
        'email': 'Correo',
        'nombre de usuario': 'Usuario',
        'user': 'Usuario',
        'estudiante': 'Estudiante',
        'participante': 'Estudiante'
    }
    
    # Normalizar nombres de columnas
    nuevos_nombres = {}
    for col in df_normalizado.columns:
        col_lower = col.lower().strip()
        if col_lower in mapeo_columnas:
            nuevos_nombres[col] = mapeo_columnas[col_lower]
    
    if nuevos_nombres:
        df_normalizado = df_normalizado.rename(columns=nuevos_nombres)
        logger.info(f"Columnas normalizadas: {nuevos_nombres}")
    
    return df_normalizado

def encontrar_columna_id(df: pd.DataFrame) -> Optional[str]:
    """Encuentra la columna de identificación más apropiada"""
    for col_posible in POSIBLES_COLUMNAS_ID:
        if col_posible in df.columns:
            # Verificar que la columna tenga valores válidos
            valores_no_nulos = df[col_posible].dropna()
            if not valores_no_nulos.empty:
                logger.info(f"Columna ID encontrada: {col_posible}")
                return col_posible
    
    return None

def transformar_formato_ancho_a_largo(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte formato ancho (columnas por respuesta) a largo (filas por respuesta)"""
    df_normalizado = normalizar_columnas(df)
    
    # Encontrar columnas de respuestas
    columnas_respuestas = [col for col in df_normalizado.columns if 'respuesta' in col.lower()]
    
    if not columnas_respuestas:
        logger.warning("No se encontraron columnas de respuestas, asumiendo formato largo")
        return df_normalizado
    
    # Encontrar columna de identificación
    columna_id = encontrar_columna_id(df_normalizado)
    
    registros = []
    for idx, fila in df_normalizado.iterrows():
        identificador = fila.get(columna_id, f"Usuario_{idx+1}") if columna_id else f"Usuario_{idx+1}"
        correo = fila.get('Correo', '')
        
        for i, col_resp in enumerate(columnas_respuestas, start=1):
            registros.append({
                'ID_Usuario': identificador,
                'Correo': correo,
                'ID': i,  # ID de la pregunta
                'Respuesta': fila.get(col_resp, '')
            })
    
    df_largo = pd.DataFrame(registros)
    logger.info(f"Transformado a formato largo: {len(registros)} registros")
    return df_largo

def evaluar_criterios_smart(respuesta: str, criterios: Dict) -> Dict:
    """Evalúa una respuesta según criterios SMART para Pilar 4"""
    if pd.isna(respuesta) or not respuesta.strip():
        return {
            'cumple_especifico': False,
            'cumple_medible': False,
            'cumple_alcanzable': False,
            'cumple_relevante': False,
            'cumple_temporal': False,
            'puntuacion_total': 0,
            'observaciones': 'Respuesta vacía'
        }
    
    respuesta_lower = respuesta.lower()
    evaluacion = {}
    puntuacion = 0
    
    # Específico: buscar palabras clave de especificidad
    palabras_especificas = ['específicamente', 'concretamente', 'exactamente', 'precisamente']
    evaluacion['cumple_especifico'] = any(palabra in respuesta_lower for palabra in palabras_especificas)
    if evaluacion['cumple_especifico']: puntuacion += 1
    
    # Medible: buscar números, porcentajes, métricas
    patron_medible = r'\d+|%|porcentaje|cantidad|número|métrica|indicador'
    evaluacion['cumple_medible'] = bool(re.search(patron_medible, respuesta_lower))
    if evaluacion['cumple_medible']: puntuacion += 1
    
    # Alcanzable: buscar palabras de viabilidad
    palabras_alcanzables = ['posible', 'viable', 'factible', 'alcanzable', 'realista']
    evaluacion['cumple_alcanzable'] = any(palabra in respuesta_lower for palabra in palabras_alcanzables)
    if evaluacion['cumple_alcanzable']: puntuacion += 1
    
    # Relevante: buscar conexión con objetivos
    palabras_relevantes = ['importante', 'relevante', 'necesario', 'objetivo', 'meta']
    evaluacion['cumple_relevante'] = any(palabra in respuesta_lower for palabra in palabras_relevantes)
    if evaluacion['cumple_relevante']: puntuacion += 1
    
    # Temporal: buscar referencias temporales
    patron_temporal = r'día|semana|mes|año|fecha|plazo|tiempo|cuando|durante'
    evaluacion['cumple_temporal'] = bool(re.search(patron_temporal, respuesta_lower))
    if evaluacion['cumple_temporal']: puntuacion += 1
    
    evaluacion['puntuacion_total'] = puntuacion
    evaluacion['observaciones'] = f"Cumple {puntuacion}/5 criterios SMART"
    
    return evaluacion

def analizar_respuestas_p4(df_respuestas: pd.DataFrame) -> pd.DataFrame:
    """Analiza respuestas del Pilar 4 con criterios SMART y MEiRA"""
    try:
        df = df_respuestas.copy()
        
        if df.empty:
            return {"error": "DataFrame vacío para Pilar 4"}
        
        # Detectar y convertir formato si es necesario
        formato = detectar_formato_datos(df)
        logger.info(f"Formato detectado para Pilar 4: {formato}")
        
        if formato == "ancho":
            df = transformar_formato_ancho_a_largo(df)
        elif formato == "desconocido":
            return {"error": "No se pudo detectar el formato de los datos del Pilar 4"}
        
        # Verificar columnas necesarias
        if 'ID' not in df.columns:
            return {"error": "No se encontró columna 'ID' en los datos del Pilar 4"}
        
        if 'Respuesta' not in df.columns:
            return {"error": "No se encontró columna 'Respuesta' en los datos del Pilar 4"}
        
        # Agregar preguntas
        preguntas_dict = dict(zip(PREGUNTAS_P4["ID"], PREGUNTAS_P4["Pregunta"]))
        df["Pregunta"] = df["ID"].map(preguntas_dict)
        
        # Evaluar cada respuesta con criterios SMART
        evaluaciones = []
        for _, fila in df.iterrows():
            eval_smart = evaluar_criterios_smart(
                fila['Respuesta'], 
                {} # Criterios específicos pueden venir de PARAMETROS_P4
            )
            evaluaciones.append(eval_smart)
        
        # Agregar evaluaciones al DataFrame
        df_evaluaciones = pd.DataFrame(evaluaciones)
        df_final = pd.concat([df, df_evaluaciones], axis=1)
        
        # Unir con parámetros adicionales
        df_final = df_final.merge(PARAMETROS_P4, how="left", on="ID")
        
        logger.info(f"Pilar 4 analizado: {len(df_final)} registros procesados")
        return df_final
        
    except Exception as e:
        logger.error(f"Error analizando Pilar 4: {str(e)}")
        return {"error": f"Error procesando Pilar 4: {str(e)}"}

def analizar_respuestas_p5(df_respuestas: pd.DataFrame) -> pd.DataFrame:
    """Analiza respuestas del Pilar 5 (evidencias)"""
    try:
        df = df_respuestas.copy()
        
        if df.empty:
            return {"error": "DataFrame vacío para Pilar 5"}
        
        # Detectar y convertir formato si es necesario
        formato = detectar_formato_datos(df)
        logger.info(f"Formato detectado para Pilar 5: {formato}")
        
        if formato == "ancho":
            df = transformar_formato_ancho_a_largo(df)
        elif formato == "desconocido":
            return {"error": "No se pudo detectar el formato de los datos del Pilar 5"}
        
        # Verificar columnas necesarias
        if 'ID' not in df.columns:
            return {"error": "No se encontró columna 'ID' en los datos del Pilar 5"}
        
        # Evaluar calidad de evidencias
        df['tiene_evidencia'] = df['Respuesta'].apply(
            lambda x: not pd.isna(x) and len(str(x).strip()) > 10
        )
        
        df['longitud_respuesta'] = df['Respuesta'].apply(
            lambda x: len(str(x)) if not pd.isna(x) else 0
        )
        
        df['categoria_respuesta'] = df['longitud_respuesta'].apply(
            lambda x: 'Completa' if x > 100 else 'Parcial' if x > 20 else 'Insuficiente'
        )
        
        # Unir con parámetros del Pilar 5
        df_final = df.merge(PARAMETROS_P5, how="left", on="ID")
        
        logger.info(f"Pilar 5 analizado: {len(df_final)} registros procesados")
        return df_final
        
    except Exception as e:
        logger.error(f"Error analizando Pilar 5: {str(e)}")
        return {"error": f"Error procesando Pilar 5: {str(e)}"}

def cruzar_pilares_4_y_5(df_p4: pd.DataFrame, df_p5: pd.DataFrame) -> pd.DataFrame:
    """Cruza análisis de Pilar 4 y Pilar 5 para evaluación integral"""
    try:
        if df_p4.empty or df_p5.empty:
            return {"error": "Uno de los DataFrames está vacío para el cruce"}
        
        # Identificar columna de usuario para el cruce
        col_usuario_p4 = 'ID_Usuario' if 'ID_Usuario' in df_p4.columns else 'Usuario'
        col_usuario_p5 = 'ID_Usuario' if 'ID_Usuario' in df_p5.columns else 'Usuario'
        
        if col_usuario_p4 not in df_p4.columns or col_usuario_p5 not in df_p5.columns:
            return {"error": "No se encontraron columnas de usuario para realizar el cruce"}
        
        # Preparar datos para cruce
        df_p4_resumen = df_p4.groupby(col_usuario_p4).agg({
            'puntuacion_total': 'mean',
            'cumple_especifico': 'mean',
            'cumple_medible': 'mean',
            'cumple_alcanzable': 'mean',
            'cumple_relevante': 'mean',
            'cumple_temporal': 'mean'
        }).reset_index()
        df_p4_resumen.columns = [col_usuario_p4] + [f'P4_{col}' for col in df_p4_resumen.columns[1:]]
        
        df_p5_resumen = df_p5.groupby(col_usuario_p5).agg({
            'tiene_evidencia': 'mean',
            'longitud_respuesta': 'mean',
            'categoria_respuesta': lambda x: x.mode().iloc[0] if not x.empty else 'Sin datos'
        }).reset_index()
        df_p5_resumen.columns = [col_usuario_p5] + [f'P5_{col}' for col in df_p5_resumen.columns[1:]]
        
        # Realizar cruce
        df_cruzado = df_p4_resumen.merge(
            df_p5_resumen, 
            left_on=col_usuario_p4, 
            right_on=col_usuario_p5, 
            how='outer',
            suffixes=('_P4', '_P5')
        )
        
        # Calcular puntuación integral
        df_cruzado['puntuacion_integral'] = (
            df_cruzado['P4_puntuacion_total'].fillna(0) * 0.6 +
            df_cruzado['P5_tiene_evidencia'].fillna(0) * 5 * 0.4
        )
        
        df_cruzado['categoria_integral'] = df_cruzado['puntuacion_integral'].apply(
            lambda x: 'Excelente' if x >= 4 else 'Bueno' if x >= 3 else 'Regular' if x >= 2 else 'Insuficiente'
        )
        
        logger.info(f"Pilares cruzados: {len(df_cruzado)} usuarios evaluados")
        return df_cruzado
        
    except Exception as e:
        logger.error(f"Error cruzando pilares: {str(e)}")
        return {"error": f"Error en cruce de pilares: {str(e)}"}
