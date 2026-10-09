# INVENTARIO de datos

> **Qué es un inventario de datos:** una lista de todo lo que tenemos antes de analizar nada: qué archivos hay, qué periodo cubren, qué columnas contienen, cuántas filas, y qué problemas de calidad o huecos tienen. Es el primer paso de cualquier proyecto: no se puede analizar bien lo que no se conoce.

## 1. Qué había en la carpeta

| Tipo de archivo | Cantidad | Qué son |
|---|---|---|
| CSV | 0 | — |
| Excel | 0 | — |
| PDF | 0 | — |
| Fotos HEIC (iPhone) | **55** | Fotos de la pantalla del móvil de trabajo tomadas el 07/10/2026 entre las 19:23 y las 19:30 |

No había exportaciones en CSV/Excel de la plataforma ni de Uber. **No hay ningún dato de Uber.**

Las fotos están en la carpeta padre (no se han movido). Se copiaron a `datos/originales/` en modo solo lectura y se trabajó siempre sobre copias (`datos/jpg/`). Ninguna de las dos carpetas se sube a Git porque contienen datos personales (nombre completo y foto de perfil).

## 2. Qué muestra cada foto

| Fotos | App | Pantalla | Datos que contiene | Cómo se extrajo |
|---|---|---|---|---|
| IMG_7831–7832 | App conductor | Perfil y perfil público | Nombre y foto (**datos personales, no se usan**), nº de viajes históricos, meses en la plataforma, etiquetas de valoración | No se usa salvo nº de viajes y antigüedad |
| IMG_7833 | App | Valoración | Media 4,84 de las últimas 100 valoraciones (96 positivas, 0 neutras, 4 negativas) y etiquetas | OCR + lectura manual |
| IMG_7834 | App | Tasa de finalización | Última semana: 38 viajes, 34 finalizados, 4 cancelaciones forzosas del pasajero | OCR + lectura manual |
| IMG_7835–7859 (25 fotos) | App | **Historial de viajes** | Por viaje: fecha, hora, tipo de servicio, importe e icono de método de pago | OCR automático + revisión manual de las 25 fotos |
| IMG_7860–7869 | App | Finanzas | Ganancia semanal (5–11 oct), mensual (sep, oct) y diaria (30 sep, 1, 2, 4, 5, 6, 7 oct) | OCR + lectura manual |
| IMG_7870–7873 | App | Desglose de ganancias | Por mes: precio base, extras, incentivos, propinas, pago app/efectivo, peajes, «pagado a bordo» | OCR + lectura manual |
| IMG_7874–7876 | App de la flota | Turnos (mes, semana, día) | Tiempo efectivo y tiempo total | OCR + lectura manual |
| IMG_7877–7885 | App de la flota | Detalle de jornada | 8 días (28/09–07/10): hora inicio/fin, conducción efectiva, recarga eléctrica, cuidado del vehículo, conducción no efectiva, descansos, tiempo total | OCR + lectura manual (IMG_7878 es repetida de 7877) |

## 3. Tablas resultantes

| Archivo | Filas | Periodo | Columnas principales |
|---|---|---|---|
| `datos/intermedios/viajes_ocr_candidatos.csv` | 245 | 31/08–07/10 | Una fila por viaje **visto en cada foto** (con repetidos por solape) |
| `datos/intermedios/viajes_transcritos.csv` | **212** | 31/08 21:23 – 07/10 10:37 | fecha, hora, producto, importe_eur, metodo_pago, imágenes de origen |
| `datos/intermedios/jornadas_flota_transcritas.csv` | 8 | 28/09–07/10 (8 días) | inicio, fin y minutos por concepto |
| `datos/intermedios/resumen_app_transcrito.csv` | 43 | sep–oct | Totales y métricas que da la app (para validar) |
| `datos/limpios/*.csv` | — | — | Generados por `01_limpieza.ipynb` (ver `diccionario_de_datos.md`) |

## 4. Calidad de los datos

