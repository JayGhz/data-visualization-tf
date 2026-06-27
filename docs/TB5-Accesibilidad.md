# Entrega 5 — Checklist de Accesibilidad
**Proyecto:** Brecha de Eficiencia en Inversión Pública Peruana (MEF 2020–2026)  
**Curso:** Data Visualization CC0211 · NRC 18519 · UPC  

---

## 1. Color

| Criterio | Estado | Detalle |
|---|---|---|
| El color no es el único canal de codificación | Cumple | El semáforo usa color + etiqueta de texto (NORMAL / ALERTA / CRITICO) en todas las vistas |
| La paleta es distinguible para daltonismo rojo-verde | Cumple | Se usa gris (no verde) para NORMAL, ámbar para ALERTA y rojo para CRITICO. Ámbar y rojo son distinguibles para deuteranopia |
| El fondo es blanco o de muy bajo contraste | Cumple | Fondo blanco (#FFFFFF) en todas las hojas; superficie de referencia #F9FAFB |
| Los colores categóricos no superan 6 valores simultáneos | Cumple | Máximo 4 categorías de semáforo; el resto usa secuencias monocromáticas de azul o verde |

---

## 2. Tipografía y legibilidad

| Criterio | Estado | Detalle |
|---|---|---|
| Tamaño de fuente mínimo en etiquetas: 10 pt | Cumple | Las etiquetas de barra y tooltip usan mínimo 10 pt |
| Los títulos de vista leen el gráfico, no lo nombran | Cumple | Ejemplo: "276 proyectos gastan más de lo que avanzan; Gobiernos Locales lidera el riesgo" en lugar de "Dashboard de Inversión Pública" |
| Las unidades están explícitas en ejes y tooltips | Cumple | Los ejes de brecha muestran "%" y "pp" (puntos porcentuales) |
| El footer incluye fuente y advertencia de calidad del dato | Cumple | "Fuente: MEF · Nota: 64.8% sin dato de avance físico" |

---

## 3. Jerarquía visual

| Criterio | Estado | Detalle |
|---|---|---|
| La vista principal es visualmente dominante | Cumple | Brecha por Sector ocupa el mayor espacio en el dashboard; las vistas secundarias son más compactas |
| Los filtros están en posición consistente | Cumple | Filtro LIFECYCLE ubicado en la zona superior del dashboard, visible antes de la lectura de gráficos |
| El panel de insights está separado del área de gráficos | Cumple | Panel derecho con fondo diferenciado y estructura Hallazgo / Por qué / Acción |
| No se usan efectos decorativos (sombras, gradientes, 3D) | Cumple | Todas las vistas usan geometría plana |

---

## 4. Interactividad y tooltips

| Criterio | Estado | Detalle |
|---|---|---|
| Los tooltips añaden información que no está en la vista | Cumple | Los tooltips incluyen nombre del proyecto, sector, avance físico exacto y brecha en puntos porcentuales |
| El filtro cruzado entre Brecha por Sector y el mapa está documentado | Cumple | "Use as Filter" activo en la vista de barras; al seleccionar un sector el mapa filtra automáticamente |
| Las hojas exploratorias están separadas del dashboard principal | Cumple | Scatter, distribución por rango de costo y tendencia temporal son hojas independientes |

---

## 5. Limitaciones conocidas

- Las coordenadas LATITUD/LONGITUD tienen 0.2% de nulos en el dataset Cierre, lo que genera puntos faltantes en el mapa para proyectos cerrados con dato geográfico incompleto.
- La paleta de semáforo no ha sido validada formalmente con herramienta de simulación de daltonismo (Coblis o equivalente). La selección se basa en criterios de contraste conocidos, no en prueba empírica.
- El gráfico de scatter usa transparencia de 20% para manejar la densidad de 291,000 puntos. En pantallas de baja resolución, la nube puede aparecer más oscura de lo esperado.

---

*Entrega 5 — Data Visualization CC0211 · UPC · Junio 2026*
