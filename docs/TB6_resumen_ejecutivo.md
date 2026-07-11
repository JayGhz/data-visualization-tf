# E6 — Resumen Ejecutivo

**Proyecto:** Brecha de eficiencia en la inversión pública peruana (MEF 2020–2026)
**Curso:** Data Visualization CC0211 · UPC
**Entrega:** 6 — Trabajo final completo y defensa

---

## Pregunta analítica

¿En qué medida la ejecución financiera de las inversiones públicas refleja el avance real de las obras, y qué sectores o regiones presentan los mayores cuellos de botella durante el periodo 2020–2026?

El producto responde con un dashboard de Tableau centrado en la métrica **BRECHA** (`AVANCE_EJECUCION − AVANCE_FISICO`, en puntos porcentuales): valores positivos indican que se gasta más rápido de lo que se construye (alerta de fiscalización); valores negativos, que la obra avanza más rápido que el registro del gasto (desfase administrativo).

## Metodología (pipeline en 6 pasos)

1. **Ingesta (Bronze)** — `00_download_data.py` + `01_bronze.py`: descarga de 3 datasets del portal de Datos Abiertos del MEF (detalle de inversiones, Formato 12-B, cierre de inversiones) y conversión CSV → Parquet sin lógica de negocio, para preservar trazabilidad del dato original.
2. **Perfilado** — `02_eda_preliminary.py`: nulos, cardinalidad, duplicados y solapamiento de llaves (`CODIGO_UNICO`) entre las 3 fuentes antes de decidir el merge.
3. **Limpieza y consolidación (Silver)** — `03_silver.py`: tipado, homologación de categorías, merge de fuentes y clasificación NLP de los problemas reportados en texto libre.
4. **Métricas de negocio (Gold)** — `04_gold.py`: derivación de BRECHA, DIAS_SIN_REPORTE, DIAS_ARRANQUE, DIAS_PLANIFICADOS y flags de calidad; reglas de negocio (proyectos cerrados sin reporte físico se asumen 100 %, avances > 100 % se limitan a 100).
5. **Esquema estrella** — `06_star_schema.py`: `fact_inversiones` (291,453 proyectos, 1 fila por proyecto) + 5 dimensiones con llaves sustitutas, semáforos (`SEMAFORO_BRECHA`, `SEMAFORO_REPORTE`) y segmentos (`RANGO_COSTO`) listos para Tableau.
6. **Componente avanzado (PCA)** — `07_pca.py`: PCA con scikit-learn sobre 6 métricas numéricas (imputación por mediana + estandarización z-score), exportado como `pca_proyectos.csv` para el módulo avanzado del dashboard.

## Hallazgos principales

- **La brecha promedio es negativa (−12.2 pp; mediana 0)** entre los 103,785 proyectos con brecha calculable: en el agregado, el avance físico va *por delante* del gasto registrado. El problema dominante no es el sobregasto generalizado, sino el desfase y la calidad del registro administrativo.
- **La opacidad de reporte es el cuello de botella principal: el 64.4 % de la cartera (187,668 proyectos) no permite calcular la brecha** por nulos en avance físico o financiero, y 75,255 proyectos llevan más de 90 días sin reportar (46,234 de ellos aún activos, es decir, 1 de cada 4 proyectos activos).
- **Existe un núcleo pequeño pero grave de proyectos desalineados: 20 CRITICO y 256 ALERTA.** Los críticos promedian solo 7.2 % de avance físico habiendo ejecutado 25.2 % de su presupuesto, concentran S/ 69.3 millones de costo actualizado, y 18 de los 20 pertenecen a **Gobiernos Locales** — el nivel de gobierno que además concentra el 80 % de los proyectos con brecha calculable.
- **El PCA valida estadísticamente la segmentación del dashboard:** PC2 (19.9 % de varianza) contrapone BRECHA (+0.70) contra AVANCE_FISICO (−0.65) — exactamente el eje de la pregunta analítica — y los proyectos CRITICO/ALERTA se separan en la zona alta del plano sin que el algoritmo conociera el semáforo. PC1 (25.0 %) ordena madurez financiera y antigüedad de reporte (AVANCE_EJECUCION +0.69, DIAS_SIN_REPORTE +0.61).
- **El costo del proyecto casi no pesa en ningún componente (cargas < 0.05):** los megaproyectos no son intrínsecamente más propensos a la desalineación financiero-física que los proyectos pequeños; el riesgo se explica por comportamiento de ejecución y reporte, no por envergadura presupuestal.

## Limitaciones del análisis