**Cómo se comprobó la transcripción:** sumando los viajes transcritos y comparándolos con los totales que muestra la propia app.

| Comprobación | App | Transcrito | ¿Cuadra? |
|---|---|---|---|
| Septiembre, viajes pagados en la app | 1.620,42 € | 1.620,42 € | ✔ exacto |
| Septiembre, viajes en efectivo | 122,61 € | 122,61 € | ✔ exacto |
| Octubre, viajes pagados en la app | 394,87 € | 394,87 € | ✔ exacto |
| Octubre, viajes en efectivo | 57,79 € | 57,79 € | ✔ exacto |
| Ganancia diaria 30/09, 1, 2, 5, 6 y 7 oct | ver app | suma de viajes − peajes + incentivos | ✔ los 6 días |
| Jornadas: inicio→fin + recarga + cuidado = tiempo total | ver app | — | ✔ los 8 días (±1 min de redondeo) |

**Problemas encontrados y resueltos**
- 25 fotos del historial se solapan: el mismo viaje sale en dos fotos seguidas → deduplicado (245 → 212 filas).
- 2 fotos movidas (IMG_7843 e IMG_7850): el OCR leyó mal horas e importes → corregidas a mano ampliando la foto original. Todas las correcciones están en `datos/intermedios/correcciones_manuales.csv`, con el motivo de cada una.
- 1 viaje con la parte de arriba cortada (01/10, Prioritario, 11,56 €): hora registrada como 08:00 aproximada.
- 1 viaje con el tipo de servicio tapado por un dedo (28/09 11:36, 6,55 €): tipo = «Desconocido».

**Huecos (lo que no hay)**
- **31/08**: solo están los viajes desde las 21:23 (la última foto acaba ahí). Ese día está **incompleto** y no se usa en los análisis diarios.
- **Horas trabajadas**: solo hay detalle de jornada de **8 de los 27 días** con viajes (28/09–07/10).
- **Ganancia diaria oficial**: solo 7 días.
- **Sin direcciones ni zonas**, **sin distancias**, **sin duración de cada viaje** (solo la hora de inicio), **sin datos de Uber**, **sin costes** (comisión, alquiler, energía).
- No hay viajes del 25/09 (viernes) ni de fines de semana: probablemente no se trabajó esos días (no se puede confirmar).

## 5. ¿Hay datos suficientes?

**Sí, para un análisis serio pero acotado**: 212 viajes reales en 27 días (casi 5 semanas) y 8 jornadas con horas, todo validado contra los totales de la app. Por eso **no se ha creado un dataset sintético**.

Lo que **no** se puede responder con estos datos (zonas, Uber, ganancia neta) se explica en `LIMITACIONES.md`, junto con cómo conseguir esos datos.

## 6. Preguntas de negocio: cuáles se pueden responder

| # | Pregunta | ¿Con datos reales? | Con qué |
|---|---|---|---|
| 1 | €/hora bruto y neto | **Bruto: sí, parcial** (8 días con horas). **Neto: no** (faltan costes) → tabla de escenarios | Jornadas + viajes |
| 2 | Días y franjas más rentables | **Sí** (franjas por hora de inicio del viaje; días laborables) | Viajes |
| 3 | Zonas/barrios | **No** (no hay direcciones). Solo aproximación: viajes «Airport» frente al resto | Tipo de servicio |
| 4 | Tiempo muerto y su coste | **Parcial** (8 días: recarga, tiempo sin clasificar, conducción no efectiva) | Jornadas |
| 5 | Plataforma frente a Uber | **No** (no hay datos de Uber). Se compara entre tipos de servicio de la plataforma | — |
| 6 | Propinas, cancelaciones, peajes | **Sí** (mensual y viajes a 0 €) | Finanzas + viajes |
| 7 | Cambios de horario | **Sí, con cautela** (deducido de 2 y 4) | Todo lo anterior |
| extra | Efectivo frente a app; tipos de servicio | **Sí** | Viajes |
