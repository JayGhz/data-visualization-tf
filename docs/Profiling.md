# Perfil de Datos y Decisiones de Pipeline

## 1. Resumen de Datasets
- **Detalle**: 183,759 filas, 68 columnas
- **F12B**: 215,996 filas, 54 columnas
- **Cierre**: 111,207 filas, 57 columnas

## 2. Auditoría de Solapamiento CUI
| Conexión | Proyectos únicos | % de Detalle |
| :--- | :--- | :--- |
| **Total Detalle** | 183,692 | 100% |
| **Total F12B** | 215,996 | 117.6% |
| **Total Cierre** | 107,762 | 58.7% |
| Puente F12B-Detalle | 117,930 | 64.2% |
| Puente F12B-Cierre | 48,147 | 26.2% |
| Directo Detalle-Cierre | 1 | 0.0% |

## 3. Plan de Limpieza e Imputación
| Dataset | Variable | Hallazgo / Problema | Estrategia |
| :--- | :--- | :--- | :--- |
| Detalle | `FEC_REG_F9` | 91.7% faltante | Estructuralmente disperso, solo marcar |
| Detalle | `ETAPA_F9` | 91.7% faltante | Estructuralmente disperso, solo marcar |
| Detalle | `PIA_ANIO_ACTUAL` | 77.3% faltante | Estructuralmente disperso, solo marcar |
| Detalle | `CERTIF_ANIO_ACTUAL` | 77.3% faltante | Estructuralmente disperso, solo marcar |
| Detalle | `COMPROM_ANUAL_ANIO_ACTUAL` | 77.3% faltante | Estructuralmente disperso, solo marcar |
| Detalle | `PMI_ANIO_1` | 71.3% faltante | Estructuralmente disperso, solo marcar |
| Detalle | `PMI_ANIO_4` | 70.3% faltante | Estructuralmente disperso, solo marcar |
| Detalle | `PMI_ANIO_2` | 70.3% faltante | Estructuralmente disperso, solo marcar |
| Detalle | `PMI_ANIO_3` | 70.3% faltante | Estructuralmente disperso, solo marcar |
| Detalle | `AVANCE_FISICO` | 66.4% faltante | Estructuralmente disperso, solo marcar |
| Detalle | `ULT_FEC_DECLA_ESTIM` | 57.4% faltante | Estructuralmente disperso, solo marcar |
| Detalle | `AVANCE_EJECUCION` | 39.1% faltante | Marcar columna, sin imputación |
| Detalle | `FEC_FIN_EJEC_FISICA` | 39.0% faltante | Marcar columna, sin imputación |
| Detalle | `FEC_INI_EJEC_FISICA` | 39.0% faltante | Marcar columna, sin imputación |
| Detalle | `DES_TIPOLOGIA` | 31.3% faltante | Marcar columna, sin imputación |
| Detalle | `PRIMER_DEVENGADO` | 30.1% faltante | Marcar columna, sin imputación |
| Detalle | `ULTIMO_DEVENGADO` | 30.1% faltante | Marcar columna, sin imputación |
| Detalle | `NUM_HABITANTES_BENEF` | 27.0% faltante | Marcar columna, sin imputación |
| Detalle | `ALTERNATIVA` | 27.0% faltante | Marcar columna, sin imputación |
| Detalle | `FEC_INI_EJECUCION` | 25.4% faltante | Marcar columna, sin imputación |
| Detalle | `FEC_FIN_EJECUCION` | 25.4% faltante | Marcar columna, sin imputación |
| Detalle | `ETAPA_F8` | 22.8% faltante | Marcar columna, sin imputación |
| Detalle | `MONTO_ET_F8` | 22.1% faltante | Marcar columna, sin imputación |
| Detalle | `NOMBRE_UEI` | 9.4% faltante | Conservar nulo |
| Detalle | `DES_MODALIDAD` | 9.0% faltante | Conservar nulo |
| F12B | `DEV_ENE_AÑO_VIG` | 89.1% faltante | Estructuralmente disperso, solo marcar |
| F12B | `DEV_FEB_AÑO_VIG` | 89.1% faltante | Estructuralmente disperso, solo marcar |
| F12B | `DEV_MAR_AÑO_VIG` | 89.1% faltante | Estructuralmente disperso, solo marcar |
| F12B | `DEV_ABR_AÑO_VIG` | 89.1% faltante | Estructuralmente disperso, solo marcar |
| F12B | `DEV_MAY_AÑO_VIG` | 89.1% faltante | Estructuralmente disperso, solo marcar |
| F12B | `DEV_JUN_AÑO_VIG` | 89.1% faltante | Estructuralmente disperso, solo marcar |
| F12B | `DEV_JUL_AÑO_VIG` | 89.1% faltante | Estructuralmente disperso, solo marcar |
| F12B | `DEV_AGO_AÑO_VIG` | 89.1% faltante | Estructuralmente disperso, solo marcar |
| F12B | `DEV_SET_AÑO_VIG` | 89.1% faltante | Estructuralmente disperso, solo marcar |
| F12B | `DEV_OCT_AÑO_VIG` | 89.1% faltante | Estructuralmente disperso, solo marcar |
| F12B | `DEV_NOV_AÑO_VIG` | 89.1% faltante | Estructuralmente disperso, solo marcar |
| F12B | `DEV_DIC_AÑO_VIG` | 89.1% faltante | Estructuralmente disperso, solo marcar |
| F12B | `ULT_PERIODO_REG_F12B` | 68.6% faltante | Estructuralmente disperso, solo marcar |
| F12B | `AVANCE_FISICO` | 57.4% faltante | Estructuralmente disperso, solo marcar |
| F12B | `ULT_FEC_DECLA_ESTIM` | 45.5% faltante | Marcar columna, sin imputación |
| F12B | `ULT_PROBLEMA` | 42.7% faltante | Marcar columna, sin imputación |
| F12B | `ACC_PROBLEMA` | 42.7% faltante | Marcar columna, sin imputación |
| F12B | `PRIMER_DEVENGADO` | 23.7% faltante | Marcar columna, sin imputación |
| F12B | `ULTIMO_DEVENGADO` | 23.7% faltante | Marcar columna, sin imputación |
| F12B | `INICIO_EJEC_FISICA` | 21.8% faltante | Marcar columna, sin imputación |
| F12B | `CULMINA_EJEC_FISICA` | 21.8% faltante | Marcar columna, sin imputación |
| F12B | `DEVENGADO_ACUMULADO` | 16.1% faltante | Conservar nulo |
| F12B | `ULT_ESTADO_SITUACIONAL` | 11.1% faltante | Conservar nulo |
| F12B | `AVANCE_EJECUCION` | 9.5% faltante | Conservar nulo |
| F12B | `MONTO_ACTUALIZADO_1` | 9.5% faltante | Conservar nulo |
| Cierre | `FUENTE_FINANCIAMIENTO` | 66.7% faltante | Estructuralmente disperso, solo marcar |
| Cierre | `DES_TIPOLOGIA` | 65.5% faltante | Estructuralmente disperso, solo marcar |
| Cierre | `FEC_TRANSFERENCIA` | 59.8% faltante | Estructuralmente disperso, solo marcar |
| Cierre | `FEC_INI_OPER` | 55.8% faltante | Estructuralmente disperso, solo marcar |
| Cierre | `CULMINA_EJEC_FISICA` | 55.3% faltante | Estructuralmente disperso, solo marcar |
| Cierre | `INICIO_EJEC_FISICA` | 55.2% faltante | Estructuralmente disperso, solo marcar |
| Cierre | `TOTAL_LIQUIDACION` | 53.6% faltante | Estructuralmente disperso, solo marcar |
| Cierre | `FEC_LIQUIDACION` | 47.9% faltante | Marcar columna, sin imputación |
| Cierre | `UNIDAD_OPE_MANT` | 38.5% faltante | Marcar columna, sin imputación |
| Cierre | `DES_MODALIDAD` | 30.5% faltante | Marcar columna, sin imputación |
| Cierre | `BENEFICIARIO` | 23.0% faltante | Marcar columna, sin imputación |
| Cierre | `RESPONSABLE_UEI` | 23.0% faltante | Marcar columna, sin imputación |
| Cierre | `NOM_OPMI` | 21.7% faltante | Marcar columna, sin imputación |
| Cierre | `FEC_REG_F9` | 21.6% faltante | Marcar columna, sin imputación |
| Cierre | `CULMINADA` | 21.6% faltante | Marcar columna, sin imputación |
| Cierre | `ETAPA_F9` | 21.6% faltante | Marcar columna, sin imputación |
| Cierre | `NOM_UEI` | 20.9% faltante | Marcar columna, sin imputación |
| Cierre | `PRIMER_DEVENGADO` | 13.4% faltante | Conservar nulo |
| Cierre | `ULTIMO_DEVENGADO` | 13.4% faltante | Conservar nulo |
| Cierre | `DES_CIERRE` | 3.1% faltante | Conservar nulo |
| Cierre | `CODIGO_UNICO` | 3.1% faltante | Conservar nulo |
| Cierre | `NOM_UF` | 1.2% faltante | Conservar nulo |
| Cierre | `ENTIDAD` | 0.2% faltante | Conservar nulo |
| Cierre | `LATITUD` | 0.2% faltante | Conservar nulo |
| Cierre | `LONGITUD` | 0.2% faltante | Conservar nulo |
| Auditoría Join | `Detalle/Cierre` | Proyectos compartidos < 10 | Usar F12B como puente |
| Detalle | `DEV_ANIO_ACTUAL` | 12.7% atípicos, 1 negativos | Conservar por defecto |
| Detalle | `AVANCE_FISICO` | 0.0% atípicos, 219 valores >100 | Limitar a 100 |
| Detalle | `PIM_ANIO_ACTUAL` | 22.1% atípicos, 0 negativos | Conservar por defecto |
| Detalle | `DEVEN_ACUMUL_ANIO_ANT` | 14.5% atípicos | Conservar (proyectos de alto valor) |
| Detalle | `COSTO_ACTUALIZADO` | 11.8% atípicos | Conservar (proyectos de alto valor) |
| Detalle | `MONTO_VIABLE` | 11.3% atípicos | Conservar (proyectos de alto valor) |
| Detalle | `AVANCE_EJECUCION` | 0.1% atípicos, 177 valores >100 | Limitar a 100 |
| Detalle | `NUM_HABITANTES_BENEF` | 14.4% atípicos, 0 negativos | Conservar por defecto |
| F12B | `AVANCE_FISICO` | 13.1% atípicos, 352 valores >100 | Limitar a 100 |
| F12B | `DEVENGADO_ACUMULADO` | 14.2% atípicos | Conservar (proyectos de alto valor) |
| F12B | `AVANCE_EJECUCION` | 0.0% atípicos, 277 valores >100 | Limitar a 100 |
| Detalle | `FEC_INI_EJECUCION` | 110 fechas futuras extremas | Anular en Silver |
| Detalle | `FEC_FIN_EJECUCION` | 134 fechas futuras extremas | Anular en Silver |
| Detalle | `Fechas` | 109072 proyectos con Inicio >= Fin | Marcar como INCONSISTENTE en Gold |
| Temporal | `Fechas` | Múltiples formatos / YYYYMM | Parsear a datetime / Extraer año |

