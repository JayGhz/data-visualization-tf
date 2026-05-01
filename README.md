# Proyecto Final: Brecha de eficiencia en la inversion publica peruana (2020-2026)

## Tema del proyecto
Este proyecto analiza la brecha de eficiencia en la inversion publica peruana mediante un dashboard de monitoreo que contrasta la ejecucion financiera con el avance fisico de las obras durante 2020-2026. Se busca pasar de un enfoque contable del gasto a uno centrado en resultados sobre infraestructura y servicios publicos.

## Pregunta analitica
¿En que medida la ejecucion financiera de las inversiones publicas refleja el avance real de las obras, y que sectores o regiones presentan los mayores cuellos de botella durante el periodo 2020-2026?

## Usuario objetivo
- Analistas de gestion publica y organismos de control (por ejemplo, Contraloria) que requieren detectar proyectos con alta ejecucion financiera y bajo avance fisico.
- Autoridades regionales y locales que necesitan evaluar su desempeno en inversion publica y comparar resultados entre jurisdicciones.
- Periodistas de investigacion y sociedad civil interesados en fiscalizar el uso de recursos publicos mediante visualizaciones comprensibles.

## Fuente de datos propuesta
### Origen
Portal de Datos Abiertos del Ministerio de Economia y Finanzas (MEF) del Peru. La fuente cubre inversiones publicas desde 2001 hasta 2026.

### Caracteristicas del dataset
- Registros: 260,199 observaciones.
- Variables: 68 en total; se seleccionan 27 variables enfocadas en caracterizacion, ejecucion financiera, avance fisico y tiempo.
- Dimensiones clave: sector, region y periodo temporal.
- Utilidad: habilita analisis longitudinal y comparativo con dashboards interactivos.

## Proposito del dashboard
- Detectar desalineaciones entre gasto ejecutado y avance fisico.
- Identificar patrones de estancamiento y cuellos de botella por sector o region.
- Brindar una herramienta de monitoreo y fiscalizacion con evidencia visual clara.

## Estructura del proyecto
- data/: fuentes originales y limpias.
- notebooks/: notebooks de perfilado, limpieza, analisis y modelado.
- outputs/: CSVs o tablas exportadas para Tableau.
- tableau/: workbook o enlace publicado.
- docs/: presentacion, diccionario, bitacora, QA.
