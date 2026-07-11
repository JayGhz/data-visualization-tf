# QA Técnico — Entrega 6
**Proyecto:** Brecha de Eficiencia en Inversión Pública Peruana (MEF 2020–2026)  
**Curso:** Data Visualization CC0211 · NRC 18519 · UPC  
**Equipo:** Cuadros (u20221c488) · Jeri (u202219322) · Quispe (u20211c699)

---

## 1. Resumen Ejecutivo del QA

| Verificación | Resultado | Estado |
|---|---|---|
| Esquema estrella — duplicados en PK | 0 duplicados | ✅ |
| Esquema estrella — nulos en FKs | 0 nulos | ✅ |
| Join fact → dim_tiempo (inflación de filas) | 291,453 → 291,453 | ✅ |
| Bug SK_Tiempo (overflow Int8) | Detectado y corregido | ✅ |
| dim_tiempo — duplicados en SK | 0 (antes: 4,680) | ✅ |
| PCA — varianza explicada PC1+PC2 | 44.85% | ✅ |
| PCA — nulos imputados antes del PCA | Mediana por columna | ✅ |
| Integridad referencial (0 huérfanos) | Verificada | ✅ |
| Dashboard — responde pregunta sin ayuda | Sí | ✅ |
| Vista longitudinal defendible | Tendencia temporal con línea referencia | ✅ |
| Vista transversal defendible | Brecha por sector (36 sectores) | ✅ |

---

## 2. QA del Pipeline (Bronze → Silver → Gold → Star Schema)

### 2.1 Bronze
| Check | Resultado |
|---|---|
| Registros cargados (Detalle) | 260,422 |
| Registros cargados (F12B) | 213,214 |
| Registros cargados (Cierre) | 108,841 |
| Tipo de dato AVANCE_FISICO en Bronze | String (problema detectado → corregido en Silver) |

### 2.2 Silver
| Check | Resultado |
|---|---|
| Filas sin CODIGO_UNICO eliminadas (Detalle) | 67 |
| Filas sin CODIGO_UNICO eliminadas (Cierre) | 3,447 |
| Universo maestro post-merge | 294,966 filas |
| LIFECYCLE = ACTIVE | 183,692 |
| LIFECYCLE = CLOSED | 107,761 (107,761 + 3,515 duplicados eliminados) |
| Conversión AVANCE_FISICO a Float64 | ✅ |
| NLP híbrido CATEGORIA_PROBLEMA | ✅ Regex + SentenceTransformer |

### 2.3 Gold
| Check | Resultado |
|---|---|
| Regla: CLOSED + AVANCE_FISICO nulo → 100.0 | ✅ Aplicada |
| Cap AVANCE_FISICO > 100 → 100.0 | ✅ Aplicada |
| BRECHA calculada | AVANCE_EJECUCION − AVANCE_FISICO |
| DIAS_SIN_REPORTE calculada | HOY − ULT_FEC_DECLA_ESTIM |
| FLAGS de calidad generados | FLAG_SIN_AVANCE_FISICO, FLAG_FECHAS_INCONSISTENTES |
| Filas en gold_master | 294,966 × 51 cols |

### 2.4 Star Schema (06_star_schema.py)

**Bug detectado y corregido durante QA:**

| Problema | `dt.month()` retorna `Int8` en Polars 1.40.1 → `mes × 100` desborda antes del cast a `Int64` |
|---|---|
| **Impacto** | 35.6% de SK_Tiempo duplicados — join fact → dim_tiempo inflaba de 291,453 a 514,634 filas |
| **Fix aplicado** | Cast a `Int64` en cada componente antes de multiplicar en `build_dim_tiempo()` y `fecha_a_sk()` |
| **Calendario extendido** | 2000–2040 (7 proyectos con fin planificado en 2036 estaban fuera del rango original) |

**Post-fix:**

| Check | Antes del fix | Después del fix |
|---|---|---|
| dim_tiempo filas | 13,149 | 14,976 |
| SK_Tiempo duplicados | 4,680 | **0** |
| Spot check 2020-12-31 | ❌ SK incorrecto | ✅ → 20201231 |
| Spot check 2020-08-10 | ❌ SK incorrecto | ✅ → 20200810 |
| Join fact → dim_tiempo | 514,634 filas (inflación) | **291,453 filas** |

**Validaciones del esquema final:**

```
fact_inversiones filas          : 291,453
fact_inversiones duplicados SK  : 0        ✅
SK_Ubicacion nulos              : 0        ✅
SK_Institucion nulos            : 0        ✅
SK_Estructura nulos             : 0        ✅
Cobertura dim_proyecto          : 100%     ✅
Métricas duplicadas en dims     : 0        ✅
```

---

## 3. QA del PCA (07_pca.py)

### 3.1 Variables incluidas
| Variable | Nulos antes de imputar | Mediana usada |
|---|---|---|
| BRECHA | 64.4% | 0.00 |
| AVANCE_FISICO | 19.3% | 100.00 |
| AVANCE_EJECUCION | 47.1% | 45.78 |
| DIAS_SIN_REPORTE | 62.8% | 248.00 |
| DIAS_ARRANQUE | 53.0% | 157.00 |
| COSTO_ACTUALIZADO | 0.0% | 713,877.84 |

### 3.2 Resultados del PCA
| Componente | Varianza explicada | Variables dominantes |
|---|---|---|
| PC1 | 25.0% | AVANCE_EJECUCION (+0.69), DIAS_SIN_REPORTE (+0.61) |
| PC2 | 19.9% | BRECHA (+0.70), AVANCE_FISICO (−0.65) |
| Total PC1+PC2 | 44.85% | — |

