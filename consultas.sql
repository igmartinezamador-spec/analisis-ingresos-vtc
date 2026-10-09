-- =====================================================================
-- consultas.sql — Las consultas clave del proyecto VTC, en SQL (SQLite)
-- =====================================================================
-- Cómo ejecutarlas:   python3 scripts/ejecutar_sql.py
--   (crea datos/vtc.sqlite a partir de datos/limpios/*.csv y ejecuta cada consulta)
-- También puedes abrir datos/vtc.sqlite con DB Browser for SQLite o DBeaver y pegarlas.
--
-- Tablas:
--   viajes     -> 1 fila por viaje (datos/limpios/viajes_limpios.csv)
--   jornadas   -> 1 fila por jornada con horas de la flota (8 filas)
--   dias       -> 1 fila por día con viajes (resumen_diario.csv)
--   app        -> totales oficiales de la app (resumen_app.csv)
--
-- Notas de SQLite: los booleanos se guardan como 1/0 (True/False);
-- ROUND(x, 2) redondea a 2 decimales; || concatena texto.
-- Cada consulta empieza por una línea "-- @nombre:" que usa el script.
-- =====================================================================


-- @q01_panorama: Panorama general (solo días completos: excluye la noche del 31/08)
-- COUNT(*) cuenta filas; COUNT(DISTINCT x) cuenta valores distintos; SUM suma.
SELECT COUNT(DISTINCT fecha)                              AS dias_trabajados,
       COUNT(*)                                           AS viajes,
       ROUND(SUM(importe_eur), 2)                         AS ingresos_eur,
       ROUND(SUM(importe_eur) / COUNT(DISTINCT fecha), 2) AS ingreso_medio_dia,
       ROUND(AVG(CASE WHEN importe_eur > 0 THEN importe_eur END), 2) AS ticket_medio_con_ingreso
FROM viajes
WHERE dia_completo = 1;


-- @q02_validacion_app: Validación — la suma de viajes debe coincidir con la app (pago app / efectivo)
-- Un JOIN une dos tablas por una columna común. Aquí: mes + método de pago.
SELECT v.mes,
       v.metodo_pago,
       ROUND(SUM(v.importe_eur), 2)                AS suma_viajes,
       a.valor                                     AS total_app,
       ROUND(SUM(v.importe_eur) - a.valor, 2)      AS diferencia
FROM viajes v
JOIN app a
  ON a.periodo = v.mes
 AND a.concepto = CASE v.metodo_pago WHEN 'app' THEN 'viajes_pago_app' ELSE 'viajes_efectivo' END
GROUP BY v.mes, v.metodo_pago, a.valor
ORDER BY v.mes, v.metodo_pago;


-- @q03_euros_por_hora: Pregunta 1 — € por hora en las jornadas con horas (sin la jornada anómala del 02/10)
-- Cociente de sumas: total de euros ÷ total de horas (no la media de los cocientes).
SELECT COUNT(*)                                                         AS jornadas,
       ROUND(SUM(d.ingresos_eur), 2)                                    AS ingresos_eur,
       ROUND(SUM(j.tiempo_total_app_min) / 60.0, 2)                     AS horas_totales,
       ROUND(SUM(d.ingresos_eur) / (SUM(j.tiempo_total_app_min) / 60.0), 2) AS eur_por_hora_total,
       ROUND(SUM(d.ingresos_eur) / (SUM(j.tiempo_efectivo_min) / 60.0), 2)  AS eur_por_hora_efectiva
FROM jornadas j
JOIN dias d ON d.fecha = j.fecha
WHERE j.jornada_anomala = 0;


-- @q04_euros_hora_por_jornada: Pregunta 1 — detalle por jornada
SELECT j.fecha,
       j.dia_semana,
       d.n_viajes,
       d.ingresos_eur,
       ROUND(j.tiempo_total_app_min / 60.0, 2)                    AS horas_totales,
       ROUND(d.ingresos_eur / (j.tiempo_total_app_min / 60.0), 2) AS eur_por_hora,
       j.jornada_anomala
FROM jornadas j
JOIN dias d ON d.fecha = j.fecha
ORDER BY j.fecha;


-- @q05_dia_semana: Pregunta 2 — ingreso medio por día de la semana (días completos)
-- Subconsulta: primero sumo por día y luego hago la media por día de la semana.
SELECT dia_semana,
       COUNT(*)                   AS dias,
       ROUND(AVG(ingresos), 1)    AS ingreso_medio_dia,
       ROUND(MIN(ingresos), 1)    AS minimo,
       ROUND(MAX(ingresos), 1)    AS maximo
FROM (SELECT fecha, dia_semana, num_dia_semana, SUM(importe_eur) AS ingresos
      FROM viajes
      WHERE dia_completo = 1
      GROUP BY fecha, dia_semana, num_dia_semana) AS por_dia
GROUP BY dia_semana, num_dia_semana
ORDER BY num_dia_semana;


-- @q06_franjas: Pregunta 2 — € y viajes por hora de inicio (totales y % de viajes a 0 €)
-- (El € por HORA TRABAJADA de cada franja necesita saber qué horas estuviste activo; está en 02_analisis.ipynb.)
SELECT franja_horaria,
       COUNT(*)                                     AS viajes,
       COUNT(DISTINCT fecha)                        AS dias_con_viajes,
       ROUND(SUM(importe_eur), 2)                   AS ingresos_eur,
       ROUND(SUM(importe_eur) / COUNT(DISTINCT fecha), 2) AS eur_por_dia_con_viajes,
       ROUND(100.0 * SUM(sin_ingreso) / COUNT(*), 1) AS pct_viajes_0_eur
FROM viajes
WHERE dia_completo = 1
GROUP BY franja_horaria
ORDER BY franja_horaria;


-- @q07_aeropuerto: Pregunta 3 (aproximación a «zonas») — aeropuerto frente al resto
SELECT CASE WHEN es_aeropuerto = 1 THEN 'Aeropuerto' ELSE 'Resto' END AS tipo,
       COUNT(*)                                                  AS viajes,
       ROUND(AVG(CASE WHEN importe_eur > 0 THEN importe_eur END), 2) AS importe_medio_sin_ceros,
       ROUND(100.0 * SUM(importe_eur) / (SELECT SUM(importe_eur) FROM viajes WHERE dia_completo = 1), 1) AS pct_ingresos
FROM viajes
WHERE dia_completo = 1
GROUP BY tipo;


-- @q08_tiempo_muerto: Pregunta 4 — desglose medio de la jornada (minutos por día, 7 jornadas normales)
SELECT ROUND(AVG(conduccion_efectiva_min), 1)    AS conduccion_efectiva,
       ROUND(AVG(recarga_electrica_min), 1)      AS recarga,
       ROUND(AVG(cuidado_vehiculo_min), 1)       AS cuidado,
       ROUND(AVG(conduccion_no_efectiva_min), 1) AS no_efectiva,
       ROUND(AVG(sin_clasificar_min), 1)         AS sin_clasificar,
       ROUND(AVG(recarga_electrica_min + cuidado_vehiculo_min + conduccion_no_efectiva_min + sin_clasificar_min), 1) AS total_sin_conduccion_efectiva,
       ROUND(AVG(tiempo_total_app_min), 1)       AS tiempo_total
FROM jornadas
WHERE jornada_anomala = 0;


-- @q09_tipos_servicio: Pregunta 5 (alternativa, no hay Uber) — tipos de servicio de la plataforma
SELECT producto,
       COUNT(*)                                                     AS viajes,
       ROUND(SUM(importe_eur), 2)                                   AS ingresos_eur,
       ROUND(AVG(CASE WHEN importe_eur > 0 THEN importe_eur END), 2) AS importe_medio_sin_ceros,
       ROUND(100.0 * SUM(sin_ingreso) / COUNT(*), 1)               AS pct_viajes_0_eur
FROM viajes
WHERE dia_completo = 1
GROUP BY producto
ORDER BY viajes DESC;


-- @q10_cancelaciones_minimos: Pregunta 6 — viajes a 0 € y de 6 € exactos
SELECT COUNT(*)                                          AS viajes,
       SUM(sin_ingreso)                                  AS viajes_0_eur,
       ROUND(100.0 * SUM(sin_ingreso) / COUNT(*), 1)     AS pct_0_eur,
       SUM(importe_6_exactos)                            AS viajes_6_eur,
       ROUND(100.0 * SUM(importe_6_exactos) / COUNT(*), 1) AS pct_6_eur
FROM viajes
WHERE dia_completo = 1;


-- @q11_propinas_peajes_incentivos: Pregunta 6 — conceptos extra según la app
SELECT periodo, concepto, valor
FROM app
WHERE concepto IN ('propinas', 'peajes', 'incentivos', 'ganancia_mensual')
ORDER BY periodo, concepto;


-- @q12_semanas: Ingresos por semana ISO (con nº de días trabajados, para no comparar semanas desiguales)
SELECT semana_iso,
       MIN(fecha)                                         AS desde,
       MAX(fecha)                                         AS hasta,
       COUNT(DISTINCT fecha)                              AS dias,
       COUNT(*)                                           AS viajes,
       ROUND(SUM(importe_eur), 2)                         AS ingresos_eur,
       ROUND(SUM(importe_eur) / COUNT(DISTINCT fecha), 2) AS eur_por_dia
FROM viajes
WHERE dia_completo = 1
GROUP BY semana_iso
ORDER BY semana_iso;


-- @q13_efectivo_vs_app: Extra — efectivo frente a pago en la app
SELECT metodo_pago,
       COUNT(*)                   AS viajes,
       ROUND(AVG(importe_eur), 2) AS importe_medio,
       ROUND(SUM(importe_eur), 2) AS total_eur
FROM viajes
WHERE dia_completo = 1
GROUP BY metodo_pago;


-- @q14_ventana_funcion_ventana: Extra (para practicar funciones de ventana) — tiempo entre viajes consecutivos
-- LAG(x) OVER (PARTITION BY fecha ORDER BY fecha_hora) = valor de x en la fila anterior del mismo día.
-- julianday() convierte una fecha-hora a días; × 24 × 60 = minutos.
SELECT fecha,
       hora,
       producto,
       importe_eur,
       ROUND((julianday(substr(fecha_hora, 1, 19)) -
              julianday(LAG(substr(fecha_hora, 1, 19)) OVER (PARTITION BY fecha ORDER BY fecha_hora))) * 24 * 60) AS min_desde_anterior
FROM viajes
WHERE fecha = '2026-10-07'
ORDER BY fecha_hora;
