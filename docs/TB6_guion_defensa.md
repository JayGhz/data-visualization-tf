# E6 — Guion de Defensa (10 minutos)

**Proyecto:** Brecha de eficiencia en la inversión pública peruana (MEF 2020–2026)
**Curso:** Data Visualization CC0211 · UPC

---

## Guion por secciones

### 1. Apertura: problema y pregunta (0:00 – 1:00)

> "En el Perú, que un proyecto haya gastado el 80 % de su presupuesto no significa que la obra esté al 80 %. Nuestra pregunta es: **¿en qué medida la ejecución financiera refleja el avance real de las obras, y dónde están los cuellos de botella?** Trabajamos con la cartera completa del Banco de Inversiones del MEF: 291,453 proyectos, tres fuentes públicas cruzadas por código único."

- Mencionar usuario objetivo: analistas de control (Contraloría), autoridades subnacionales, periodismo de datos.
- Una decisión que se apoya en el producto: **a qué proyectos mandar fiscalización primero**.

### 2. Pipeline y decisiones de datos (1:00 – 3:00)

> "Todo el producto sale de un pipeline reproducible en Python con arquitectura Medallion: Bronze conserva el dato crudo del MEF, Silver limpia y consolida las tres fuentes, Gold deriva las métricas de negocio, y de ahí exportamos un esquema estrella para Tableau más el módulo PCA."

Puntos a tocar (30 segundos cada uno):

- **Métrica central:** BRECHA = ejecución financiera − avance físico, en puntos porcentuales. Positiva ⇒ se gasta más de lo que se construye.
- **Reglas de negocio explícitas:** cerrados sin reporte físico se asumen 100 %; avances > 100 % se capan (error de digitación). No se imputa BRECHA: si falta un avance, el proyecto queda `SIN DATO` — preferimos mostrar el vacío de información a inventarlo.
- **Esquema estrella:** 1 fila por proyecto en la fact, 5 dimensiones con llaves sustitutas; elegido sobre tabla plana por rendimiento en Tableau y filtros independientes por dimensión.

### 3. Hallazgos con el dashboard (3:00 – 5:30)

Recorrer el dashboard en este orden (un insight por vista):

1. **KPIs de contexto:** brecha media −12.2 pp y mediana 0 ⇒ el problema agregado no es sobregasto, es **desfase y calidad de registro**.
2. **Vista de opacidad:** 64 % de la cartera sin brecha calculable; 75 mil proyectos con más de 90 días sin reporte, 46 mil de ellos activos. "El principal cuello de botella no es lo que vemos, es lo que no se reporta."
3. **Vista transversal (sector/territorio):** los 20 proyectos CRITICO promedian 7 % de obra con 25 % del presupuesto gastado; 18 de 20 son de Gobiernos Locales.
4. **Vista longitudinal:** evolución de registro y ejecución 2020–2026 sobre fechas nativas.

### 4. Componente avanzado: PCA (5:30 – 8:00)

> "Para el componente avanzado aplicamos PCA con scikit-learn sobre las 6 métricas numéricas del proyecto. La pregunta que le hicimos al PCA fue: **¿la desalineación financiero-física es un eje real de los datos, o un artefacto de nuestras reglas de semáforo?**"

- **Preparación:** imputación por mediana (robusta a la asimetría de costo y días) y estandarización z-score (pp, días y soles no son comparables sin escalar).
- **Resultado:** PC1 = 25.0 % de varianza, PC2 = 19.9 %, 44.9 % acumulado.
- **PC1** carga en AVANCE_EJECUCION (+0.69) y DIAS_SIN_REPORTE (+0.61): eje de madurez financiera y antigüedad del reporte.
- **PC2** contrapone BRECHA (+0.70) contra AVANCE_FISICO (−0.65): **es exactamente nuestra pregunta analítica, encontrada por el algoritmo sin conocer el semáforo.** Los CRITICO/ALERTA se separan en la zona alta del plano.
- **Hallazgo colateral:** COSTO_ACTUALIZADO casi no pesa (< 0.05): el riesgo no depende de la envergadura del proyecto.
- **Traducción operativa:** el cuadrante PC1-alto + PC2-alto es la lista corta de fiscalización; `pca_proyectos.csv` alimenta ese scatter en Tableau.

