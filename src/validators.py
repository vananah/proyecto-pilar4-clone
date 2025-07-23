import pandas as pd
import io
from fastapi import UploadFile, HTTPException
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Configuración de validaciones
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls']
MIN_ROWS = 1
MAX_ROWS = 10000

def validar_archivo_csv(file: UploadFile) -> None:
    """Valida que el archivo sea válido para procesamiento"""
    
    # Validar que se haya subido un archivo
    if not file.filename:
        raise HTTPException(status_code=400, detail="No se ha subido ningún archivo")
    
    # Validar extensión
    extension = '.' + file.filename.lower().split('.')[-1]
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Formato no permitido. Use: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validar tamaño (aproximado basado en content-length si está disponible)
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"Archivo demasiado grande. Máximo permitido: {MAX_FILE_SIZE/1024/1024:.1f}MB"
        )
    
    logger.info(f"Archivo validado: {file.filename}")

def detectar_formato_archivo(contenido: bytes, nombre_archivo: str) -> pd.DataFrame:
    """Detecta el formato y lee el archivo apropiadamente"""
    
    try:
        nombre_lower = nombre_archivo.lower()
        
        if nombre_lower.endswith('.csv'):
            # Intentar diferentes encodings para CSV
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(io.BytesIO(contenido), encoding=encoding)
                    logger.info(f"CSV leído con encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("No se pudo decodificar el archivo CSV con ningún encoding soportado")
        
        elif nombre_lower.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contenido))
            logger.info("Archivo Excel leído exitosamente")
        
        else:
            raise ValueError(f"Extensión no soportada: {nombre_archivo}")
        
        # Validar contenido del DataFrame
        validar_contenido_dataframe(df, nombre_archivo)
        
        return df
        
    except pd.errors.EmptyDataError:
        raise ValueError("El archivo está vacío")
    except pd.errors.ParserError as e:
        raise ValueError(f"Error parseando archivo: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error leyendo archivo {nombre_archivo}: {str(e)}")

def validar_contenido_dataframe(df: pd.DataFrame
