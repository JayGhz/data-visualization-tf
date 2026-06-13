# Reglas de Métricas, Segmentos y Parámetros
**Proyecto:** Brecha de Eficiencia en Inversión Pública Peruana (MEF 2020–2026)  
**Curso:** Data Visualization CC0211 · NRC 18519 · UPC  
**Equipo:** Cuadros (u20221c488) · Jeri (u202219322) · Quispe (u20211c699)  
**Entrega:** 4 — Segmentación, cálculos analíticos y fuentes para Tableau

---

## 1. Métricas Derivadas

Las métricas se calculan en dos etapas del pipeline:

- **`scripts/04_gold.py`** → métricas de negocio base
- **`scripts/06_star_schema.py`** → métricas de segmentación para Tableau

Todas son **consistentes con la pregunta analítica**:  
> *¿En qué medida la ejecución financiera refleja el avance real de las obras?*

---

### 1.1 BRECHA *(métrica central)*

| Campo | Detalle |
|---|---|
| **Fórmula** | `AVANCE_EJECUCION − AVANCE_FISICO` |
| **Unidad** | Puntos porcentuales (pp) |
| **Ubicación** | `fact_inversiones` · calculada en `04_gold.py` |

**Interpretación:**
- `BRECHA > 0` → se gastó más de lo que avanzó la obra físicamente → posible alerta
- `BRECHA < 0` → la obra avanzó más rápido que el gasto registrado → desfase de registro
- `BRECHA ≈ 0` → alineación entre ejecución financiera y avance físico

**Regla de calidad:** Si `AVANCE_EJECUCION` o `AVANCE_FISICO` es nulo, BRECHA queda nula y se clasifica como `SIN DATO` en el semáforo.

---

### 1.2 PCT_EJECUCION_PRESUPUESTAL

| Campo | Detalle |
|---|---|
| **Fórmula** | `DEVENGADO_ACUMULADO / COSTO_ACTUALIZADO × 100` |
| **Unidad** | Porcentaje (%) |
| **Ubicación** | `fact_inversiones` · calculada en `06_star_schema.py` |

**Propósito:** Complementa BRECHA. Permite detectar proyectos que consumen presupuesto sin avanzar físicamente (`PCT alto + AVANCE_FISICO bajo = alerta`).

---

### 1.3 DIAS_SIN_REPORTE

| Campo | Detalle |
|---|---|
| **Fórmula** | `FECHA_HOY − ULT_FEC_DECLA_ESTIM` |
| **Unidad** | Días |
| **Ubicación** | `fact_inversiones` · calculada en `04_gold.py` |

**Propósito:** Proxy de parálisis operativa. El 77% de proyectos activos supera los 30 días sin reporte.

---

### 1.4 DIAS_ARRANQUE

| Campo | Detalle |
|---|---|
| **Fórmula** | `FEC_INI_EJECUCION − FECHA_REGISTRO` |
| **Unidad** | Días |
| **Ubicación** | `fact_inversiones` · calculada en `04_gold.py` |

**Propósito:** Mide la demora burocrática entre el registro del proyecto y el inicio de la ejecución. Permite identificar cuellos de botella administrativos previos a la obra.

---

### 1.5 DIAS_PLANIFICADOS

| Campo | Detalle |
|---|---|
| **Fórmula** | `FEC_FIN_EJECUCION − FEC_INI_EJECUCION` |
| **Unidad** | Días |
| **Ubicación** | `fact_inversiones` · calculada en `04_gold.py` |

**Propósito:** Duración prevista de la obra. Permite comparar con la duración real y detectar cronogramas inflados o proyectos que superaron su plazo.

---

### 1.6 Flags de calidad

| Variable | Fórmula | Propósito |
|---|---|---|
| `FLAG_SIN_AVANCE_FISICO` | `1` si `AVANCE_FISICO` es nulo | Identifica proyectos que no reportan avance físico |
| `FLAG_FECHAS_INCONSISTENTES` | `1` si `FEC_FIN_EJECUCION ≤ FEC_INI_EJECUCION` | Detecta errores de captura en el sistema de origen |

---

## 2. Segmentos

Se definen **6 segmentos** usados como filtros y dimensiones de color en el dashboard de Tableau.

---

### 2.1 LIFECYCLE *(ciclo de vida del proyecto)*

| Valor | Origen | Cantidad |
|---|---|---|
| `ACTIVE` | Dataset Detalle de inversiones | 183,692 (63.0%) |
| `CLOSED` | Dataset Cierre de inversiones | 107,761 (37.0%) |

**Uso en Tableau:** Filtro primario para separar el análisis de proyectos en curso del análisis histórico.

**Regla:** Se asigna en la capa Silver mediante concatenación diagonal de los dos datasets fuente.

---

### 2.2 SEMAFORO_BRECHA *(alerta de desalineación)*

| Valor | Condición | Cantidad |
|---|---|---|
| `NORMAL` | `BRECHA ≤ 10 pp` | 103,509 |
| `ALERTA` | `10 pp < BRECHA ≤ 30 pp` | 256 |
| `CRITICO` | `BRECHA > 30 pp` | 20 |
| `SIN DATO` | `BRECHA` es nula | 187,668 |

**Uso en Tableau:** Filtro y color principal del dashboard para detectar proyectos de alto riesgo.

---

### 2.3 SEMAFORO_REPORTE *(vigencia del reporte de avance)*

| Valor | Condición | Interpretación |
|---|---|---|
| `AL DIA` | `DIAS_SIN_REPORTE ≤ 30` | Reporte vigente |
| `REZAGADO` | `30 < DIAS_SIN_REPORTE ≤ 90` | Atención requerida |
| `PARALIZADO` | `DIAS_SIN_REPORTE > 90` | Posible proyecto abandonado |
| `SIN DATO` | Fecha de reporte nula | Sin información disponible |

