from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import sys
import os

# Asegura que src/ esté en el path de Python
sys.path.append(os.path.dirname(__file__))

from utils import analizar_respuestas_p4, analizar_respuestas_p5

app = FastAPI(
    title="Clasificador Pilar 4 y 5",
    version="1.0",
    description="API que evalúa automáticamente las respuestas de estudiantes para los Pilares 4 y 5 del modelo MEiRA."
)

@app.get("/")
def read_root():
    return {
        "mensaje": "API MEiRA lista. Subí tus respuestas para analizarlas.",
        "endpoints_disponibles": [
            "/procesar_pilar4/",
            "/procesar_pilar5/"
        ]
    }

@app.post("/procesar_pilar4/")
async def procesar_pilar4(file: UploadFile = File(...)):
    contenido = await file.read()
    df_respuestas = pd.read_csv(io.BytesIO(contenido))

    df_analizado = analizar_respuestas_p4(df_respuestas)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_analizado.to_excel(writer, index=False, sheet_name="Pilar 4 Evaluado")
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=resultados_pilar4.xlsx"}
    )

@app.post("/procesar_pilar5/")
async def procesar_pilar5(file: UploadFile = File(...)):
    contenido = await file.read()
    df_respuestas = pd.read_csv(io.BytesIO(contenido))

    # ⚠️ Más adelante se podrá cruzar con Pilar 4 real si se desea
    df_p4_vacio = pd.DataFrame()
    df_analizado = analizar_respuestas_p5(df_respuestas, df_p4_vacio)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_analizado.to_excel(writer, index=False, sheet_name="Pilar 5 Evaluado")
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=resultados_pilar5.xlsx"}
    )
