# Entrega 5 — Dashboard Alpha y Visualización Exploratoria
**Proyecto:** Brecha de Eficiencia en Inversión Pública Peruana (MEF 2020–2026)  
**Curso:** Data Visualization CC0211 · NRC 18519 · UPC  
**Equipo:** Cuadros (u20221c488) · Jeri (u202219322) · Quispe (u20211c699)

---

## 1. Insights Exploratorios

### Insight 1 — La mayoría de proyectos no reporta avance físico

El 64.8% de los proyectos del universo (187,668 de 291,453) no tiene dato de BRECHA porque nunca declaró avance físico en el sistema MEF. Este porcentaje no refleja proyectos sin ejecución, sino proyectos que gastan pero no reportan. La ausencia masiva de dato constituye en sí misma un hallazgo de gestión: el sistema de seguimiento físico presenta una cobertura crítica que impide la fiscalización efectiva del avance de obra.

---

### Insight 2 — Gobiernos Locales concentra el riesgo sistémico

Gobiernos Locales concentra 83,340 proyectos (28.6% del universo) con una brecha media de −10.76 puntos porcentuales. El valor negativo indica que el avance físico declarado supera al avance de ejecución financiera registrado, lo que puede explicarse por rezago en el ingreso de devengados al SIAF o por sobreestimación del avance físico reportado. En cualquier caso, el volumen de proyectos hace de este sector el foco prioritario de cualquier política de monitoreo.

---

### Insight 3 — Los proyectos CRÍTICOS son escasos pero extremos

Solo 20 proyectos (0.007% del universo) califican como CRÍTICO según el semáforo de brecha (diferencia superior a 30 puntos porcentuales). Sin embargo, en el scatter de relación estos proyectos aparecen completamente desplazados de la diagonal de alineación: algunos registran avance de ejecución financiera cercano al 100% con avance físico inferior al 10%. Estos casos representan el perfil de mayor riesgo de irregularidad y deberían ser el punto de entrada de cualquier auditoría focalizada.

---

### Insight 4 — El volumen de inversión activa se duplicó entre 2018 y 2024

La vista temporal muestra que los proyectos ACTIVE registrados por año pasaron de aproximadamente 6,000 en 2018 a más de 23,000 en 2024, un crecimiento de casi 4 veces en seis años. Este incremento no estuvo acompañado de un aumento proporcional en los proyectos CLOSED, lo que genera una acumulación de obras en ejecución sin cierre. Si la capacidad de seguimiento del sistema no escala al mismo ritmo, el riesgo de paralización aumenta estructuralmente.

---

### Insight 5 — Los megaproyectos no son los más problemáticos

Contrario a la hipótesis inicial, el análisis por RANGO_COSTO muestra que los MEGAPROYECTOS (≥ S/ 50M) representan solo el 1.1% del universo (3,114 proyectos) y no concentran la mayor brecha promedio. El mayor volumen de proyectos con brecha negativa corresponde al segmento MEDIANO (S/ 500k–5M), que representa el 43.6% del universo. Esto sugiere que el problema de desalineación no es exclusivo de obras grandes sino que está distribuido en el grueso de la cartera de inversión pública.

---

## 2. Tabla de Selección y Descarte de Gráficos

### Gráficos seleccionados

| Vista | Tipo de gráfico | Justificación técnica |
|---|---|---|
| Brecha por Sector | Barras horizontales | Permite comparar valores negativos y positivos simultáneamente. El eje horizontal facilita leer etiquetas largas de sectores. El color por SEMAFORO_BRECHA añade una dimensión de alerta sin saturar la vista. |
| Semáforo Brecha | Barras verticales | Distribución de una variable categórica ordinal. La escala discreta (4 valores) hace innecesario un histograma. La verticalidad permite comparar alturas de forma intuitiva. |
| Distribución por Rango de Costo | Barras verticales apiladas | Combina dos dimensiones categóricas (rango y lifecycle) en una sola vista. El apilado muestra composición interna sin perder la comparación entre rangos. |
| Relación Avance Físico vs Ejecución | Scatter plot | Es el único tipo de gráfico que muestra simultáneamente dos variables continuas a nivel de registro individual. La diagonal implícita sirve como referencia de alineación perfecta sin necesidad de anotación adicional. |
| Mapa Brecha Departamental | Mapa de puntos | La dimensión geográfica es parte de la pregunta analítica ("¿qué regiones presentan mayores cuellos de botella?"). El mapa permite identificar patrones espaciales que un gráfico de barras no revelaría. |
| Tendencia Temporal de Inversiones | Líneas | La evolución temporal requiere una variable continua en el eje X. Las líneas son superiores a las barras para mostrar tendencia y permiten comparar dos series (ACTIVE vs CLOSED) sin solapamiento visual. |