## 4. Distribución de Indicadores Clave

### Situación (Top 5)
| Situación | Cantidad | % |
| :--- | :--- | :--- |
| VIABLE | 134,689 | 73.3% |
| APROBADO | 48,838 | 26.6% |
| EN FORMULACION | 232 | 0.1% |

### TIPO_INVERSION vs TIENE_AVAN_FISICO
| Tipo Inversión | Tiene Avance Físico | Cantidad | % del Total |
| :--- | :--- | :--- | :--- |
| INTERVENCIONES IRI | NO | 5,131 | 2.8% |
| INVERSIONES IOARR | NO | 25,139 | 13.7% |
| INVERSIONES IOARR | SI | 18,573 | 10.1% |
| PIP MAYOR (SNIP) | NO | 17,152 | 9.3% |
| PIP MAYOR (SNIP) | SI | 7,782 | 4.2% |
| PIP MENOR (SNIP) | NO | 22,499 | 12.2% |
| PIP MENOR (SNIP) | SI | 2,490 | 1.4% |
| PROGRAMA (SNIP) | NO | 38 | 0.0% |
| PROGRAMA DE INVERSION | NO | 170 | 0.1% |
| PROYECTO DE INVERSION | NO | 57,385 | 31.2% |
| PROYECTO DE INVERSION | SI | 27,262 | 14.8% |
| PROYECTO EMBLEMATICO | NO | 1 | 0.0% |
| PROYECTO EMBLEMATICO | SI | 113 | 0.1% |
| PROYECTO ENERGIA | NO | 1 | 0.0% |
| PROYECTO ENERGIA | SI | 3 | 0.0% |
| PROYECTO ESSALUD | NO | 4 | 0.0% |
| PROYECTO FONCOR | SI | 1 | 0.0% |
| PROYECTO FORSUR | SI | 1 | 0.0% |
| PROYECTO LAUDOS | NO | 11 | 0.0% |
| PROYECTO PEIP | NO | 1 | 0.0% |
| PROYECTO SANEAMIENTO | NO | 1 | 0.0% |
| PROYECTO SANEAMIENTO | SI | 1 | 0.0% |
