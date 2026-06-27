# Entrega 5 — Historia Visual
**Proyecto:** Brecha de Eficiencia en Inversión Pública Peruana (MEF 2020–2026)  
**Curso:** Data Visualization CC0211 · NRC 18519 · UPC  

---

## Historia Visual

La historia tiene cinco pantallas. Cada una responde una pregunta progresiva que lleva al lector desde el problema hasta la acción concreta.

---

### Pantalla 1 — El sistema gasta pero no reporta

**Pregunta que responde:** ¿Qué tan grave es el problema de cobertura del seguimiento físico?

**Mensaje central:** El 64.8% de los proyectos del universo MEF nunca declaró avance físico. No es que no avancen: es que no reportan. Eso hace imposible la fiscalización efectiva.

**Elemento visual principal:** Tabla de semáforo con cuatro filas (SIN DATO, NORMAL, ALERTA, CRITICO). La fila SIN DATO ocupa 187,668 proyectos — casi dos tercios del total.

**Anotación de contexto:** "187 668 proyectos ejecutan presupuesto sin declarar avance físico en el sistema MEF."

**Por qué abre la historia:** Establece el problema de fondo antes de mostrar los datos de brecha. El lector necesita entender primero que el sistema tiene un problema de cobertura, no solo de desalineación.

---

### Pantalla 2 — Donde hay dato, el gasto va por delante de la obra

**Pregunta que responde:** Entre los proyectos que sí reportan, ¿cuántos muestran desalineación?

**Mensaje central:** De los 103,785 proyectos con dato de avance físico, 276 presentan una brecha mayor a 10 puntos porcentuales. Veinte de ellos superan los 30 puntos: gastaron más del 30% adicional de lo que avanzaron físicamente.

**Elemento visual principal:** Gráfico de barras horizontales de Brecha por Sector. El eje muestra valores positivos (finanzas adelante) y negativos (físico adelante) en la misma escala. El color semántico — gris para NORMAL, ámbar para ALERTA, rojo para CRITICO — permite identificar excepciones sin recorrer todas las barras.

**Anotación de contexto:** "Una brecha de 30 pp no se explica por desfase administrativo. A ese nivel, el sistema necesita auditoría."

**Transición:** Los 276 proyectos en alerta no son aleatorios. Se concentran en ciertos niveles de gobierno.

---

### Pantalla 3 — Gobiernos Locales concentra el riesgo

**Pregunta que responde:** ¿Qué nivel de gobierno o sector presenta el mayor volumen de proyectos problemáticos?

**Mensaje central:** Gobiernos Locales reúne 83,340 proyectos con una brecha media de −10.76 puntos porcentuales. El valor negativo indica que el avance físico declarado supera al avance de ejecución financiera registrado, lo que puede reflejar rezago en el ingreso de devengados al SIAF o sobreestimación del avance físico reportado. El volumen hace de este nivel el foco prioritario de monitoreo.

**Elemento visual principal:** La misma vista de Brecha por Sector, filtrada con el selector de LIFECYCLE en ACTIVE. Gobiernos Locales aparece en la parte inferior del gráfico con la barra más extendida hacia la izquierda.

**Anotación de contexto:** "83 340 proyectos activos. Si el 1% presenta irregularidad, son más de 800 casos que el sistema actual no puede detectar automáticamente."

**Transición:** El problema no es homogéneo en el territorio. El mapa muestra dónde se acumulan los casos críticos.

---

### Pantalla 4 — Los proyectos críticos tienen coordenadas

**Pregunta que responde:** ¿Hay concentración geográfica de los casos más graves?

**Mensaje central:** Los 20 proyectos clasificados como CRITICO no están distribuidos aleatoriamente. El mapa de puntos con color semántico permite identificar los departamentos con mayor densidad de alertas activas.

**Elemento visual principal:** Mapa de puntos georreferenciados por LATITUD/LONGITUD. Cada punto representa un proyecto. El color sigue la paleta del semáforo. El filtro cruzado con la vista de sectores permite identificar qué sectores concentran los puntos rojos en cada región.

**Anotación de contexto:** "El mapa no muestra todos los proyectos. Muestra los que tienen coordenadas y dato de avance. El resto es parte del 64.8% invisible."

