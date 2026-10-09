# Guía: monta tu panel en Power BI en 10 pasos

No se puede generar un `.pbix` desde aquí (Power BI Desktop solo funciona en Windows y es una aplicación gráfica). Los datos limpios ya están listos en `datos/limpios/`. En el bootcamp verás Power BI: esta guía te sirve de práctica.

> **Si usas Mac:** Power BI Desktop no existe para macOS. Opciones: una máquina virtual con Windows (Parallels), un ordenador con Windows o **Power BI en el navegador** (app.powerbi.com: permite crear informes a partir de un CSV subido, pero eso sube tus datos a la nube de Microsoft. Están anonimizados, pero decide tú).

**Archivos que vas a usar**
- `datos/limpios/viajes_limpios.csv` (tabla de hechos: 1 fila por viaje)
- `datos/limpios/jornadas_limpias.csv` (8 jornadas con horas)
- `datos/limpios/resumen_diario.csv` (1 fila por día)

---

### Paso 1 · Importar los CSV
*Inicio → Obtener datos → Texto/CSV* → elige `viajes_limpios.csv`. En la vista previa comprueba que el **origen del archivo es UTF-8** (las tildes se ven bien) y el **delimitador es la coma**. Pulsa **Transformar datos** (no «Cargar»): así entras en Power Query. Repite con `jornadas_limpias.csv` y `resumen_diario.csv`.

### Paso 2 · Revisar los tipos en Power Query
Los CSV usan **punto decimal**. Si tu Windows está en español, Power BI puede leer `23.37` como texto o como 2337. Para evitarlo: clic derecho en la columna `importe_eur` → *Cambiar tipo → Usar configuración regional…* → Número decimal, **Inglés (Estados Unidos)**. Pon también:
- `fecha` → Fecha · `fecha_hora` → Fecha/hora/zona horaria
- `sin_ingreso`, `dia_completo`, `es_aeropuerto`, `jornada_anomala` → Verdadero/Falso
- `hora_del_dia`, `semana_iso`, `num_dia_semana` → Número entero

Pulsa **Cerrar y aplicar**.

### Paso 3 · Crear una tabla de calendario
*Modelado → Nueva tabla*:
```DAX
Calendario = ADDCOLUMNS(
    CALENDAR(DATE(2026, 8, 31), DATE(2026, 10, 11)),
    "Semana", WEEKNUM([Date], 21),
    "DiaSemana", FORMAT([Date], "dddd"),
    "NumDia", WEEKDAY([Date], 2)
)
```
Selecciona la tabla y márcala como tabla de fechas (*Herramientas de tabla → Marcar como tabla de fechas → columna Date*).

### Paso 4 · Relacionar las tablas (modelo en estrella)
En la vista **Modelo** arrastra:
- `Calendario[Date]` → `viajes_limpios[fecha]` (uno a varios)
- `Calendario[Date]` → `jornadas_limpias[fecha]` (uno a varios)
- `Calendario[Date]` → `resumen_diario[fecha]` (uno a varios)

> **Modelo en estrella:** una tabla central de *hechos* (los viajes) y tablas de *dimensiones* alrededor (el calendario) con las que filtras. Es la forma estándar de organizar datos en Power BI.

### Paso 5 · Crear las medidas (DAX)
En `viajes_limpios`, *Nueva medida*, una por una:
```DAX
Ingresos = SUM(viajes_limpios[importe_eur])
Viajes = COUNTROWS(viajes_limpios)
Dias trabajados = DISTINCTCOUNT(viajes_limpios[fecha])
Ingreso medio por dia = DIVIDE([Ingresos], [Dias trabajados])
% viajes a 0 = DIVIDE(CALCULATE([Viajes], viajes_limpios[sin_ingreso] = TRUE()), [Viajes])
Importe medio con ingreso = CALCULATE(AVERAGE(viajes_limpios[importe_eur]), viajes_limpios[importe_eur] > 0)
```
Y en `jornadas_limpias`:
```DAX
Horas jornada = DIVIDE(CALCULATE(SUM(jornadas_limpias[tiempo_total_app_min]), jornadas_limpias[jornada_anomala] = FALSE()), 60)
Euros por hora =
VAR fechas = CALCULATETABLE(VALUES(jornadas_limpias[fecha]), jornadas_limpias[jornada_anomala] = FALSE())
RETURN DIVIDE(CALCULATE([Ingresos], TREATAS(fechas, viajes_limpios[fecha])), [Horas jornada])
```
Comprueba que **Euros por hora** da **13,09** sin filtros (igual que el cuaderno y el Excel). Si no coincide, algo está mal: es tu control de calidad.

### Paso 6 · Tarjetas de KPI
Inserta 5 objetos visuales **Tarjeta** con: Ingresos, Dias trabajados, Ingreso medio por dia, Euros por hora y % viajes a 0. Formato: euros con 2 decimales y porcentaje con 1.

### Paso 7 · Gráficos principales
- **Columnas agrupadas**: eje X = `Calendario[Date]`, valor = Ingresos (ingresos por día).
- **Columnas**: eje X = `franja_horaria`, valor = Ingresos (o Viajes).
- **Barras**: eje Y = `producto`, valor = Importe medio con ingreso, ordenado de mayor a menor.
- **Barras apiladas** con `jornadas_limpias`: eje Y = fecha; valores = conducción efectiva, recarga, cuidado, no efectiva y sin clasificar.

**Pon como título de cada gráfico la conclusión** (p. ej. «La franja de 8 a 9 es la que más rinde»), no «Ingresos por franja».

### Paso 8 · Segmentaciones (filtros)
Inserta **Segmentaciones** con: `Calendario[Semana]`, `Calendario[DiaSemana]`, `viajes_limpios[producto]` y `viajes_limpios[metodo_pago]`. Añade un filtro de página con `dia_completo = Verdadero` (para excluir la noche incompleta del 31/08).

### Paso 9 · Ordenar los días de la semana
Por defecto Power BI los ordena alfabéticamente (domingo, jueves, lunes…). Selecciona `Calendario[DiaSemana]` → *Herramientas de columna → Ordenar por columna → NumDia*.

### Paso 10 · Revisar y publicar
- Comprueba con los filtros que las cifras cuadran con el dashboard HTML (p. ej., semana 40: 435 € en 5 días).
- Añade un cuadro de texto con las **limitaciones** (8 jornadas con horas, sin costes, sin Uber).
- Guarda como `panel_vtc.pbix`. Publicar en la web es opcional: si lo haces, **revisa que no haya datos personales** (no los hay en estos CSV).

**Reto extra:** recrea en DAX el «€ por hora trabajada según la franja horaria» (pista: necesitas, para cada día, la hora del primer y del último viaje).
