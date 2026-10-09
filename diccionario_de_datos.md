# Diccionario de datos

> **Qué es un diccionario de datos:** la «ficha técnica» de cada tabla: qué significa cada columna, de qué tipo es y de dónde sale. Sirve para que cualquiera (incluido tú dentro de 6 meses) entienda los datos sin adivinar.

Todas las tablas están en `datos/limpios/`, en CSV (UTF-8, separador coma, **punto** decimal). Las genera `01_limpieza.ipynb`. Moneda: euros. Zona horaria: Europe/Madrid (UTC+2 en todo el periodo).

## `viajes_limpios.csv` — 1 fila = 1 viaje (212 filas)

| Columna | Tipo | Descripción |
|---|---|---|
| `id_viaje` | texto | Identificador inventado por orden cronológico (V001…V212). No es el ID de la plataforma. |
| `fecha_hora` | fecha-hora ISO 8601 con zona | Momento del viaje según el historial (p. ej. `2026-10-07T10:37:00+0200`). Probablemente la hora de inicio o de aceptación; la app no lo aclara. |
| `fecha` | texto AAAA-MM-DD | Día del viaje. |
| `hora` | texto HH:MM | Hora del viaje. |
| `mes` | texto AAAA-MM | Mes. |
| `semana_iso` | entero | Semana del año (de lunes a domingo, norma ISO). 36 = 31/08–06/09 … 41 = 05/10–11/10. |
| `num_dia_semana` | entero 0–6 | 0 = lunes … 6 = domingo. |
| `dia_semana` | texto | lunes, martes… |
| `hora_del_dia` | entero 0–23 | Hora en punto del viaje (8 = de 08:00 a 08:59). |
| `franja_horaria` | texto | La misma hora como rango («08:00-08:59»). |
| `producto` | texto | Tipo de servicio de la plataforma: VTC, VTC Airport, VTC Eco, VTC Prioritario, VTC Promo, Electric, Envíos en coche, Desconocido (1 viaje con el tipo tapado en la foto). |
| `importe_eur` | decimal | «Ganancia total del viaje» que muestra el historial. Incluye propinas y peajes. 0 = viaje sin ingreso. |
| `metodo_pago` | texto | `app` o `efectivo` (según el icono de la fila). |
| `sin_ingreso` | booleano | `True` si `importe_eur` = 0 (probable cancelación; la app no lo explica). |
| `importe_6_exactos` | booleano | `True` si `importe_eur` = 6,00 (parece un importe mínimo). |
| `es_aeropuerto` | booleano | `True` si `producto` = VTC Airport. |
| `dia_completo` | booleano | `False` solo para el 31/08 (solo se capturó desde las 21:23). |
| `hora_aproximada` | booleano | `True` en 1 viaje (01/10) cuya hora salía cortada: se registró 08:00. |
| `atipico_iqr` | booleano | `True` si el importe es atípico según la regla del rango intercuartílico (> 28,56 €). Marcado, no borrado. |
| `min_hasta_siguiente` | decimal | Minutos hasta el siguiente viaje del mismo día (vacío en el último del día). |
| `origen_dato` | texto | `ocr`, `ocr + corrección manual` o `transcripción manual`. |
| `imagenes_origen` | texto | Foto(s) donde aparece el viaje (IMG_xxxx; separadas por `;`). |

## `jornadas_limpias.csv` — 1 fila = 1 jornada con horas (8 filas)

Fuente: app de la flota, «Detalle de jornada» (28/09–07/10).

| Columna | Tipo | Descripción |
|---|---|---|
| `fecha` | texto | Día. |
| `inicio`, `fin` | texto HH:MM | Inicio y fin de la sesión según la app de la flota. |
| `conduccion_efectiva_min` | entero | Minutos de «conducción efectiva» (definición de la flota; no se sabe si incluye los trayectos vacíos hasta el pasajero). |
| `tareas_adicionales_min` | entero | Siempre 0 en estos datos. |
| `recarga_electrica_min` | entero | Minutos cargando el coche. |
| `cuidado_vehiculo_min` | entero | «Cuidado básico del vehículo» (+10 min fijos cada día). |
| `conduccion_no_efectiva_min` | entero | Conduciendo sin estar disponible para viajes. |
| `descansos_min` | entero | Siempre 0 en estos datos. |
| `tiempo_total_app_min` | entero | «Tiempo total» de la app = (fin − inicio) + recarga + cuidado (comprobado). |
| `duracion_sesion_min` | entero | Calculado: fin − inicio. |
| `tiempo_efectivo_min` | entero | Calculado: conducción efectiva + tareas + recarga + cuidado («tiempo efectivo» de la app). |
| `sin_clasificar_min` | entero | Calculado: sesión − conducción efectiva − no efectiva − descansos. Minutos que la app no asigna (probablemente esperas con el coche parado). |
| `total_recalculado_min`, `dif_vs_app_min` | entero | Control: el total recalculado frente al de la app (diferencia ≤ 1 min). |
| `ultimo_viaje` | texto HH:MM | Hora del último viaje del día (del historial de la plataforma). |
| `jornada_anomala` | booleano | `True` el 02/10: la sesión dura más de 1,5 veces la mediana (probable jornada no cerrada). |
| `dia_semana` | texto | Día de la semana. |

## `resumen_diario.csv` — 1 fila = 1 día con viajes (27 filas)

| Columna | Descripción |
|---|---|
| `fecha`, `dia_semana`, `semana_iso` | Día. |
| `n_viajes`, `n_sin_ingreso` | Nº de viajes y cuántos fueron de 0 €. |
| `ingresos_eur` | Suma de `importe_eur` del día. |
| `primer_viaje`, `ultimo_viaje` | Hora del primer y del último viaje. |
| `ventana_actividad_h` | Horas entre el primer y el último viaje (aproximación de la jornada cuando no hay datos de la flota). |
| `dia_completo` | `False` para el 31/08. |
| `tiempo_total_app_min`, `tiempo_efectivo_min`, `conduccion_efectiva_min`, `jornada_anomala` | De la flota (solo 8 días; vacío en el resto). |
| `tiene_horas_flota` | `True` si hay datos de la flota ese día. |

## `resumen_app.csv` — totales oficiales transcritos (43 filas)

Formato «largo»: cada fila es una cifra. Columnas: `fuente` (app_finanzas, app_perfil, flota_turnos), `concepto` (ganancia_diaria, peajes, propinas, valoracion_media_ult_100…), `periodo` (día, semana o mes), `valor`, `unidad`, `imagen`, `nota`.

## `registro_cambios.csv` — trazabilidad de la limpieza

Cada fila es un cambio: `paso`, `accion` (corregir, eliminar, añadir, marcar…), `detalle` (qué fila y qué valores), `motivo`, `filas_afectadas`.

## `metricas_clave.json`

Las cifras clave que calcula `02_analisis.ipynb` (€/hora, medias, franjas…). Las usan el informe, el dashboard y el control de calidad.

## Glosario de los tipos de servicio

| Producto | Qué es (según el nombre; la plataforma no lo detalla en las capturas) |
|---|---|
| VTC | Servicio estándar |
| VTC Airport | Viajes con origen o destino en el aeropuerto |
| VTC Eco | Versión más económica |
| VTC Prioritario | El pasajero paga más por una asignación más rápida |
| VTC Promo | Viaje con promoción para el pasajero |
| Electric | El pasajero pide un vehículo eléctrico |
| Envíos en coche | Envío de paquetes |