**Transición:** El problema no es solo de hoy. El stock de proyectos activos viene creciendo desde 2018 sin un cierre proporcional.

---

### Pantalla 5 — El portafolio creció cuatro veces sin que el cierre acompañara

**Pregunta que responde:** ¿Es un problema puntual o estructural en el tiempo?

**Mensaje central:** Los proyectos ACTIVE registrados por año pasaron de aproximadamente 6,000 en 2018 a más de 23,000 en 2024. Los proyectos CLOSED no crecieron al mismo ritmo. La acumulación de obras sin cierre es estructural, no coyuntural.

**Elemento visual principal:** Gráfico de líneas temporales con dos series (ACTIVE en azul, CLOSED en verde) sobre el mismo eje Y. Una línea de referencia horizontal en 6,000 proyectos (nivel promedio pre-2018) contextualiza la magnitud del cambio.

**Anotación de contexto:** "Si la capacidad de seguimiento no escala al mismo ritmo que el portafolio, el riesgo de paralización aumenta estructuralmente cada año."

**Cierre de la historia:** El lector termina con una imagen clara: el problema no es solo que algunos proyectos gastan más de lo que avanzan. Es que el sistema de seguimiento no cubre la mayoría, el portafolio activo cuadruplicó su tamaño en seis años, y los mecanismos de cierre no lo acompañaron. La acción no es auditar 20 proyectos críticos: es rediseñar el sistema de reporte.

---

## Reflexión Metodológica

### Qué decisiones resultaron más difíciles

**La elección de la unidad de análisis.** El universo tiene tres datasets con granularidades distintas y solapamiento casi nulo entre Detalle y Cierre. La decisión de usar unión diagonal (no join) para construir el universo maestro fue contraintuitiva pero correcta: preserva la integridad de cada fuente sin crear registros artificiales.

**El umbral de CRITICO.** Fijar 30 puntos porcentuales como límite no es una decisión estadística: es un umbral de negocio basado en el desfase natural de registro del sistema MEF (estimado en hasta 10 pp). Por encima de 30 pp, el desfase no tiene explicación administrativa razonable.

**La decisión de no usar mapa cloroplético.** Un mapa por departamento con color por brecha media oculta la heterogeneidad interna: un departamento puede tener 500 proyectos NORMALES y 1 CRITICO, y el promedio no lo señalaría. El mapa de puntos individuales respeta la granularidad del dato.

### Qué funcionó mejor de lo esperado

La clasificación NLP de `ULT_PROBLEMA` resultó más útil de lo anticipado. El enfoque híbrido de Regex más embeddings logró clasificar el 42.9% del universo en cinco categorías limpias (TECNICO, CONTRATACION, PRESUPUESTO, SOCIAL, EMERGENCIA), directamente interpretables por un analista de gestión pública.

La paleta de tres colores semánticos (gris / ámbar / rojo) resultó más efectiva que una escala continua de color para la BRECHA. Con una escala continua, los 20 proyectos CRITICO quedarían visualmente diluidos en el gradiente.

### Limitaciones no resueltas

El 64.8% de proyectos sin dato de avance físico es la limitación más importante. El análisis de brecha solo cubre el 35.2% del universo. Las conclusiones son válidas para ese subconjunto, pero no pueden generalizarse al total sin asumir que la cobertura es aleatoria, lo cual no está demostrado.

La BRECHA es una diferencia puntual, no una trayectoria. Un proyecto que tuvo BRECHA de 50 pp en 2022 y la corrigió a 5 pp en 2024 aparece como NORMAL en el análisis actual. Un análisis longitudinal requeriría series de tiempo por `CODIGO_UNICO`, que no están disponibles en la fuente del MEF.

### Qué se haría diferente en la siguiente iteración

- Validar la paleta con una herramienta de simulación de daltonismo antes de la versión final.
- Incluir una vista de evolución de la brecha por cohorte de año de inicio.
- Agregar un parámetro interactivo en Tableau para que el usuario ajuste el umbral de CRITICO entre 20 y 40 pp.
- Publicar el workbook en Tableau Public para habilitar la reproducibilidad fuera del entorno local.

---

*Entrega 5 — Data Visualization CC0211 · UPC · Junio 2026*
