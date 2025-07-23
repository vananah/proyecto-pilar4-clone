from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from utils import analizar_respuestas_p4, analizar_respuestas_p5
import pandas as pd
from io import BytesIO

app = FastAPI(title="API MEiRA", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"mensaje": "API MEiRA lista. Subí tus respuestas para analizarlas en formato CSV o XLSX."}

@app.post("/procesar_pilar4/")
async def procesar_pilar4(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents)) if file.filename.endswith((".xlsx", ".xls")) else pd.read_csv(BytesIO(contents))
        resultado = analizar_respuestas_p4(df)
        if isinstance(resultado, dict) and "error" in resultado:
            return resultado
        return resultado.to_dict(orient="records")
    except Exception as e:
        return {"error": f"Error procesando archivo Pilar 4: {str(e)}"}

@app.post("/procesar_pilar5/")
async def procesar_pilar5(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents)) if file.filename.endswith((".xlsx", ".xls")) else pd.read_csv(BytesIO(contents))
        resultado = analizar_respuestas_p5(df)
        if isinstance(resultado, dict) and "error" in resultado:
            return resultado
        return resultado.to_dict(orient="records")
    except Exception as e:
        return {"error": f"Error procesando archivo Pilar 5: {str(e)}"}
