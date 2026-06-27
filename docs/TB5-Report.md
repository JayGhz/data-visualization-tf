# Entrega 5 — Dashboard Alpha y Visualización Exploratoria
**Proyecto:** Brecha de Eficiencia en Inversión Pública Peruana (MEF 2020–2026)  
**Curso:** Data Visualization · UPC  

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

### Insight 4 — El volumen de inversión activa creció 4 veces desde 2018 sin cierre proporcional

La vista temporal muestra que los proyectos ACTIVE registrados por año pasaron de aproximadamente 6,000 en 2018 a más de 23,000 en 2024, un crecimiento de casi 4 veces en seis años. Este incremento no estuvo acompañado de un aumento proporcional en los proyectos CLOSED, lo que genera una acumulación de obras en ejecución sin cierre. La línea de referencia en 6,000 proyectos (nivel promedio pre-2018) permite visualizar la magnitud del desbalance estructural. Si la capacidad de seguimiento del sistema no escala al mismo ritmo, el riesgo de paralización aumenta estructuralmente.

---

### Insight 5 — Los megaproyectos no son los más problemáticos

Contrario a la hipótesis inicial, el análisis por RANGO_COSTO muestra que los MEGAPROYECTOS (≥ S/ 50M) representan solo el 1.1% del universo (3,114 proyectos) y no concentran la mayor brecha promedio. El mayor volumen de proyectos con brecha negativa corresponde al segmento MEDIANO (S/ 500k–5M), que representa el 43.6% del universo. Esto sugiere que el problema de desalineación no es exclusivo de obras grandes sino que está distribuido en el grueso de la cartera de inversión pública.

---

## 2. Tabla de Selección y Descarte de Gráficos

### Gráficos seleccionados

| Vista | Tipo de gráfico | Ubicación | Justificación técnica |
|---|---|---|---|
| Brecha por Sector | Barras horizontales | Dashboard alpha | Permite comparar valores negativos y positivos simultáneamente. El eje horizontal facilita leer etiquetas largas de sectores. El color por SEMAFORO_BRECHA (gris=normal, ámbar=alerta, rojo=crítico) añade una dimensión de alerta sin saturar la vista. |
| Semáforo Brecha | Tabla con formato semántico | Dashboard alpha | Las 4 categorías tienen magnitudes tan dispares (CRITICO=20 vs NORMAL=103,509) que una barra haría invisible lo más urgente. La tabla con iconos (❌⚠️✅) y colores semánticos permite leer excepciones críticas de forma inmediata, siguiendo el principio del profe: "pocos casos críticos con formato semántico, no tabla gigante". |
| Mapa de Proyectos Críticos | Mapa de puntos con color semántico | Dashboard alpha | La dimensión geográfica es parte de la pregunta analítica ("¿qué regiones presentan mayores cuellos de botella?"). El color por SEMAFORO_BRECHA permite identificar dónde se concentran los proyectos en alerta, patrón que un gráfico de barras no revelaría. |
| Relación Avance Físico vs Ejecución | Scatter plot | Hoja separada | Es el único tipo de gráfico que muestra simultáneamente dos variables continuas a nivel de registro individual. La diagonal implícita sirve como referencia de alineación perfecta. Su densidad (291k puntos) lo hace difícil de leer en el espacio reducido del dashboard. |
| Distribución por Rango de Costo | Barras verticales apiladas | Hoja separada | Combina dos dimensiones categóricas (rango y lifecycle) en una sola vista. El apilado muestra composición interna sin perder la comparación entre rangos. |
| Tendencia Temporal de Inversiones | Líneas + línea de referencia | Hoja separada | La evolución temporal requiere una variable continua en el eje X. Las dos líneas (ACTIVE vs CLOSED) en la misma escala permiten ver el desbalance sin eje dual. La línea de referencia en 6,000 proyectos (nivel pre-2018) contextualiza el boom de inversión activa post-2019. |

---

### Gráficos descartados

#### Descartado 1 — Pie chart para distribución de SEMAFORO_BRECHA

**Descripción:** Se evaluó usar un gráfico circular para mostrar la proporción de proyectos por categoría de semáforo (NORMAL, ALERTA, CRÍTICO, SIN DATO).

**Razón del descarte:**

