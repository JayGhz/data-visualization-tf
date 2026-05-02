# 📊 Data Profile & Pipeline Decisions

## 1. Dataset Overview
- **Detalle**: 260,425 rows, 68 columns
- **F12B**: 213,244 rows, 54 columns
- **Cierre**: 108,843 rows, 57 columns

## 2. Join Overlap Audit (CODIGO_UNICO)
| Connection | Unique Projects | % of Detalle |
| :--- | :--- | :--- |
| **Detalle Total** | 260,358 | 100% |
| **F12B Total** | 213,244 | 81.9% |
| **Cierre Total** | 105,397 | 40.5% |
| Bridge F12B-Detalle | 147,655 | 56.7% |
| Bridge F12B-Cierre | 46,456 | 17.8% |
| Direct Detalle-Cierre | 1 | 0.0% |

## 3. Data Cleaning & Imputation Plan
| Dataset | Variable | Finding / Issue | Strategy |
| :--- | :--- | :--- | :--- |
| Detalle | `FEC_REG_F9` | 94.4% missing | Structurally sparse, Flag only |
| Detalle | `ETAPA_F9` | 94.4% missing | Structurally sparse, Flag only |
| Detalle | `PIA_ANIO_ACTUAL` | 84.6% missing | Structurally sparse, Flag only |
| Detalle | `CERTIF_ANIO_ACTUAL` | 84.6% missing | Structurally sparse, Flag only |
| Detalle | `COMPROM_ANUAL_ANIO_ACTUAL` | 84.6% missing | Structurally sparse, Flag only |
| Detalle | `PMI_ANIO_1` | 78.9% missing | Structurally sparse, Flag only |
| Detalle | `PMI_ANIO_4` | 78.1% missing | Structurally sparse, Flag only |
| Detalle | `PMI_ANIO_2` | 78.1% missing | Structurally sparse, Flag only |
| Detalle | `PMI_ANIO_3` | 78.1% missing | Structurally sparse, Flag only |
| Detalle | `AVANCE_FISICO` | 76.1% missing | Structurally sparse, Flag only |
| Detalle | `ULT_FEC_DECLA_ESTIM` | 67.1% missing | Structurally sparse, Flag only |
| Detalle | `FEC_INI_EJEC_FISICA` | 48.0% missing | Flag column, no imputation |
| Detalle | `FEC_FIN_EJEC_FISICA` | 48.0% missing | Flag column, no imputation |
| Detalle | `AVANCE_EJECUCION` | 46.5% missing | Flag column, no imputation |
| Detalle | `DES_TIPOLOGIA` | 39.6% missing | Flag column, no imputation |
| Detalle | `FEC_INI_EJECUCION` | 35.3% missing | Flag column, no imputation |
| Detalle | `FEC_FIN_EJECUCION` | 35.3% missing | Flag column, no imputation |
| Detalle | `ETAPA_F8` | 29.7% missing | Flag column, no imputation |
| Detalle | `NUM_HABITANTES_BENEF` | 23.6% missing | Flag column, no imputation |
| Detalle | `ALTERNATIVA` | 23.5% missing | Flag column, no imputation |
| Detalle | `PRIMER_DEVENGADO` | 22.0% missing | Flag column, no imputation |
| Detalle | `ULTIMO_DEVENGADO` | 22.0% missing | Flag column, no imputation |
| Detalle | `MONTO_ET_F8` | 20.5% missing | Flag column, no imputation |
| Detalle | `NOMBRE_UEI` | 19.5% missing | Retain null |
| Detalle | `NOMBRE_OPMI` | 16.8% missing | Retain null |
| F12B | `DEV_ENE_AÑO_VIG` | 91.2% missing | Structurally sparse, Flag only |
| F12B | `DEV_FEB_AÑO_VIG` | 91.2% missing | Structurally sparse, Flag only |
| F12B | `DEV_MAR_AÑO_VIG` | 91.2% missing | Structurally sparse, Flag only |
| F12B | `DEV_ABR_AÑO_VIG` | 91.2% missing | Structurally sparse, Flag only |
| F12B | `DEV_MAY_AÑO_VIG` | 91.2% missing | Structurally sparse, Flag only |
| F12B | `DEV_JUN_AÑO_VIG` | 91.2% missing | Structurally sparse, Flag only |
| F12B | `DEV_JUL_AÑO_VIG` | 91.2% missing | Structurally sparse, Flag only |
| F12B | `DEV_AGO_AÑO_VIG` | 91.2% missing | Structurally sparse, Flag only |
| F12B | `DEV_SET_AÑO_VIG` | 91.2% missing | Structurally sparse, Flag only |
| F12B | `DEV_OCT_AÑO_VIG` | 91.2% missing | Structurally sparse, Flag only |
| F12B | `DEV_NOV_AÑO_VIG` | 91.2% missing | Structurally sparse, Flag only |
| F12B | `DEV_DIC_AÑO_VIG` | 91.2% missing | Structurally sparse, Flag only |
| F12B | `ULT_PERIODO_REG_F12B` | 68.7% missing | Structurally sparse, Flag only |
| F12B | `AVANCE_FISICO` | 57.9% missing | Structurally sparse, Flag only |
| F12B | `ULT_FEC_DECLA_ESTIM` | 46.1% missing | Flag column, no imputation |
| F12B | `ACC_PROBLEMA` | 43.4% missing | Flag column, no imputation |
| F12B | `ULT_PROBLEMA` | 43.4% missing | Flag column, no imputation |
| F12B | `PRIMER_DEVENGADO` | 23.8% missing | Flag column, no imputation |
| F12B | `ULTIMO_DEVENGADO` | 23.8% missing | Flag column, no imputation |
| F12B | `INICIO_EJEC_FISICA` | 22.1% missing | Flag column, no imputation |
| F12B | `CULMINA_EJEC_FISICA` | 22.1% missing | Flag column, no imputation |
| F12B | `DEVENGADO_ACUMULADO` | 16.3% missing | Retain null |
| F12B | `ULT_ESTADO_SITUACIONAL` | 11.1% missing | Retain null |
| F12B | `AVANCE_EJECUCION` | 9.5% missing | Retain null |
| F12B | `MONTO_ACTUALIZADO_1` | 9.5% missing | Retain null |
| Cierre | `FUENTE_FINANCIAMIENTO` | 66.0% missing | Structurally sparse, Flag only |
| Cierre | `DES_TIPOLOGIA` | 65.9% missing | Structurally sparse, Flag only |
| Cierre | `FEC_TRANSFERENCIA` | 60.8% missing | Structurally sparse, Flag only |
| Cierre | `CULMINA_EJEC_FISICA` | 55.8% missing | Structurally sparse, Flag only |
| Cierre | `INICIO_EJEC_FISICA` | 55.8% missing | Structurally sparse, Flag only |
| Cierre | `FEC_INI_OPER` | 54.8% missing | Structurally sparse, Flag only |
| Cierre | `TOTAL_LIQUIDACION` | 52.6% missing | Structurally sparse, Flag only |
| Cierre | `FEC_LIQUIDACION` | 48.3% missing | Flag column, no imputation |
| Cierre | `UNIDAD_OPE_MANT` | 39.0% missing | Flag column, no imputation |
| Cierre | `DES_MODALIDAD` | 30.6% missing | Flag column, no imputation |
| Cierre | `RESPONSABLE_UEI` | 23.5% missing | Flag column, no imputation |
| Cierre | `BENEFICIARIO` | 22.9% missing | Flag column, no imputation |
| Cierre | `NOM_OPMI` | 22.1% missing | Flag column, no imputation |
| Cierre | `FEC_REG_F9` | 22.1% missing | Flag column, no imputation |
| Cierre | `CULMINADA` | 22.1% missing | Flag column, no imputation |
| Cierre | `ETAPA_F9` | 22.1% missing | Flag column, no imputation |
| Cierre | `NOM_UEI` | 21.3% missing | Flag column, no imputation |
| Cierre | `PRIMER_DEVENGADO` | 13.7% missing | Retain null |
| Cierre | `ULTIMO_DEVENGADO` | 13.7% missing | Retain null |
| Cierre | `DES_CIERRE` | 3.2% missing | Retain null |
| Cierre | `CODIGO_UNICO` | 3.2% missing | Retain null |
| Cierre | `NOM_UF` | 1.2% missing | Retain null |
| Cierre | `ENTIDAD` | 0.2% missing | Retain null |
| Cierre | `LATITUD` | 0.2% missing | Retain null |
| Cierre | `LONGITUD` | 0.2% missing | Retain null |
| Join Audit | `Detalle/Cierre` | Shared projects < 10 | Use F12B as bridge |
| Detalle | `FEC_INI_EJECUCION` | 120 extreme future dates (e.g. 2039) | Nullify in Silver |
| Detalle | `FEC_FIN_EJECUCION` | 143 extreme future dates (e.g. 2039) | Nullify in Silver |
| Detalle | `Dates` | 132295 projects with Start >= End | Flag as INCONSISTENTE in Gold |
| Temporal | `Dates` | Multiple formats/YYYYMM | Parse to datetime/Extract year |

