# proyecto-pilar4-clone
# MEiRA Evaluador Automático

Este proyecto permite analizar automáticamente respuestas de formularios vinculados a los Pilares 4 y 5 del Marco MEiRA mediante una API desarrollada con FastAPI y desplegada en Render.

El objetivo es facilitar la evaluación de planes y evidencias entregadas por estudiantes, generando archivos Excel con análisis automatizados, colores diferenciados y estructura clara para revisión docente.

---

## Funcionalidades

- Procesamiento del Pilar 4: análisis de planificación según criterios SMART y MEiRA.
- Procesamiento del Pilar 5: evaluación de evidencias y preparación para cruce con el Pilar 4.
- Generación automática de archivos Excel con respuestas, evaluaciones y formato de revisión.
- No requiere re-subida constante de archivos base (plantillas y parámetros).

---

## Cómo usarlo

### 1. Procesar Pilar 4

- **Endpoint:** `/procesar_pilar4/`
- **Método:** POST
- **Archivo requerido:** CSV exportado del formulario de respuestas del Pilar 4
- **Resultado:** archivo Excel con análisis automatizado

### 2. Procesar Pilar 5

- **Endpoint:** `/procesar_pilar5/`
- **Método:** POST
- **Archivo requerido:** CSV exportado del formulario de respuestas del Pilar 5
- **Resultado:** archivo Excel con evaluación de evidencias

> Nota: para el cruce Pilar 4 - Pilar 5, se agregará una función adicional en futuras versiones.

---

## Estructura del proyecto

---

## Tecnologías utilizadas

- Python 3.10+
- FastAPI
- Pandas
- Uvicorn
- OpenPyXL

---

## Despliegue en Render

1. Crear un nuevo Web Service en [Render.com](https://render.com).
2. Usar este repositorio de GitHub.
3. Configurar:
   - Runtime: **Python 3.10+**
   - Start command:  
     ```
     uvicorn src.main:app --host 0.0.0.0 --port 10000
     ```
   - Dependencies: definidas en `requirements.txt`

---

## Consideraciones

- La evaluación es anónima utilizando un campo "ID de usuario".
- Los archivos base (plantillas y parámetros) están embebidos en el proyecto en `src/data/`.
- La API no almacena los datos procesados: solo analiza y devuelve el resultado.
- Si se desea evaluar el cruce Pilar 4 - 5, el archivo del Pilar 4 deberá re-subirse.

---




