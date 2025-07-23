from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import pandas as pd
import io

from src.utils import analizar_respuestas_p4

app = FastAPI()

@app.get("/")
def read_root():
    return {"mensaje": "API MEiRA lista. Subí tus respuestas para analizarlas en formato CSV o XLSX."}

def transformar_formato_ancho_a_largo(df):
    columnas_respuestas = [col for col in df.columns if col.lower().startswith("respuesta")]

    posibles_ids = [
        "ID", "id", "Id", "Identificador", "identificador",
        "Correo electrónico", "correo electrónico", "Correo", "correo",
        "Nombre", "Nombre completo", "Apellido(s)", "Nombre y Apellido"
    ]
    columna_id = next((col for col in posibles_ids if col in df.columns), None)

    if not columna_id:
        raise ValueError("No se encontró una columna de identificación válida como 'ID', 'Correo', 'Nombre', etc.")

    registros = []
    for idx, fila in df.iterrows():
        identificador = fila.get(columna_id, f"Estudiante_{idx+1}")
        for i, col in enumerate(columnas_respuestas, start=1):
            registros.append({
                "Estudiante": identificador,
                "ID": i,
                "Respuesta": fila[col]
            })

    return pd.DataFrame(registros)

def leer_archivo(file: UploadFile):
    contenido = file.file.read()
    nombre = file.filename.lower()

    if nombre.endswith(".csv"):
        return pd.read_csv(io.BytesIO(contenido))
    elif nombre.endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(contenido))
    else:
        raise ValueError("Formato no compatible. Subí un archivo .csv o .xlsx")

@app.post("/procesar_pilar4/")
async def procesar_pilar4(file: UploadFile = File(...)):
    try:
        df_ancho = leer_archivo(file)
        df_largo = transformar_formato_ancho_a_largo(df_ancho)
        df_analizado = analizar_respuestas_p4(df_largo)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_analizado.to_excel(writer, index=False, sheet_name="Pilar 4 Evaluado")
        output.seek(0)

        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers={"Content-Disposition": "attachment; filename=Informe_Pilar4_Explicado.xlsx"})
    except Exception as e:
        return {"error": str(e)}
