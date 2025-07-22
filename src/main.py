from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from src.utils import procesar_excel
import shutil
import os

app = FastAPI()

# Monta los archivos estáticos si usás HTML en /static
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return {"mensaje": "Agente IA Pilar 4 activo y funcionando correctamente"}

@app.post("/analizar")
async def analizar(file: UploadFile = File(...)):
    archivo_entrada = "entrada.xlsx"
    archivo_salida = "salida.xlsx"

    # Guardar archivo subido temporalmente
    with open(archivo_entrada, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Procesar el Excel
    try:
        procesar_excel(archivo_entrada, archivo_salida)
    except Exception as e:
        return {"error": str(e)}

    # Devolver el archivo procesado
    return FileResponse(archivo_salida, filename="resultado_pilar4.xlsx")