---

### Gráficos descartados

#### Descartado 1 — Pie chart / Gráfico de torta para distribución de SEMAFORO_BRECHA

**Descripción:** Se evaluó usar un gráfico circular para mostrar la proporción de proyectos por categoría de semáforo (NORMAL, ALERTA, CRÍTICO, SIN DATO).

**Razón del descarte:**
El pie chart presenta tres limitaciones críticas para este caso:

1. **Dominancia visual engañosa:** SIN DATO representa el 64.8% del universo. Una torta con un segmento dominante de esa magnitud oculta visualmente las diferencias entre NORMAL (35.1%), ALERTA (0.09%) y CRÍTICO (0.007%), que son justamente los valores de interés analítico.
2. **Imposibilidad de detectar valores extremos:** Con 4 categorías de magnitudes tan dispares, el pie chart hace virtualmente invisible la categoría CRÍTICO, que es el hallazgo más relevante del proyecto.
3. **No permite comparación cuantitativa precisa:** El ojo humano no puede estimar ángulos con precisión. Las barras verticales permiten comparar alturas de forma inmediata.

**Alternativa elegida:** Barras verticales (Semáforo Brecha), que mantiene las proporciones legibles y permite ver la diferencia entre ALERTA y CRÍTICO incluso cuando ambos son minoritarios.

---

#### Descartado 2 — Treemap para distribución de sectores

**Descripción:** Se evaluó usar un treemap para mostrar el volumen de proyectos por sector, donde el tamaño del rectángulo representaría el número de proyectos y el color la brecha media.

**Razón del descarte:**
El treemap presenta dos problemas fundamentales para este análisis:

1. **Codificación de área imprecisa:** El tamaño de los rectángulos codifica el número de proyectos, pero la pregunta analítica se centra en la BRECHA, no en el volumen. Un sector con muchos proyectos pero brecha baja (como Salud) quedaría visualmente prominente sin ser analíticamente relevante, generando una interpretación errónea.
2. **Etiquetas ilegibles en valores pequeños:** El universo tiene 36 sectores. Los sectores con pocos proyectos (Universidades, Tribunal Constitucional) generarían rectángulos tan pequeños que sus etiquetas serían ilegibles, perdiendo información relevante.
3. **Dificulta la comparación de valores negativos:** La brecha puede ser negativa. Un treemap de área no puede representar valores negativos de forma intuitiva, lo que obligaría a añadir una escala de color divergente que compite visualmente con el tamaño.

**Alternativa elegida:** Barras horizontales (Brecha por Sector), que representa directamente el valor de brecha en un eje continuo, permite valores negativos y positivos en la misma escala, y mantiene las etiquetas legibles al estar en el eje vertical.

---

#### Descartado 3 — Heatmap de brecha por sector y departamento

**Descripción:** Se evaluó construir un heatmap cruzando SECTOR (filas) con DEPARTAMENTO (columnas) y coloreando por brecha media.

**Razón del descarte:**
1. **Dimensionalidad excesiva:** 36 sectores × 25 departamentos = 900 celdas. La mayoría estarían vacías porque no todos los sectores tienen proyectos en todos los departamentos, generando un heatmap disperso y difícil de leer.
2. **Cobertura de la pregunta ya resuelta por vistas separadas:** El mapa departamental y el gráfico de sector responden las mismas preguntas por separado con mayor claridad. Combinarlos en una matriz agrega complejidad sin añadir insight incremental.

**Alternativa elegida:** Mapa geográfico (dimensión espacial) + barras por sector (dimensión institucional) como vistas independientes que el dashboard conecta mediante filtros cruzados.

---

## 3. Flujo de Lectura del Dashboard Alpha

El dashboard está diseñado con el siguiente flujo de lectura para el usuario objetivo (analista de gestión pública):

```
1. SEMÁFORO BRECHA        → ¿Cuántos proyectos tienen alerta?
2. DISTRIBUCIÓN POR COSTO → ¿De qué tamaño son los proyectos?
3. BRECHA POR SECTOR      → ¿Qué sectores tienen mayor desalineación?
4. MAPA DEPARTAMENTAL     → ¿Dónde están los proyectos con brecha?
5. SCATTER RELACIÓN       → ¿Qué tan alineados están gasto y avance?
6. TENDENCIA TEMPORAL     → ¿Cómo evolucionó el stock de inversiones?
```

Los filtros de **LIFECYCLE** y **SEMAFORO_BRECHA** son globales: al seleccionar una categoría en cualquier vista, todas las demás se actualizan, permitiendo análisis cruzados interactivos.

---

*Entrega 5 — Data Visualization CC0211 · UPC · Junio 2026*