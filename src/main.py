from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import pandas as pd
import io

from utils import analizar_respuestas_p4, analizar_respuestas_p5

app = FastAPI(
    title="MEiRA Evaluador",
    description="Subí tus respuestas en CSV para obtener el análisis de los pilares 4 y 5.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "mensaje": "✅ API MEiRA en funcionamiento. Usá /procesar_pilar4 o /procesar_pilar5 para analizar tus respuestas."
    }

@app.post("/procesar_pilar4/", summary="Procesar Pilar 4", description="Subí un archivo CSV con respuestas del Pilar 4.")
async def procesar_pilar4(file: UploadFile = File(...)):
    try:
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
    except Exception as e:
        return {"error": f"Ocurrió un problema procesando Pilar 4: {str(e)}"}

@app.post("/procesar_pilar5/", summary="Procesar Pilar 5", description="Subí un archivo CSV con respuestas del Pilar 5.")
async def procesar_pilar5(file: UploadFile = File(...)):
    try:
        contenido = await file.read()
        df_respuestas = pd.read_csv(io.BytesIO(contenido))

        # ⚠️ Por ahora no hacemos cruce con Pilar 4. Cuando esté disponible, reemplazá esta línea.
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
    except Exception as e:
        return {"error": f"Ocurrió un problema procesando Pilar 5: {str(e)}"}