### 5. QA, limitaciones y cierre (8:00 – 10:00)

> "En el QA final encontramos un bug real: las llaves de tiempo del esquema estrella se corrompían por un overflow de Int8 en polars — `mes×100` desborda antes del cast a Int64, así que solo las fechas de enero generaban SK correctos y el 35.6 % de los SK de `dim_tiempo` estaban duplicados. Lo detectó nuestra celda de validación de integridad referencial, lo diagnosticamos hasta la causa raíz, lo corregimos y regeneramos el esquema estrella completo: la validación final muestra 0 duplicados y joins sin inflación."

- Limitaciones honestas: BRECHA calculable solo en 35.6 % de la cartera; datos declarativos (no auditados); PCA explica 44.9 % — es una herramienta de priorización, no un modelo causal.
- Cierre con la recomendación: **primero destrabar el reporte (46 mil activos en silencio), luego fiscalizar el cuadrante crítico del PCA, con foco en Gobiernos Locales.**
- Última frase: "El dashboard no solo muestra dónde está la brecha: muestra dónde ni siquiera podemos medirla — y eso también es un hallazgo."

---

## Posibles preguntas del profesor (con respuestas preparadas)

**P1. ¿Por qué imputaron con la mediana en el PCA si dijeron que no imputan BRECHA?**
> Son dos capas distintas con contratos distintos. En la capa de negocio (fact/semáforos) no imputamos: un `SIN DATO` es información para el usuario de control. El PCA, en cambio, exige una matriz completa; la mediana es robusta a la fuerte asimetría de costo y días, y documentamos su efecto: compacta el centro del plano. Los grupos que nos interesan (CRITICO/ALERTA) se separan igual.

**P2. PC1+PC2 solo explican 44.9 % de la varianza. ¿No es poco?**
> Para clustering predictivo sería poco; para nuestro objetivo — proyectar la cartera en un scatter interpretable que priorice fiscalización — es suficiente, porque los dos ejes que emergen son directamente accionables y coinciden con la pregunta analítica. Con 6 variables poco correlacionadas entre sí, dos componentes con 45 % es una estructura real, no ruido.

**P3. ¿Por qué PCA y no t-SNE?**
> t-SNE preserva vecindades locales pero sus ejes no son interpretables ni estables, y con 291 mil puntos es costoso y no admite proyectar datos nuevos de forma natural. El valor de nuestro componente avanzado está en las **cargas**: poder decir "PC2 *es* la desalineación financiero-física". PCA es lineal, reproducible (random_state fijo) y sus ejes se explican al usuario de control.

**P4. ¿Estandarizaron antes del PCA? ¿Qué pasa si no?**
> Sí, z-score con StandardScaler. Sin escalar, COSTO_ACTUALIZADO (varianza en soles, hasta miles de millones) absorbería PC1 por completo y el PCA describiría solo la escala presupuestal. Escalando, cada variable entra con varianza 1 y los componentes reflejan estructura, no unidades.

**P5. La brecha media es negativa. ¿No contradice la hipótesis de ineficiencia?**
> La refina. Esperábamos sobregasto generalizado y encontramos que el desfase dominante es administrativo: el registro financiero corre detrás de la obra. La ineficiencia grave existe pero está concentrada — 20 críticos, 256 en alerta — y eso convierte el problema en uno de **focalización**, que es exactamente lo que el dashboard resuelve.