- **Cobertura de la métrica central:** BRECHA solo es calculable para el 35.6 % de la cartera; los hallazgos sobre desalineación describen ese subconjunto, y el resto se reporta como `SIN DATO` (decisión explícita en lugar de imputar la métrica de negocio).
- **Fotografía, no historia:** la fact tiene granularidad de 1 fila por proyecto con valores acumulados a la fecha de corte; no se reconstruye la trayectoria mensual de cada proyecto.
- **Bug detectado y corregido en QA — llaves de tiempo:** la validación de integridad del notebook final detectó que `SK_Tiempo` se corrompía por un overflow de Int8 en polars 1.40.1 (`month*100` desbordaba antes del cast a Int64): 35.6 % de SK duplicados en `dim_tiempo` y joins inflados de 291,453 a 514,634 filas. Se corrigió la fórmula (cast a Int64 antes de multiplicar), se extendió el calendario a 2040 (hay proyectos con fin planificado en 2036) y se regeneró el esquema estrella; la validación posterior confirma 0 duplicados y join sin inflación.
- **Imputación del PCA:** la mediana imputa el 64 % de los valores de BRECHA con 0 y el 19 % de AVANCE_FISICO con 100, lo que compacta el centro del plano PCA; los componentes describen la estructura de los datos observados más los supuestos de imputación.
- **PC1+PC2 explican 44.9 % de la varianza:** el plano PCA es una proyección para priorizar fiscalización, no un modelo completo del fenómeno.
- Los datos reflejan lo **declarado** por las entidades en el Banco de Inversiones; no se audita la veracidad del avance físico reportado.

## Recomendaciones accionables

1. **Priorizar la fiscalización en el cuadrante PC1-alto / PC2-alto** del módulo PCA: proyectos con presupuesto ya consumido, reporte desactualizado y brecha alta — empezando por los 20 CRITICO (S/ 69.3 M, 90 % en Gobiernos Locales).
2. **Atacar la opacidad antes que la brecha:** exigir actualización de reporte a los 46,234 proyectos activos con más de 90 días de silencio; sin reporte no hay brecha medible ni control posible.
3. **Focalizar asistencia técnica en Gobiernos Locales**, que concentran tanto el volumen de cartera como los casos críticos; comparar municipios pares con el módulo transversal del dashboard.
4. **Institucionalizar el semáforo de brecha (NORMAL ≤ 10 pp < ALERTA ≤ 30 pp < CRITICO)** como regla de monitoreo continuo: es simple, explicable y el PCA confirma que separa grupos reales.
5. **Mantener la validación automática de integridad referencial como parte del pipeline:** fue la que detectó el bug de `SK_Tiempo` (ya corregido) antes de la defensa; toda regeneración futura del esquema estrella debería pasar por esas mismas verificaciones.

## Glosario de términos técnicos

| Término | Definición |
|---|---|
| **BRECHA** | `AVANCE_EJECUCION − AVANCE_FISICO`, en puntos porcentuales (pp). Métrica central del proyecto. |
| **AVANCE_FISICO** | Porcentaje de avance físico de la obra reportado en el Formato 12-B. |
| **AVANCE_EJECUCION** | Porcentaje de ejecución financiera acumulada del proyecto. |
| **DEVENGADO** | Gasto reconocido oficialmente (obligación de pago registrada), base de la ejecución financiera. |
| **SEMAFORO_BRECHA** | Segmentación de BRECHA: NORMAL (≤ 10 pp), ALERTA (10–30 pp), CRITICO (> 30 pp), SIN DATO (nulos). |
| **DIAS_SIN_REPORTE** | Días transcurridos desde la última fecha de declaración estimada; mide vigencia del reporte. |
| **Arquitectura Medallion** | Patrón de capas Bronze (crudo) → Silver (limpio) → Gold (métricas de negocio). |
| **Esquema estrella** | Modelo con una tabla de hechos central (`fact_inversiones`) unida a dimensiones por llaves sustitutas. |
| **Llave sustituta (SK)** | Identificador numérico autogenerado que reemplaza llaves naturales de texto en los joins. |
| **PCA** | Análisis de Componentes Principales: reduce las 6 métricas a 2 ejes (PC1, PC2) que conservan la mayor varianza posible. |
| **Carga (loading)** | Peso de cada variable original en un componente principal; indica qué variables definen el eje. |
| **Imputación por mediana** | Reemplazo de nulos con la mediana de la variable, robusta a valores extremos. |
| **Estandarización z-score** | Transformación a media 0 y desviación 1; evita que variables de mayor escala dominen el PCA. |
| **Devengado acumulado / Costo actualizado** | Base del `PCT_EJECUCION_PRESUPUESTAL`: cuánto del costo total ya se gastó. |
