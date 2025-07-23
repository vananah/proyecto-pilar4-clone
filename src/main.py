from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import io

from .utils import analizar_respuestas_p4, analizar_respuestas_p5

app = FastAPI()

@app.get("/")
def read_root():
    return {"mensaje": "API MEiRA lista. Subí tus respuestas para analizarlas en formato CSV o XLSX."}

def transformar_formato_ancho_a_largo(df):
    """Convierte un archivo ancho (una fila por estudiante) al formato largo (una fila por respuesta)."""
    print(f"DataFrame original - Forma: {df.shape}, Columnas: {list(df.columns)}")
    
    columnas_respuestas = [col for col in df.columns if col.lower().startswith("respuesta")]
    print(f"Columnas de respuestas encontradas: {columnas_respuestas}")

    # Buscar columna de identificación
    posibles_ids = ["ID", "id", "Id", "Identificador", "identificador", "Estudiante", "Nombre de usuario", "Correo electrónico"]
    columna_id = next((col for col in posibles_ids if col in df.columns), None)
    print(f"Columna ID encontrada: {columna_id}")

    if not columnas_respuestas:
        # Si no hay columnas "Respuesta", asumir que ya está en formato largo
        print("No se encontraron columnas 'Respuesta'. Asumiendo formato largo.")
        return df

    registros = []
    for idx, fila in df.iterrows():
        identificador = fila.get(columna_id, f"Estudiante_{idx+1}")
        correo = fila.get("Correo electrónico", "")

        for i, col in enumerate(columnas_respuestas, start=1):
            registros.append({
                "Estudiante": identificador,
                "Correo": correo,
                "ID": i,
                "Respuesta": fila[col] if col in fila else None
            })

    df_largo = pd.DataFrame(registros)
    print(f"DataFrame transformado - Forma: {df_largo.shape}, Columnas: {list(df_largo.columns)}")
    return df_largo

def leer_archivo(file: UploadFile):
    """Detecta automáticamente si es CSV o XLSX y lo convierte a DataFrame."""
    contenido = file.file.read()
    nombre = file.filename.lower()

    try:
        if nombre.endswith(".csv"):
            # Intentar diferentes encodings
            try:
                df = pd.read_csv(io.BytesIO(contenido), encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(io.BytesIO(contenido), encoding='latin-1')
                except UnicodeDecodeError:
                    df = pd.read_csv(io.BytesIO(contenido), encoding='cp1252')
        elif nombre.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(contenido))
        else:
            raise ValueError("Formato no compatible. Subí un archivo .csv o .xlsx")
        
        print(f"Archivo leído exitosamente: {df.shape[0]} filas, {df.shape[1]} columnas")
        return df
        
    except Exception as e:
        raise ValueError(f"Error al leer el archivo: {str(e)}")

@app.post("/procesar_pilar4/")
async def procesar_pilar4(file: UploadFile = File(...)):
    try:
        # Validar el archivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="No se proporcionó un archivo")
        
        df_ancho = leer_archivo(file)
        if df_ancho.empty:
            raise HTTPException(status_code=400, detail="El archivo está vacío o mal formateado")

        # Transformar formato si es necesario
        df_largo = transformar_formato_ancho_a_largo(df_ancho)
        
        # Analizar respuestas
        df_analizado = analizar_respuestas_p4(df_largo)

        # Verificar si hubo error en el análisis
        if isinstance(df_analizado, dict) and "error" in df_analizado:
            raise HTTPException(status_code=400, detail=df_analizado["error"])

        if df_analizado.empty:
            raise HTTPException(status_code=400, detail="El análisis no devolvió resultados. Verificá el archivo subido")

        # Generar archivo Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_analizado.to_excel(writer, index=False, sheet_name="Pilar 4 Evaluado")
        output.seek(0)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=resultados_pilar4.xlsx"}
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en procesar_pilar4: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.post("/procesar_pilar5/")
async def procesar_pilar5(file: UploadFile = File(...)):
    try:
        # Validar el archivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="No se proporcionó un archivo")
            
        df = leer_archivo(file)
        if df.empty:
            raise HTTPException(status_code=400, detail="El archivo está vacío o mal formateado")

        # Analizar respuestas (DataFrame vacío para P4 ya que no se está cruzando)
        df_p4_vacio = pd.DataFrame()
        df_analizado = analizar_respuestas_p5(df, df_p4_vacio)

        # Verificar si hubo error en el análisis
        if isinstance(df_analizado, dict) and "error" in df_analizado:
            raise HTTPException(status_code=400, detail=df_analizado["error"])

        if df_analizado.empty:
            raise HTTPException(status_code=400, detail="El análisis no devolvió resultados. Verificá el archivo subido")

        # Generar archivo Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_analizado.to_excel(writer, index=False, sheet_name="Pilar 5 Evaluado")
        output.seek(0)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=resultados_pilar5.xlsx"}
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en procesar_pilar5: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