**P6. ¿Cómo garantizan que la fact no duplica proyectos?**
> Granularidad declarada de 1 fila por `CODIGO_UNICO`, deduplicación explícita al construir la fact, y una celda de validación en el notebook final que verifica unicidad de SK_Proyecto (0 duplicados) e integridad referencial contra las 5 dimensiones (0 llaves huérfanas en ubicación, institución y estructura).

**P7. Encontraron un bug en sus propias llaves de tiempo. ¿Cómo lo manejaron?**
> Lo detectó nuestra propia validación automática de integridad referencial, antes de la defensa. Diagnosticamos la causa raíz (overflow de Int8 en polars: `mes×100` supera 127 antes del cast a Int64), cuantificamos el impacto (35.6 % de SK duplicados, joins inflados de 291 mil a 514 mil filas), corregimos la fórmula casteando cada componente antes de multiplicar, extendimos el calendario a 2040 —había proyectos con fin planificado en 2036— y regeneramos el esquema estrella. La validación posterior muestra 0 duplicados y 0 llaves fuera de calendario. Documentamos todo el ciclo en el notebook porque el QA es parte del entregable: es la diferencia entre un pipeline auditado y uno que solo parece limpio.

**P8. ¿Por qué asumir 100 % de avance físico en proyectos cerrados sin reporte?**
> Regla de negocio conservadora respecto de nuestra métrica: un proyecto con cierre formal aprobado se considera concluido por el propio proceso administrativo del MEF. La alternativa (dejarlo nulo) inflaría artificialmente el grupo SIN DATO con proyectos que sí terminaron. El flag `FLAG_SIN_AVANCE_FISICO` conserva la trazabilidad de qué valores fueron asumidos.

**P9. ¿El dataset cumple los requisitos del curso?**
> Sí, con holgura: 291,453 registros (mínimo 2,000), 26 columnas en la fact más dimensiones, dimensión temporal (5 fechas), categóricas fuertes (sector, lifecycle, semáforos), geografía (ubigeo, departamento, lat/long) y más de 8 variables numéricas para el componente avanzado.

**P10. ¿Qué harían distinto con más tiempo?**
> Tres cosas: corregir y regenerar `dim_tiempo`; reconstruir series mensuales de devengado por proyecto para pasar de fotografía a trayectoria; y validar el avance físico declarado contra una muestra auditada de la Contraloría para estimar el sesgo de auto-reporte.

---

## Decisiones clave que el equipo debe poder defender

| # | Decisión | Defensa en una línea |
|---|---|---|
| 1 | Arquitectura Medallion (Bronze/Silver/Gold) | Trazabilidad: siempre se puede volver al dato crudo del MEF y reproducir cada transformación. |
| 2 | BRECHA como métrica central | Operacionaliza la pregunta analítica en una sola cifra interpretable en pp, con umbrales de semáforo explicables. |
| 3 | No imputar BRECHA; sí clasificar `SIN DATO` | El vacío de reporte es un hallazgo de fiscalización, no un hueco a rellenar. |
| 4 | Asumir 100 % físico en cerrados sin reporte + cap a 100 | Reglas conservadoras y trazables vía flags; evitan inflar SIN DATO y arrastrar errores de digitación. |
| 5 | Esquema estrella con llaves sustitutas | Menos redundancia, joins eficientes y filtros independientes por dimensión en Tableau. |
| 6 | Granularidad: 1 fila por proyecto (fotografía) | Coherente con la fuente (acumulados a fecha de corte); la evolución se trabaja con fechas nativas. |
| 7 | PCA sobre 6 métricas, no t-SNE | Ejes interpretables (cargas), reproducible y escalable a 291 mil filas. |
| 8 | Mediana + z-score antes del PCA | Robustez a asimetría extrema y comparabilidad de unidades (pp, días, soles). |
| 9 | 2 componentes | El objetivo es un scatter accionable en Tableau, no maximizar varianza retenida. |
| 10 | Reportar el bug de SK_Tiempo como hallazgo de QA | Detección propia por validación automática, causa raíz diagnosticada, impacto cuantificado y corrección verificada. |
