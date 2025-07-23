import pandas as pd

# Preguntas del Pilar 4 (en orden)
PREGUNTAS_P4 = [
    "¿Por qué considera necesario incorporar IA en el ámbito educativo?",
    "¿Qué ventajas puede ofrecer la IA en los procesos de enseñanza y aprendizaje?",
    "¿Qué riesgos y desafíos puede implicar el uso de IA en educación?",
    "¿Qué estrategias propondría para promover un uso responsable y ético de la IA en su institución?",
    "¿Qué aspectos considera importantes profundizar para fortalecer su comprensión sobre la IA?",
    "¿Cómo espera que el aprendizaje sobre IA impacte en su práctica profesional?"
]

def evaluar_respuesta_p4(respuesta, pregunta):
    if pd.isna(respuesta) or not str(respuesta).strip():
        return "Vacía", "La respuesta está vacía o no se ha completado."
    
    respuesta = str(respuesta).lower()

    claves_pregunta = {
        0: ["necesario", "importante", "relevante", "incorporar", "fundamental"],
        1: ["ventaja", "mejorar", "beneficio", "oportunidad", "fortalecer"],
        2: ["riesgo", "desafío", "problema", "peligro", "preocupación"],
        3: ["estrategia", "ética", "responsable", "lineamiento", "norma"],
        4: ["profundizar", "aprender", "conocer más", "formación", "capacitación"],
        5: ["impacto", "cambio", "mejorar", "transformar", "aplicar"]
    }

    indice = PREGUNTAS_P4.index(pregunta)
    claves = claves_pregunta.get(indice, [])

    if any(palabra in respuesta for palabra in claves):
        return "Adecuada", f"La respuesta incluye términos relevantes como: {', '.join([p for p in claves if p in respuesta])}."
    else:
        return "Débil", "La respuesta no desarrolla adecuadamente los aspectos esperados para esta pregunta."

def analizar_respuestas_p4(df_largo: pd.DataFrame) -> pd.DataFrame:
    df_largo["Pregunta"] = df_largo["ID"].apply(lambda x: PREGUNTAS_P4[x - 1] if 0 < x <= len(PREGUNTAS_P4) else "Pregunta desconocida")

    evaluaciones = df_largo.apply(lambda fila: evaluar_respuesta_p4(fila["Respuesta"], fila["Pregunta"]), axis=1)
    df_largo["Evaluación Pilar 4"] = [e[0] for e in evaluaciones]
    df_largo["Explicación"] = [e[1] for e in evaluaciones]

    resumen = df_largo.groupby("Estudiante")["Evaluación Pilar 4"].apply(
        lambda evals: "Cumple" if all(e == "Adecuada" for e in evals) else "No cumple"
    ).reset_index().rename(columns={"Evaluación Pilar 4": "Clasificación General"})

    df_final = df_largo.merge(resumen, on="Estudiante", how="left")
    return df_final
