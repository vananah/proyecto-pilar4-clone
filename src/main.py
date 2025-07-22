from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from src.utils import procesar_excel
import shutil
import os

app = FastAPI()

# Para servir archivos estáticos si querés usar HTML en /static
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return {"mensaje": "Agente IA Pilar 4 activo"}

@app.post("/analizar")
async def analizar(file: UploadFile = File(...)):
    entrada = "entrada.xlsx"
    salida = "salida.xlsx"

    with open(entrada, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        procesar_excel(entrada, salida)
    except Exception as e:
        return {"error": str(e)}

    return FileResponse(salida, filename="resultado_pilar4.xlsx")

