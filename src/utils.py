import pandas as pd

def analizar_respuestas_p4(df_largo: pd.DataFrame) -> pd.DataFrame:
    def evaluar_respuesta(respuesta):
        if pd.isna(respuesta):
            return "Sin respuesta"
        respuesta = str(respuesta).lower()
        indicadores = [
            "necesidad de incorporar", "ventajas", "riesgos", "uso responsable", "profundizar", "aprendizaje"
        ]
        return "Cumple" if any(palabra in respuesta for palabra in indicadores) else "No cumple"

    df_largo["Evaluación Pilar 4"] = df_largo["Respuesta"].apply(evaluar_respuesta)
    return df_largo

def analizar_respuestas_p5(df_largo: pd.DataFrame, df_p4: pd.DataFrame) -> pd.DataFrame:
    def evaluar_respuesta(respuesta):
        if pd.isna(respuesta):
            return "Sin respuesta"
        respuesta = str(respuesta).lower()
        indicadores = [
            "análisis de ventajas", "riesgos", "aplicación", "actividad", "divulgación", "guía", "medir resultados"
        ]
        return "Cumple" if any(palabra in respuesta for palabra in indicadores) else "No cumple"

    df_largo["Evaluación Pilar 5"] = df_largo["Respuesta"].apply(evaluar_respuesta)
    return df_largo
