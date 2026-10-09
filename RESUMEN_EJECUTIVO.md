# Resumen ejecutivo · ¿Cómo gano más por hora conduciendo en VTC?

**Datos:** 212 viajes reales de la plataforma (31/08–07/10/2026) y 8 jornadas con horas de la app de la flota, extraídos de 55 fotos de la pantalla y **validados al céntimo** con los totales de la app. Sin datos de Uber, de zonas ni de costes.

## Hallazgos

| | Cifra | Base (n) |
|---|---|---|
| Ingreso medio por día trabajado | **84 €** (IC 95 %: 78–91 €); 7,8 viajes/día | 26 días |
| **€ brutos por hora de jornada** | **13,1 €/h** (IC 95 %: 11,2–14,7); 15,4 €/h sobre el tiempo «efectivo» | 7 jornadas |
| Mejor franja | **08:00–08:59: 22 € por hora trabajada**; de 7:00 a 9:59, entre 18 y 22 € | 24–26 días |
| Tramo final (de 11:00 al cierre, ~1 h 38 min/día) | **solo 6 €/día ≈ 3,9 €/h**, frente a 18 €/h antes de las 11 | 7 jornadas |
| Tiempo sin conducción efectiva | **~1 h 49 min por jornada (26 %)**: 56 min sin clasificar (esperas), 35 min de recarga, 10 de cuidado y 7 de conducción no efectiva | 7 jornadas |
| Viajes que no dejan dinero | **15 % a 0 €** (probables cancelaciones) y **13 % en el mínimo de 6 €** | 204 viajes |
| Aeropuerto | Viaje medio de **17,39 €** frente a 11,86 € del resto: +47 %. Es el 13 % de los viajes y el 19 % de los ingresos | 27 viajes |
| Día de la semana | Miércoles (95 €) y lunes (92 €) por encima de jueves y viernes (75–76 €), **pero los intervalos se solapan: no concluyente** | 4–6 días por día |
| Propinas + incentivos | < 1 % de la ganancia (4 € y 11 € en 5 semanas) | app |

## 3 recomendaciones accionables

1. **Revisa el tramo de 11:00 al cierre de la sesión.** En las 7 jornadas medidas, esos ~98 minutos diarios solo dejaron 6 € de media (el 8 % de los ingresos de todo el periodo viene de viajes que empiezan después de las 11:00). Si ese tiempo no es obligatorio (devolver el coche, recargar), **cerrar hacia las 11:00** subiría tu €/hora de jornada de **13,1 a ~15,8 €**, perdiendo unos 6 € al día. Esas horas rendirían más en otra franja.
2. **Saca la recarga de las horas fuertes y reduce las esperas.** Las horas de 7:00 a 9:59 rinden 18–22 €/h. Si recargas (35 min/día de media), hazlo **antes de las 6:30 o después de las 11:00**. Los 56 min/día «sin clasificar» (coche parado) son el mayor hueco: prueba a esperar cerca de los puntos que generan viajes de aeropuerto (+47 % por viaje).
3. **Haz un experimento con la noche, midiéndolo.** La única noche registrada (lunes 31/08, 21:23–23:26) dejó 84 € en 8 viajes: unos 41 €/h de ventana de actividad, frente a una mediana de 20 €/h por la mañana. **Es un solo día y no prueba nada**, pero merece la pena: 4–6 noches (por ejemplo de 20:00 a 24:00) en lugar del tramo final de la mañana, apuntando las horas de conexión y comparando el €/hora con el mismo método.

## Qué datos mejorarían el análisis

- **Costes reales** (qué % te queda tras comisión y reparto con la flota, alquiler, energía) → para pasar de €/hora **bruto a neto**. Hay una plantilla: `parametros_costes.csv`.
- **Horas de todas las jornadas** (no solo de 8) → €/hora más fiable y por día de la semana.
- **Exportación RGPD de la plataforma** (y de Uber si la usas): zonas de origen y destino, duración y distancia de cada viaje → preguntas de zonas, tiempo sin pasajero y comparación entre plataformas.
- **Más semanas** (idealmente 3 meses) → efecto de la estacionalidad y diferencias entre días de la semana con confianza.

*Detalle y método: `README.md`, `02_analisis.ipynb` y `LIMITACIONES.md`.*