### 3.3 Validaciones del PCA
| Check | Resultado |
|---|---|
| Estandarización aplicada | StandardScaler (z-score) |
| Nulos imputados con mediana | ✅ |
| Export pca_proyectos.csv | 291,453 filas × 6 cols (15.7 MB) |
| SK_Proyecto nulos en export | 1 fila (nullable integer para compatibilidad Tableau) |
| Join con fact_inversiones en Tableau | 1:1 por SK_Proyecto ✅ |
| COSTO_ACTUALIZADO loading | 0.045 → confirma que el riesgo no depende del tamaño |

---

## 4. QA del Dashboard (Tableau)

### 4.1 Contraste y accesibilidad
| Elemento | Color | Contraste | ¿Sobrevive daltonismo? |
|---|---|---|---|
| Header | `#1E293B` fondo + blanco texto | Alto ✅ | ✅ |
| CRITICO | `#EF4444` rojo | Alto ✅ | ✅ (rojo vs gris, no vs verde) |
| ALERTA | `#F59E0B` ámbar | Alto ✅ | ✅ |
| NORMAL | `#94A3B8` gris azulado | Medio ✅ | ✅ |
| SIN DATO | `#E2E8F0` gris claro | Bajo (intencional — es ruido) | ✅ |

**Nota de accesibilidad:** La paleta evita el clásico rojo/verde (problema para daltonismo rojo-verde). NORMAL es gris, no verde — el rojo CRITICO contrasta contra gris sin ambigüedad.

### 4.2 Títulos analíticos
| Vista | Título | Tipo |
|---|---|---|
| Dashboard | "276 proyectos gastan más de lo que avanzan; Gobiernos Locales lidera el riesgo" | Analítico ✅ |
| Brecha por Sector | "Fonafe y Gob. Regionales: mayor desalineación" | Analítico ✅ |
| Semáforo | "276 proyectos fuera de rango — 20 requieren auditoría inmediata" | Analítico ✅ |
| Mapa/PCA | "Proyectos CRITICO se concentran en alta ejecución con alta desalineación" | Analítico ✅ |
| Tendencia | "Stock activo creció 4x desde 2018; cierres no siguen el ritmo" | Analítico ✅ |

### 4.3 Vista longitudinal (tiempo)
**Hoja:** Tendencia Temporal de Inversiones  
**Tipo:** Línea ACTIVE vs CLOSED por año  
**Línea de referencia:** 6,000 proyectos (nivel pre-2018)  
**Defiende:** La acumulación de obras sin cierre es un problema estructural post-2018, no puntual.

### 4.4 Vista transversal (comparación)
**Hoja:** Brecha por Sector  
**Tipo:** Barras horizontales ordenadas por brecha media  
**Dimensión:** 36 sectores institucionales  
**Defiende:** Fonafe y Gobiernos Regionales son outliers institucionales, no geografía.

### 4.5 Filtros y navegación
| Filtro | Scope | Estado |
|---|---|---|
| LIFECYCLE | Todas las vistas | ✅ Global |
| Use as Filter (Brecha por Sector) | Mapa de Riesgo PCA | ✅ Activo |
| Story de 5 pantallas | Navegación secuencial | ✅ |

---

## 5. Supuestos, Límites y Decisiones Documentadas

| Decisión | Justificación |
|---|---|
| Esquema estrella (no OBT) | Tableau procesa joins 1-nivel nativamente; OBT genera 291k × 51 cols con redundancia masiva |
| Una sola fact table | fact_situacional y fact_componentes tienen granularidad N:M incompatible con Tableau |
| Imputar AVANCE_FISICO=100 si CLOSED y nulo | Cierre administrativo asume obra culminada |
| Cap AVANCE > 100 → 100 | Errores de captura del sistema MEF; valores > 100 son imposibles físicamente |
| Umbral BRECHA 10pp → NORMAL | Absorbe desfase natural de registro MEF (gasto se registra antes que avance físico) |
| Umbral BRECHA 30pp → CRITICO | A ese nivel la desalineación no es explicable por desfase; requiere auditoría |
| PCA sobre 6 variables (no todas) | Variables con > 60% nulos (tras imputación con mediana) introducen sesgos; COSTO como variable de control |
| Mediana para imputar nulos en PCA | La distribución de BRECHA y DIAS_SIN_REPORTE es asimétrica; media sesgaría hacia outliers |
| 64.4% SIN DATO en semáforo | No son proyectos sin ejecución — son proyectos que no declararon avance físico. El dato faltante es en sí un hallazgo |

---

## 6. Reproducibilidad del Pipeline

```bash
# Desde la raíz del proyecto
cd ~/Documents/data-visualization-tf

# Bronze → Silver → Gold → Star Schema
python3 run_pipeline.py --from star_schema

# PCA
python3 scripts/07_pca.py

# Verificar outputs
ls -lh data/gold/
# Esperado: fact_inversiones.csv, dim_*.csv, pca_proyectos.csv
```

**Dependencias:** Python 3.11+, Polars, scikit-learn, sentence-transformers, pandas, matplotlib  
**Tiempo de ejecución:** ~1 min (star_schema) + ~30s (PCA)  
**Plataforma:** macOS Apple Silicon (zsh) — compatible con Linux

---

*QA Técnico — Entrega 6 · Data Visualization CC0211 · UPC · Julio 2026*