1. **Dominancia visual engañosa:** SIN DATO representa el 64.8% del universo. Una torta con un segmento dominante de esa magnitud oculta visualmente las diferencias entre NORMAL (35.1%), ALERTA (0.09%) y CRÍTICO (0.007%), que son justamente los valores de interés analítico.
2. **Imposibilidad de detectar valores extremos:** Con 4 categorías de magnitudes tan dispares, el pie chart hace virtualmente invisible la categoría CRÍTICO, que es el hallazgo más relevante del proyecto.
3. **No permite comparación cuantitativa precisa:** El ojo humano no puede estimar ángulos con precisión. El profe indica explícitamente "evitar pie explotado — comparar ángulos es más difícil que comparar longitudes".

**Alternativa elegida:** Tabla con formato semántico (Semáforo Brecha), que permite leer el valor exacto de cada categoría y resalta visualmente las excepciones mediante iconos y color.

---

#### Descartado 2 — Treemap para distribución de sectores

**Descripción:** Se evaluó usar un treemap para mostrar el volumen de proyectos por sector, donde el tamaño del rectángulo representaría el número de proyectos y el color la brecha media.

**Razón del descarte:**

1. **Codificación de área imprecisa:** El tamaño de los rectángulos codifica el número de proyectos, pero la pregunta analítica se centra en la BRECHA, no en el volumen. Un sector con muchos proyectos pero brecha baja quedaría visualmente prominente sin ser analíticamente relevante.
2. **Etiquetas ilegibles en valores pequeños:** El universo tiene 36 sectores. Los sectores con pocos proyectos generarían rectángulos tan pequeños que sus etiquetas serían ilegibles.
3. **No representa valores negativos:** La brecha puede ser negativa. Un treemap de área no puede representar valores negativos de forma intuitiva.

**Alternativa elegida:** Barras horizontales (Brecha por Sector), que representa directamente el valor de brecha en un eje continuo con valores negativos y positivos en la misma escala.

---

#### Descartado 3 — Heatmap de brecha por sector y departamento

**Descripción:** Se evaluó construir un heatmap cruzando SECTOR (filas) con DEPARTAMENTO (columnas) y coloreando por brecha media.

**Razón del descarte:**

1. **Dimensionalidad excesiva:** 36 sectores × 25 departamentos = 900 celdas. La mayoría estarían vacías porque no todos los sectores tienen proyectos en todos los departamentos, generando un heatmap disperso y difícil de leer.
2. **Redundancia con vistas existentes:** El mapa departamental y el gráfico de sector responden las mismas preguntas por separado con mayor claridad. Combinarlos en una matriz agrega complejidad sin añadir insight incremental.

**Alternativa elegida:** Mapa geográfico (dimensión espacial) + barras por sector (dimensión institucional) como vistas independientes conectadas por filtros cruzados en el dashboard.

---

## 3. Estructura del Dashboard Alpha

### Vistas dentro del dashboard
```
┌─────────────────────────────────────────────────────────────┐
│ HEADER: "276 proyectos gastan más de lo que avanzan;        │
│ Gobiernos Locales lidera el riesgo"                         │
│ Periodo: 2020-2026 | Filtro: Lifecycle | Fuente: MEF        │
├──────────────────────────┬──────────────┬───────────────────┤
│                          │ Semáforo     │                   │
│  Brecha por Sector       │ Brecha       │  PANEL DE         │
│  (vista principal)       │ (tabla)      │  INSIGHTS         │
│                          ├──────────────┤  1. QUÉ           │
│                          │ Mapa         │  2. POR QUÉ       │
│                          │ Proyectos    │  3. ACCIÓN        │
│                          │ Críticos     │                   │
├──────────────────────────┴──────────────┴───────────────────┤
│ Footer: Fuente MEF · Nota: 64.8% sin dato de avance físico  │
└─────────────────────────────────────────────────────────────┘
```

### Hojas separadas (exploratorias)
- Scatter: Relación Avance Físico vs Ejecución
- Distribución por Rango de Costo
- Tendencia Temporal: Stock activo creció 4x desde 2018

### Filtros activos
- **LIFECYCLE** (ACTIVE / CLOSED) — global a todas las vistas
- **Use as Filter** activado en Brecha por Sector → filtra el mapa

### Principios de diseño aplicados
- Paleta de 3 colores semánticos: gris=normal · ámbar=alerta · rojo=crítico
- Atributos preatentivos: color y posición guían la mirada al dato crítico
- Título del dashboard = lectura del gráfico, no nombre descriptivo
- Panel de insights con estructura Hallazgo + Comparación + Evidencia + Acción
- Tabla de excepciones para semáforo (no barra) — CRITICO visible aunque sea el 0.007%
- Footer con fuente y advertencia de calidad del dato

---

*Entrega 5 — Data Visualization  · UPC · Junio 2026*