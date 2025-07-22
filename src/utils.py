import pandas as pd

def generar_feedback(respuesta):
    texto = str(respuesta).lower().strip()
    if not texto:
        return "🟥 Desaprobado – Respuesta vacía"
    elif any(p in texto for p in ["no sé", "ni idea", "?"]):
        return "🟨 Revisión – Duda o inseguridad"
    elif len(texto) < 20:
        return "🟨 Revisión – Respuesta muy breve"
    else:
        return "🟩 Aprobado – Respuesta clara"

def procesar_excel(input_path, output_path):
    df = pd.read_excel(input_path)

    if "Respuesta" not in df.columns:
        raise ValueError("El archivo debe contener una columna llamada 'Respuesta'.")

    df["Evaluación IA"] = df["Respuesta"].apply(generar_feedback)
    df.to_excel(output_path, index=False)
