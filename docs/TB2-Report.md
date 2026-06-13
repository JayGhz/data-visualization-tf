#  Informe Técnico de Ingeniería de Datos
**Arquitectura de Pipelines de Datos y Enriquecimiento Semántico**

## 1. Introducción
Este documento detalla la infraestructura técnica y las decisiones de ingeniería de datos aplicadas para transformar los datasets de inversión pública del MEF en un activo analítico de alta fidelidad. Se ha implementado un ecosistema basado en la **Arquitectura Medallion** utilizando **Polars** como motor de procesamiento de alto rendimiento.

---

## 2. Ingeniería de Ingesta (Capa Bronze)
La ingesta se diseñó bajo los principios de **idempotencia** y **fidelidad cruda**.

- **Estrategia de Descarga**: El script `00_download_data.py` utiliza un mecanismo de "Smart Download" que verifica la existencia y el tamaño del archivo local antes de iniciar la transferencia, ahorrando ancho de banda y tiempo.
- **Persistencia en Parquet**: Se abandonó el uso de CSV en las capas intermedias. La conversión a Parquet reduce el tamaño en disco en un ~70% y permite el uso de **Predicate Pushdown** y **Proyección de Columnas**, optimizando la lectura selectiva.
- **Esquema de Ingesta**: Para evitar errores de truncamiento o inferencia incorrecta, la Capa Bronze fuerza todas las columnas a tipo `String`. Esto garantiza que caracteres especiales o formatos de fecha inconsistentes no rompan el pipeline inicial.

---

## 3. Orquestación y Modularidad
El sistema se orquesta mediante un controlador centralizado (`run_pipeline.py`).

- **Desacoplamiento**: Cada etapa del pipeline (`Bronze`, `Silver`, `Gold`) es un módulo independiente que puede ejecutarse de forma aislada.
- **Inyección de Dependencias**: El controlador gestiona dinámicamente el `sys.path`, permitiendo que los scripts se comuniquen sin dependencias circulares y facilitando las pruebas unitarias por capa.
- **Control de Flujo**: Se implementó un argumento `--from` que permite reanudar el pipeline desde cualquier punto, esencial para iterar en la lógica de negocio (Gold) sin tener que re-procesar o re-descargar datos crudos.

---

## 4. Ingeniería de Transformación y Calidad (Capa Silver)
Esta es la fase de procesamiento pesado donde el dato se convierte en información.

### A. Limpieza de Datos
- **Normalización**: Eliminación sistemática de artefactos de CSV (comillas dobles, espacios en blanco residuales) mediante expresiones vectorizadas en Polars.
- **Manejo de Nulos**: Se implementó una lógica de **Imputación Estratégica**:
    - Variables de texto: `fill_null("DESCONOCIDO")`.
    - Avance Físico: Se aplica una unión diagonal de múltiples fuentes, priorizando los datos del Formato 12B (más recientes) sobre los de Detalle.
- **Validación de Fechas**: Se detectaron registros con el año **2039**. La ingeniería de datos aplica un "clipping" o nulificación controlada de estas fechas para evitar que funciones de agregación temporal (como promedios de duración) se contaminen con valores atípicos.

### B. Enriquecimiento mediante NLP Híbrido
Se integró una etapa de **procesamiento de lenguaje natural** dentro del flujo de datos:
1. **Paso 1 (Regex)**: Clasificación de alta velocidad para patrones conocidos (Social, Presupuesto).
2. **Paso 2 (Embeddings)**: Para los textos ambiguos, se utiliza el modelo `all-MiniLM-L6-v2` para generar vectores semánticos y calcular la similitud de coseno contra "anclas" de categorías de problemas.
3. **Optimización**: El modelo solo se aplica sobre textos únicos (reduciendo la carga de 200k a ~2k llamadas), lo que permite que una tarea de ML pesado se integre en un pipeline de datos de < 1 minuto.

---

## 5. Modelado de Negocio y Feature Engineering (Capa Gold)
La Capa Gold materializa los indicadores que consumirá el dashboard.

- **Feature Engineering**:
    - `BRECHA`: Cálculo diferencial vectorial: `(Avance Financiero - Avance Físico)`. Un valor > 0 indica sobre-gasto sin ejecución física.
    - `DIAS_SIN_REPORTE`: Cálculo de delta de tiempo usando la fecha actual vs `ULT_FEC_DECLA_ESTIM`.
- **Integridad Referencial**: Se realizó una auditoría de cardinalidad del `CODIGO_UNICO`. Se descubrió que el dataset de **Cierre** tiene un traslape nulo con **Detalle**, pero ambos se cruzan con **F12B**. El pipeline resuelve esto mediante un `left join` complejo que preserva el universo completo de proyectos (369k+ registros).

---

## 6. Stack Tecnológico y Rendimiento
- **Motor**: Polars (Multi-threading nativo en Rust).
- **IA**: Sentence-Transformers (HuggingFace).
- **Reportes**: Tablas dinámicas en Markdown para trazabilidad de auditoría.
- **Velocidad**: Pipeline de punta a punta en **~65 segundos** para un volumen de datos crudos de ~1GB.

---