**Uso en Tableau:** Complementa SEMAFORO_BRECHA para generar alertas de seguimiento.

---

### 2.4 RANGO_COSTO *(tamaño del proyecto)*

| Valor | Condición | Cantidad |
|---|---|---|
| `PEQUENO` | `COSTO_ACTUALIZADO < S/ 500,000` | 122,939 (41.6%) |
| `MEDIANO` | `S/ 500k ≤ COSTO < S/ 5M` | 128,435 (43.6%) |
| `GRANDE` | `S/ 5M ≤ COSTO < S/ 50M` | 36,965 (12.6%) |
| `MEGAPROYECTO` | `COSTO_ACTUALIZADO ≥ S/ 50M` | 3,114 (1.1%) |

**Uso en Tableau:** Permite analizar si los proyectos de mayor envergadura presentan peor relación entre gasto y avance físico.

---

### 2.5 SECTOR *(segmento institucional)*

- Proveniente de `dim_institucion`
- 36 sectores distintos
- **Hallazgo clave:** Gobiernos Locales concentra 83,340 proyectos con brecha media de −10.76 pp

---

### 2.6 CATEGORIA_PROBLEMA *(tipo de obstáculo declarado)*

- Proveniente de `dim_proyecto`
- Obtenida mediante clasificación NLP híbrida: Regex + SentenceTransformer (umbral coseno 0.5)
- Convierte texto libre de `ULT_PROBLEMA` en categorías estructuradas

---

## 3. Parámetros y Lógica Analítica

### 3.1 Justificación de umbrales

#### ¿Por qué 10 pp para NORMAL?
El sistema MEF tiene un **desfase natural de registro**: el gasto se registra antes de que se declare el avance físico. Ese proceso puede tardar días o semanas. 10 pp absorbe ese desfase sin generar falsas alarmas.

#### ¿Por qué 30 pp para CRITICO?
Una desalineación de 30 pp ya no puede explicarse por desfase de registro. A ese nivel, se gastó un 30% más de lo que avanzó la obra, lo que requiere revisión o auditoría.

#### ¿Por qué 30 días para REZAGADO?
Un mes sin reportar es el límite razonable de rezago administrativo en el sistema de seguimiento del MEF.

#### ¿Por qué 90 días para PARALIZADO?
Tres meses sin declarar avance físico indica que el proyecto está desatendido o paralizado operativamente.

---

### 3.2 Reglas de negocio aplicadas

| Regla | Condición | Acción | Motivo |
|---|---|---|---|
| Imputación AVANCE_FISICO | `LIFECYCLE = 'CLOSED'` y `AVANCE_FISICO` es nulo | Asignar `100.0` | Si el proyecto cerró administrativamente, se asume culminado |
| Cap de avance | `AVANCE_FISICO > 100` o `AVANCE_EJECUCION > 100` | Truncar a `100.0` | Errores de captura en el sistema fuente generan valores imposibles |
| AVANCE_FISICO preferido | `TIENE_AVAN_FISICO = 'NO'` y valor nulo | Asignar `0.0` | El sistema indica explícitamente que no hay avance |
| Coalesce F12B | `AVANCE_FISICO` nulo en Detalle | Usar valor de F12B | F12B tiene mejor cobertura (9.5% nulos vs 46.5% en Detalle) |

---

### 3.3 Evolución del modelo

La arquitectura inicial propuesta en TB2 (Sección 7.5) contemplaba múltiples tablas de hechos (`fact_financiera`, `fact_situacional`, `fact_componentes`). Durante la implementación se identificaron tres problemas:

1. `fact_situacional` y `fact_componentes` tienen granularidad N:M que Tableau no gestiona bien
2. Los joins múltiples degradan el rendimiento del dashboard
3. La pregunta analítica solo requiere una fila por proyecto

**Decisión:** Se simplificó a un esquema estrella con una única tabla de hechos (`fact_inversiones`) que concentra todas las medidas y semáforos. Esta decisión está documentada y justificada en la Sección 8.1 del informe.

---

## 4. Validación del Esquema

Ejecutada automáticamente por `06_star_schema.py` antes de exportar:

| Verificación | Resultado |
|---|---|
| Duplicados en `SK_Proyecto` (PK) | **0** ✓ |
| Nulos en `SK_Ubicacion` | **0** ✓ |
| Nulos en `SK_Institucion` | **0** ✓ |
| Nulos en `SK_Estructura` | **0** ✓ |
| Métricas duplicadas en dimensiones | **0** ✓ |

---

## 5. Fuentes Exportadas para Tableau

| Archivo | Filas | Cols | Contenido |
|---|---|---|---|
| `fact_inversiones.csv` | 291,453 | 26 | Medidas, semáforos, llaves sustitutas |
| `dim_proyecto.csv` | 291,453 | 13 | Estado, lifecycle, formularios, NLP |
| `dim_ubicacion.csv` | 2,108 | 7 | Departamento, provincia, distrito, coordenadas |
| `dim_institucion.csv` | 2,127 | 4 | Sector, entidad, nivel |
| `dim_estructura.csv` | 34 | 4 | Función, tipo inversión, marco normativo |
| `dim_tiempo.csv` | 13,149 | 6 | Calendario 2000–2035 |

**Condición de entrega:** Todos los archivos se conectan directamente a Tableau Desktop sin reprocesamiento manual. El esquema fue validado con 0 duplicados y 0 nulos en llaves foráneas.

---

*Generado para Entrega 4 — Data Visualization CC0211 · UPC · Junio 2026*