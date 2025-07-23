"""
Configuraciones centralizadas para el Evaluador MEiRA
"""
import os
from typing import Dict, List

# Configuración de la API
API_CONFIG = {
    "title": "Evaluador MEiRA",
    "description": "API que analiza automáticamente respuestas de formularios MEiRA para los Pilares 4 y 5",
    "version": "1.1.0",
    "contact": {
        "name": "Soporte MEiRA",
        "email": "soporte@meira.edu"
    }
}

# Configuración de archivos
FILE_CONFIG = {
    "max_size_mb": 10,
    "allowed_extensions": ['.csv', '.xlsx', '.xls'],
    "min_rows": 1,
    "max_rows": 10000,
    "encodings_csv": ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
}

# Rutas de archivos de datos
BASE_PATH = os.path.join(os.path.dirname(__file__), "data")
DATA_FILES = {
    "preguntas_p4": os.path.join(BASE_PATH, "preguntas_pilar4.xlsx"),
    "parametros_p4": os.path.join(BASE_PATH, "parametros_pilar4.xlsx"),
    "parametros_p5": os.path.join(BASE_PATH, "parametros_pilar5.xlsx")
}

# Configuración de columnas esperadas
COLUMNS_CONFIG = {
    "posibles_id": [
        'ID', 'Id', 'id',
        'Nombre de usuario', 'Usuario', 'User',
        'Correo electrónico', 'Email', 'Correo',
        'Estudiante', 'Participante',
        'Identificador', 'identificador'
    ],
    "mapeo_normalizacion": {
        'correo electrónico': 'Correo',
        'email': 'Correo',
        'nombre de usuario': 'Usuario',
        'user': 'Usuario',
        'estudiante': 'Estudiante',
        'participante': 'Estudiante'
    }
}

# Configuración de evaluación SMART para Pilar 4
SMART_CRITERIA = {
    "especifico": {
        "palabras_clave": ['específicamente', 'concretamente', 'exactamente', 'precisamente'],
        "peso": 1
    },
    "medible": {
        "patron": r'\d+|%|porcentaje|cantidad|número|métrica|indicador',
        "peso": 1
    },
    "alcanzable": {
        "palabras_clave": ['posible', 'viable', 'factible', 'alcanzable', 'realista'],
        "peso": 1
    },
    "relevante": {
        "palabras_clave": ['importante', 'relevante', 'necesario', 'objetivo', 'meta'],
        "peso": 1
    },
    "temporal": {
        "patron": r'día|semana|mes|año|fecha|plazo|tiempo|cuando|durante',
        "peso": 1
    }
}

# Configuración de evaluación para Pilar 5
EVIDENCE_CRITERIA = {
    "longitud_minima": 10,
    "categorias": {
        "completa": 100,
        "parcial": 20,
        "insuficiente": 0
    }
}

# Configuración de puntuación integral
SCORING_CONFIG = {
    "peso_pilar4": 0.6,
    "peso_pilar5": 0.4,
    "categorias_integrales": {
        "excelente": 4.0,
        "bueno": 3.0,
        "regular": 2.0,
        "insuficiente": 0.0
    }
}

# Configuración de Excel
EXCEL_CONFIG = {
    "max_column_width": 50,
    "default_column_width": 15,
    "freeze_panes": "A2",
    "sheets": {
        "pilar4": "Pilar 4 - Planificación",
        "pilar5": "Pilar 5 - Evidencias", 
        "integral": "Evaluación Integral P4-P5"
    }
}

# Mensajes de error comunes
ERROR_MESSAGES = {
    "file_empty": "El archivo está vacío o mal formateado",
    "no_file": "No se proporcionó un archivo",
    "invalid_format": "Formato no compatible. Use archivos .csv o .xlsx",
    "file_too_large": "Archivo demasiado grande. Máximo permitido: {max_size}MB",
    "no_data": "No se generaron resultados del análisis",
    "processing_error": "Error procesando archivo: {error}",
    "internal_error": "Error interno del servidor: {error}"
}

# Configuración de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": ["console"]
}

def get_error_message(key: str, **kwargs) -> str:
    """Obtiene mensaje de error formateado"""
    message = ERROR_MESSAGES.get(key, "Error desconocido")
    return message.format(**kwargs)

def validate_config():
    """Valida que todos los archivos de configuración existan"""
    missing_files = []
    
    for name, path in DATA_FILES.items():
        if not os.path.exists(path):
            missing_files.append(f"{name}: {path}")
    
    if missing_files:
        raise FileNotFoundError(f"Archivos de configuración faltantes: {missing_files}")
    
    return True
