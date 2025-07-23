from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import logging
from typing import Optional

from .utils import analizar_respuestas_p4, analizar_respuestas_p5, cruzar_pilares_4_y_5
from .validators import validar_archivo_csv, detectar_formato_archivo
from .config import API_CONFIG

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Evaluador MEiRA",
    description="API que analiza automáticamente respuestas de formularios MEiRA para los Pilares 4 y 5",
    version="1.1.0"
)

# Configurar CORS para permitir acceso desde diferentes dominios
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "mensaje": "API MEiRA Evaluador Automático",
        "version": "1.1.0",
        "descripcion": "Procesa respuestas de formularios MEiRA para Pilares 4 y 5",
        "endpoints": {
            "/procesar_pilar4/": "Analiza respuestas del Pilar 4 (planificación SMART)",
            "/procesar_pilar5/": "Analiza respuestas del Pilar 5 (evidencias)",
            "/cruzar_pilares/": "Cruza análisis de Pilar 4 y 5",
            "/health": "Estado de la API"
        }
    }

@app.get("/health")
def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "healthy", "message": "API funcionando correctamente"}

def procesar_archivo(file: UploadFile) -> pd.DataFrame:
    """Procesa y valida un archivo subido"""
    try:
        # Validar archivo
        validar_archivo_csv(file)
        
        # Leer archivo
        contenido = file.file.read()
        df = detectar_formato_archivo(contenido, file.filename)
        
        logger.info(f"Archivo procesado: {df.shape[0]} filas, {df.shape[1]} columnas")
        return df
        
    except Exception as e:
        logger.error(f"Error procesando archivo {file.filename}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error procesando archivo: {str(e)}")

def generar_excel_respuesta(df: pd.DataFrame, nombre_hoja: str, nombre_archivo: str) -> StreamingResponse:
    """Genera respuesta Excel con formato mejorado"""
    try:
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=nombre_hoja)
            
            # Obtener worksheet para formatear
            workbook = writer.book
            worksheet = writer.sheets[nombre_hoja]
            
            # Autoajustar ancho de columnas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Congelar primera fila
            worksheet.freeze_panes = "A2"
        
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"}
        )
        
    except Exception as e:
        logger.error(f"Error generando Excel: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generando archivo Excel")

@app.post("/procesar_pilar4/")
async def procesar_pilar4(file: UploadFile = File(...)):
    """
    Procesa respuestas del Pilar 4 (planificación según criterios SMART y MEiRA)
    """
    try:
        logger.info(f"Procesando Pilar 4: {file.filename}")
        
        # Procesar archivo
        df = procesar_archivo(file)
        
        # Analizar respuestas
        df_analizado = analizar_respuestas_p4(df)
        
        if isinstance(df_analizado, dict) and "error" in df_analizado:
            raise HTTPException(status_code=400, detail=df_analizado["error"])
        
        if df_analizado.empty:
            raise HTTPException(status_code=400, detail="No se generaron resultados del análisis")
        
        logger.info(f"Pilar 4 procesado exitosamente: {df_analizado.shape[0]} registros")
        
        return generar_excel_respuesta(
            df_analizado, 
            "Pilar 4 - Planificación", 
            "evaluacion_pilar4_planificacion.xlsx"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en Pilar 4: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/procesar_pilar5/")
async def procesar_pilar5(file: UploadFile = File(...)):
    """
    Procesa respuestas del Pilar 5 (evaluación de evidencias)
    """
    try:
        logger.info(f"Procesando Pilar 5: {file.filename}")
        
        # Procesar archivo
        df = procesar_archivo(file)
        
        # Analizar respuestas
        df_analizado = analizar_respuestas_p5(df)
        
        if isinstance(df_analizado, dict) and "error" in df_analizado:
            raise HTTPException(status_code=400, detail=df_analizado["error"])
        
        if df_analizado.empty:
            raise HTTPException(status_code=400, detail="No se generaron resultados del análisis")
        
        logger.info(f"Pilar 5 procesado exitosamente: {df_analizado.shape[0]} registros")
        
        return generar_excel_respuesta(
            df_analizado, 
            "Pilar 5 - Evidencias", 
            "evaluacion_pilar5_evidencias.xlsx"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en Pilar 5: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/cruzar_pilares/")
async def cruzar_pilares(
    archivo_p4: UploadFile = File(..., description="Archivo CSV con respuestas del Pilar 4"),
    archivo_p5: UploadFile = File(..., description="Archivo CSV con respuestas del Pilar 5")
):
    """
    Cruza los análisis de Pilar 4 y Pilar 5 para evaluación integral
    """
    try:
        logger.info(f"Cruzando pilares: P4={archivo_p4.filename}, P5={archivo_p5.filename}")
        
        # Procesar ambos archivos
        df_p4 = procesar_archivo(archivo_p4)
        df_p5 = procesar_archivo(archivo_p5)
        
        # Analizar cada pilar
        df_p4_analizado = analizar_respuestas_p4(df_p4)
        df_p5_analizado = analizar_respuestas_p5(df_p5)
        
        # Verificar errores
        if isinstance(df_p4_analizado, dict) and "error" in df_p4_analizado:
            raise HTTPException(status_code=400, detail=f"Error en Pilar 4: {df_p4_analizado['error']}")
        
        if isinstance(df_p5_analizado, dict) and "error" in df_p5_analizado:
            raise HTTPException(status_code=400, detail=f"Error en Pilar 5: {df_p5_analizado['error']}")
        
        # Cruzar pilares
        df_cruzado = cruzar_pilares_4_y_5(df_p4_analizado, df_p5_analizado)
        
        if isinstance(df_cruzado, dict) and "error" in df_cruzado:
            raise HTTPException(status_code=400, detail=df_cruzado["error"])
        
        logger.info(f"Pilares cruzados exitosamente: {df_cruzado.shape[0]} registros")
        
        return generar_excel_respuesta(
            df_cruzado, 
            "Evaluación Integral P4-P5", 
            "evaluacion_integral_pilares_4_y_5.xlsx"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado cruzando pilares: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
