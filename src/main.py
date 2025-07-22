from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import pandas as pd
import io

from utils import analizar_respuestas_p4, analizar_respuestas_p5

app = FastAPI()

@app.get("/")
def read_root():
    return {"mensaje": "API MEiRA lista. Subí tus respuestas para analizarlas."}

@app.post("/procesar_pilar4/")
async def procesar_pilar4(file: UploadFile = File(...)):
    contenido = await file.read()
    df_respuestas = pd.read_csv(io.BytesIO(contenido))

    df_analizado = analizar_respuestas_p4(df_respuestas)

    # Convertir a Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_analizado.to_excel(writer, index=False, sheet_name="Pilar 4 Evaluado")
    output.seek(0)

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=resultados_pilar4.xlsx"})

@app.post("/procesar_pilar5/")
async def procesar_pilar5(file: UploadFile = File(...)):
    contenido = await file.read()
    df_respuestas = pd.read_csv(io.BytesIO(contenido))

    # ⚠️ Si más adelante necesitás cruzar con resultados de P4:
    df_p4_vacio = pd.DataFrame()  # Por ahora está vacío, lo conectamos luego
    df_analizado = analizar_respuestas_p5(df_respuestas, df_p4_vacio)

    # Convertir a Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_analizado.to_excel(writer, index=False, sheet_name="Pilar 5 Evaluado")
    output.seek(0)

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=resultados_pilar5.xlsx"})
