# LIMITACIONES

Qué **no** se puede concluir con estos datos, por qué, y cómo conseguir lo que falta. Ser honesto con las limitaciones es parte del trabajo de un analista: una cifra sin contexto puede llevar a una mala decisión.

## 1. Lo que no se pudo calcular

| Qué | Por qué no | Qué se hizo en su lugar |
|---|---|---|
| **Ganancia NETA por hora** (pregunta 1) | Las capturas no muestran la comisión de la plataforma, el reparto con la flota, el alquiler ni el coste de la energía. No sé si el importe de cada viaje ya descuenta la comisión. | Tabla de **escenarios hipotéticos** (qué neto saldría según el % que te quede y los costes fijos) y un archivo `parametros_costes.csv` para que pongas tus cifras reales. |
| **Zonas o barrios más rentables** (pregunta 3) | El historial no muestra direcciones, origen ni destino. | Solo la aproximación «viajes de aeropuerto» (tipo VTC Airport) frente al resto. |
| **Plataforma frente a Uber** (pregunta 5) | No hay ningún dato de Uber. | Comparación entre los tipos de servicio de la plataforma. |
| **Tiempo exacto sin pasajero** (pregunta 4) | No hay duración de cada viaje ni hora de fin; solo la hora de inicio. La «conducción efectiva» de la flota probablemente incluye el trayecto vacío hasta recoger al pasajero. | Desglose de la jornada de la flota (recarga, cuidado, conducción no efectiva, minutos sin clasificar) y minutos entre inicios de viajes. |
| **Motivo de los viajes a 0 €** | La app no lo dice. La tasa de finalización (4 «cancelaciones forzosas del pasajero» en la última semana) sugiere que son cancelaciones, pero no se puede confirmar viaje a viaje. | Se tratan como «sin ingreso, probable cancelación». |
| **Significado de los viajes de 6 € exactos** | Pueden ser la tarifa mínima o una compensación por cancelación (hay alguno pagado en efectivo, lo que apunta a tarifa mínima). | Se marcan con `importe_6_exactos` y no se interpretan más. |
| **«Pagado a bordo»** (171,33 € en sep, 81 € en oct) | La app no explica el concepto y no coincide con los viajes en efectivo. | Se transcribe, pero no se usa. |

## 2. Tamaño de muestra (¿cuánto fiarse de cada cifra?)

| Cifra | Base | Fiabilidad |
|---|---|---|
| Ingresos por día, por viaje, % de viajes a 0 € | 204 viajes, 26 días | **Buena** para este periodo |
| **€ por hora** | **Solo 7 jornadas** (28/09–07/10) | **Media**: IC 95 % de 11,2 a 14,7 €/h. Puede que esas dos semanas no representen bien el resto. |
| Franjas horarias | 7–26 días por franja | Buena de 7 a 10 h; **débil a las 6 y a las 12 h** (horas incompletas y menos días) |
| Días de la semana | 4–6 días por día | **Débil**: los intervalos de confianza se solapan; no hay un día ganador demostrado |
| Mapa día × hora | 4–6 días por casilla | **Muy débil**: solo para ver patrones |
| La noche del 31/08 | **1 sola noche** (y además incompleta) | **Anecdótica**: sirve para proponer un experimento, no para concluir |
| Tipos de servicio con menos de 7 viajes | 1–3 viajes | **No interpretable** |

Además, todo el periodo son **5 semanas de septiembre–octubre**: no recoge la estacionalidad (verano, Navidad, eventos, lluvia…).

## 3. Decisiones que pueden cambiar los resultados

- **02/10 excluido del €/hora.** La sesión de la flota duró de 6:30 a 18:06, pero el último viaje empezó a las 11:33 y la conducción efectiva fue normal (5 h 2 min). Lo interpreté como una jornada que no se cerró. Si de verdad trabajaste hasta las 18:06, el €/hora baja de 13,09 a 11,70 €.
- **31/08 excluido de los análisis por día**, porque solo se capturaron sus viajes desde las 21:23.
- **«Ingreso» = importe del historial**, que incluye propinas (4 € en total) y peajes (11 € en total, que en realidad son un reembolso). Su efecto es menor del 1 %.
- **Hora del viaje = hora que muestra el historial.** No sé si es la hora de aceptación, de recogida o de fin. Para las franjas horarias asumo que es aproximadamente el inicio.
- **«Sin clasificar» = esperas.** Son los minutos de la sesión que la app de la flota no asigna a nada. La interpretación como esperas con el coche parado es mía.
- **Coste del tiempo muerto = coste de oportunidad máximo.** Supone que habría demanda para llenar ese tiempo, cosa que no está garantizada.

## 4. Riesgos de la transcripción

- Los datos vienen de **fotos de la pantalla**, no de una exportación. Se leyeron con OCR y se revisaron a mano **las 25 fotos del historial**. Los totales cuadran **al céntimo** con la app (septiembre y octubre, por app y en efectivo), así que el riesgo de error en importes es muy bajo.
- Hay **errores posibles que no detectaría la suma**: una hora mal leída o un tipo de servicio confundido en una foto movida (IMG_7843: la hora 08:17 podría ser 08:47).
- **1 viaje con hora aproximada** (01/10, registrado a las 08:00; la hora real está entre 07:33 y 08:33).
- **1 viaje con el tipo de servicio desconocido** (28/09 11:36, tapado por un dedo).
- Es posible que falten viajes **anteriores al 31/08 21:23** (la última foto acaba ahí).

## 5. Cómo conseguir los datos que faltan

1. **Solicitud RGPD a la plataforma** (derecho de acceso, art. 15, y de portabilidad, art. 20 del Reglamento General de Protección de Datos). Desde la app o el centro de ayuda, pide «una copia de todos mis datos personales como conductor en formato electrónico estructurado (CSV/JSON)»: historial completo con fechas, horas de inicio y fin, distancia, duración, zonas de origen y destino, importes y cancelaciones. Tienen 1 mes para responder (ampliable). Haz lo mismo con **Uber** si trabajas con ella («Descargar tus datos» en la web de conductores).
2. **App de la flota**: exporta o fotografía el «Detalle de jornada» de **todos** los días, no solo de 8.
3. **Costes**: tu nómina o liquidación semanal de la flota (qué porcentaje te queda), recibos de alquiler o leasing y coste de las recargas. Rellena `parametros_costes.csv`.
4. **Registro manual** (si no hay exportaciones): una hoja con una fila por jornada: fecha, hora de conexión y desconexión, ingresos del día, kWh o litros, coste, incidencias. Con 4–6 semanas ya mejora mucho el análisis.
5. **Para la pregunta de zonas**: aunque no tengas direcciones exactas, apunta el **barrio** o la zona de cada recogida (nunca la dirección exacta del pasajero).
