from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import pandas as pd
import io

app = FastAPI(openapi_url="/openapi.json")
app.mount("/.well-known", StaticFiles(directory="static/.well-known"), name="well-known")

def cumple_autoeval(row):
    checks = [row.get(f"AE_{i}", False) for i in range(1, 8)]
    return sum(checks), len(checks)

def texto_valido(txt, min_pal=30):
    return isinstance(txt, str) and len(txt.split()) >= min_pal

def clasificar(row):
    suma, total = cumple_autoeval(row)
    pct = suma / total if total else 0
    if not texto_valido(row.get("Descripción","")):
        return "Descartado", "Descripción insuficiente"
    if pct == 1:
        return "Pre-aprobado", "Cumple todos"
    if pct >= 0.7:
        return "Revisión humana", f"{suma}/{total} mínimos"
    return "Descartado", f"{suma}/{total} mínimos"

@app.post("/classify")
async def classify(file: UploadFile = File(...)):
    df = pd.read_excel(await file.read(), engine="openpyxl")
    df[["Clasificación","Comentario"]] = df.apply(lambda r: pd.Series(clasificar(r)), axis=1)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    return StreamingResponse(buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition":"attachment; filename=clasificado.xlsx"})