## 4. Key Indicators Distribution

### Situación (Top 5)
| Situación | Count | % |
| :--- | :--- | :--- |
| VIABLE | 200,146 | 76.9% |
| APROBADO | 60,047 | 23.1% |
| EN FORMULACION | 232 | 0.1% |

### TIPO_INVERSION vs TIENE_AVAN_FISICO (Crosstab)
| TIPO_INVERSION | NO (Count) | SI (Count) | % with Progress (SI) |
| :--- | :--- | :--- | :--- |
| INTERVENCIONES IRI | 5,149 | 0 | **0.0%** |
| INVERSIONES IOARR | 36,414 | 18,489 | **33.7%** |
| PIP MAYOR (SNIP) | 37,412 | 7,729 | **17.1%** |
| PIP MENOR (SNIP) | 46,569 | 2,437 | **5.0%** |
| PROGRAMA (SNIP) | 38 | 0 | **0.0%** |
| PROGRAMA DE INVERSION | 169 | 0 | **0.0%** |
| PROYECTO DE INVERSION | 78,921 | 26,954 | **25.5%** |
| PROYECTO EMBLEMATICO | 4 | 116 | **96.7%** |
| PROYECTO ENERGIA | 1 | 3 | **75.0%** |
| PROYECTO ESSALUD | 4 | 0 | **0.0%** |
| PROYECTO FORCOR | 0 | 1 | **100.0%** |
| PROYECTO FORSUR | 0 | 1 | **100.0%** |
| PROYECTO LAUDOS | 11 | 0 | **0.0%** |
| PROYECTO PEIP | 1 | 0 | **0.0%** |
| PROYECTO SANEAMIENTO | 1 | 1 | **50.0%** |
