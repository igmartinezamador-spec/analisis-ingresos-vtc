# Guía de aprendizaje — tu primer proyecto de Data Analytics, paso a paso

Esta guía explica **qué se hizo, por qué y cómo**, en español sencillo, para que puedas repetirlo tú solo. Cada término técnico se explica la primera vez que aparece y está en el **glosario** del final.

**Cómo usarla:** lee una sección, abre el archivo que se menciona y ejecuta las celdas tú mismo. Al final hay **10 ejercicios** para repetir partes del análisis. Las soluciones están al final de todo: inténtalo antes de mirarlas.

---

## 0. El mapa del proyecto

Todo proyecto de datos sigue más o menos el mismo camino:

```
 1. Pregunta  →  2. Datos  →  3. Limpieza  →  4. Análisis  →  5. Comunicación
 (¿qué quiero     (inventario,   (dejarlos        (resúmenes,      (gráficos, informe,
  saber?)          extracción)    fiables)         comparaciones)   recomendaciones)
```

En este proyecto:

| Etapa | Qué hicimos | Dónde está |
|---|---|---|
| 1. Pregunta | 7 preguntas de negocio sobre tu €/hora | `INVENTARIO.md` §6 |
| 2. Datos | 55 fotos → OCR → tabla de viajes | `scripts/`, `datos/intermedios/` |
| 3. Limpieza | Correcciones, duplicados, tipos, validación | `01_limpieza.ipynb` |
| 4. Análisis | Estadística descriptiva por día, hora, tipo | `02_analisis.ipynb`, `consultas.sql` |
| 5. Comunicación | Gráficos, Excel, dashboard, resumen | `graficos/`, `analisis_vtc.xlsx`, `dashboard.html`, `RESUMEN_EJECUTIVO.md` |

> **Idea clave:** el análisis «bonito» (los gráficos) es la parte pequeña. Lo que hace fiable un proyecto son las etapas 2 y 3.

---

## 1. Empezar por las preguntas

Antes de tocar un dato se escriben las **preguntas de negocio**: lo que una persona quiere decidir. «¿Qué cambiaría en el horario para ganar más por hora?» es una buena pregunta porque lleva a una **decisión**.

Después se comprueba **cuáles se pueden responder** con los datos que hay. Aquí, 3 de las 7 no se podían responder del todo (neto, zonas, Uber). Decirlo claramente no es un fallo: es rigor.

---

## 2. Inventario y extracción de datos

### 2.1 Inventario
Un **inventario** es la lista de todo lo que tienes: archivos, qué contienen, qué periodo cubren, cuántas filas y qué falta. Ver `INVENTARIO.md`.

### 2.2 De fotos a tabla: OCR
**OCR** (*Optical Character Recognition*, reconocimiento óptico de caracteres) es convertir una imagen con texto en texto que el ordenador puede leer. Usamos el OCR que trae macOS, **en local**: ninguna foto salió de tu ordenador.

El OCR devuelve trozos de texto con su **posición** en la foto (`y` = altura). Como en el historial el importe está a la misma altura que el tipo de servicio, se pueden emparejar por posición: eso hace `scripts/extraer_viajes_ocr.py`.

### 2.3 Validar la extracción (¡lo más importante!)
El OCR se equivoca, sobre todo con fotos movidas («0B:47» en vez de «08:47»). Por eso:
1. **Revisión manual**: se miraron las 25 fotos del historial y se apuntó cada corrección, con su motivo, en `datos/intermedios/correcciones_manuales.csv`.
2. **Comprobación con totales independientes** (*checksum* o suma de control): la app dice que en septiembre cobraste 1.620,42 € por la app. Si la suma de los viajes transcritos da 1.620,42 €, la transcripción es buena. **Así se detectó un viaje duplicado** que la revisión a ojo no había visto: septiembre salía 12,18 € por encima.

> **Lección:** busca siempre un número «oficial» con el que cuadrar tus datos. Es la forma más barata de encontrar errores.

---

## 3. Limpieza de datos (`01_limpieza.ipynb`)

**Limpiar** es dejar los datos listos para analizar sin errores. Pasos típicos y cómo se hicieron aquí:

### 3.1 Tipos de datos
Cada columna tiene un **tipo**: texto, número entero, número decimal, fecha, booleano (verdadero/falso). Si la fecha es texto, no puedes ordenar por fecha ni sacar el día de la semana. En pandas:
```python
viajes["fecha_hora"] = pd.to_datetime(viajes.fecha + " " + viajes.hora)   # texto -> fecha-hora
```

### 3.2 Fechas y zona horaria
Una hora sin **zona horaria** es ambigua. Las 08:00 en Madrid en octubre son las 06:00 **UTC** (hora universal). Lo marcamos así:
```python
.dt.tz_localize("Europe/Madrid")
```
Importa cuando cruzas fuentes: muchas exportaciones (y las de Uber) vienen en UTC.

### 3.3 Duplicados
Un **duplicado** es el mismo registro repetido. Las fotos se solapaban, así que cada viaje del borde salía dos veces. Ojo: **dos filas iguales no siempre son un duplicado**. El 14/09 a las 09:13 hubo dos viajes Eco de 0 € reales. La regla usada: cuántas veces sale como máximo *dentro de la misma foto*.

### 3.4 Nulos (valores que faltan)
Un **nulo** (`NaN` en pandas) es una celda vacía. Opciones: recuperarlo de otra fuente (aquí, de la foto siguiente), dejarlo vacío y explicarlo, o eliminar la fila si no aporta. **Nunca inventarlo.**

### 3.5 Valores atípicos (*outliers*)
Un **atípico** es un valor muy alejado del resto. Se detectan con la regla del **rango intercuartílico (IQR)**:
- **Q1** (primer cuartil) = el valor que deja por debajo al 25 % de los datos. **Q3** = el que deja por debajo al 75 %.
- **IQR = Q3 − Q1**. Es atípico lo que está por encima de Q3 + 1,5·IQR (o por debajo de Q1 − 1,5·IQR).
- Aquí: Q1 = 7,46 €, Q3 = 15,90 €, así que es atípico lo que pasa de 28,56 €. Salen 6 viajes (como el de 45,12 € al aeropuerto).

**Se marcan, no se borran**: eran viajes reales. Borrar atípicos sin pensar es uno de los errores más comunes.

### 3.6 Moneda y decimales
En España se escribe «23,37 €» (coma decimal); Python y los CSV usan punto (23.37). Se convierte al leer. Problema típico: Excel o Power BI en español pueden leer mal «23.37». Ver el paso 2 de `GUIA_POWER_BI.md`.

### 3.7 Variables derivadas
Son columnas nuevas calculadas a partir de otras: día de la semana, hora del día, «¿es de 0 €?»… Permiten agrupar.

### 3.8 Registro de cambios
Cada cambio se apunta en `datos/limpios/registro_cambios.csv`. Así cualquiera puede **auditar** (revisar) qué se tocó y por qué. Esto es **trazabilidad**.

---

## 4. Análisis exploratorio (`02_analisis.ipynb`)

### 4.1 Agregar
**Agregar** es resumir muchas filas en pocas: «suma de importes **por día**». En pandas es `groupby`; en SQL, `GROUP BY`; en Excel, `SUMIFS` o una tabla dinámica:
```python
viajes.groupby("fecha").importe_eur.sum()        # pandas
```
```sql
SELECT fecha, SUM(importe_eur) FROM viajes GROUP BY fecha;   -- SQL
```

### 4.2 Estadística descriptiva
| Medida | Qué es | Ejemplo aquí |
|---|---|---|
| **Media** | Suma ÷ nº de casos | 84,45 € por día |
| **Mediana** | El valor del medio al ordenar | 84,99 € por día |
| **Percentiles (P25, P75)** | Valores que dejan por debajo el 25 % / 75 % | La mitad de los días está entre 72,92 € y 96,49 € |
| **Desviación típica** | Cuánto se alejan los datos de la media, de promedio | 17,44 € |
| **n** | Tamaño de la muestra | 26 días |

Si la media y la mediana se parecen (84 y 85), los datos son bastante **simétricos**. En los importes por viaje, la media (12,62 €) es mayor que la mediana (10,98 €) porque unos pocos viajes caros «tiran» de la media hacia arriba (distribución **asimétrica**).

### 4.3 Incertidumbre: el intervalo de confianza
Con 7 jornadas, 13,09 €/h no es «la verdad»: es una estimación. El **intervalo de confianza al 95 % (IC 95 %)** da el rango donde probablemente está el valor real si siguieras trabajando igual: **11,2 – 14,7 €/h**.

Se calculó con **bootstrap**: se cogen al azar 7 jornadas de entre las 7 (pudiendo repetir), se calcula el €/hora, y se repite 5.000 veces. El 2,5 % y el 97,5 % de esos resultados son los extremos del intervalo. No hace falta ninguna fórmula complicada, solo repetir.

**Regla práctica:** si los intervalos de dos grupos se solapan mucho, **no puedes decir que uno sea mejor**. Por eso no hay «mejor día de la semana».

### 4.4 Cómo promediar tasas (trampa clásica)
Para el €/hora de 7 días hay dos opciones:
- **Media de cocientes:** calcular el €/h de cada día y hacer la media.
- **Cociente de sumas:** total de € ÷ total de horas.

La correcta para «cuánto se gana por hora» es la **segunda**: si un día trabajas 2 h y otro 8 h, no pueden pesar igual.

### 4.5 Comparar con igual base
- Los **días de la semana** se comparan por **ingreso medio por día**, no por ingresos totales (hay 6 miércoles y solo 4 viernes).
- Las **franjas horarias**: € de esa hora ÷ días en que trabajaste a esa hora.
- La **noche del 31/08** solo se puede comparar con las mañanas usando la misma medida (ventana de actividad), y aun así es **un único dato**.

### 4.6 Correlación no es causa
Que los miércoles salgan más altos no significa que el miércoles «cause» más ingresos. Puede ser casualidad (pocos días) o por otra cosa (una semana con más viajes al aeropuerto). Para afirmar causas hace falta un **experimento**: por ejemplo, probar noches de forma planificada.

---

## 5. Visualización

Reglas que se aplicaron (y que te pedirán en el bootcamp):
1. **El título dice la conclusión**: «Las 8:00 son la hora que más rinde», no «Ingresos por hora».
2. **Subtítulo con qué se mide y n**.
3. **Un color por serie**, y un color de acento solo para lo que quieres destacar.
4. **Elige bien el tipo de gráfico**: barras para comparar categorías, línea para tendencias en el tiempo, histograma para distribuciones y mapa de calor para dos dimensiones.
5. **Nunca dos ejes Y en el mismo gráfico**: inventan correlaciones.
6. **Accesible**: colores distinguibles por personas daltónicas, etiquetas de texto y una tabla con los datos.

---

## 6. Las mismas preguntas en SQL (`consultas.sql`)

**SQL** es el lenguaje para consultar bases de datos. Lo usarás muchísimo. Equivalencias con pandas:

| Pandas | SQL | Qué hace |
|---|---|---|
| `df[df.x > 0]` | `WHERE x > 0` | Filtrar filas |
| `df.groupby("a").b.sum()` | `SELECT a, SUM(b) ... GROUP BY a` | Agregar |
| `df.merge(otra, on="k")` | `JOIN otra ON ...k = ...k` | Unir tablas |
| `df.sort_values("x")` | `ORDER BY x` | Ordenar |
| `df.x.nunique()` | `COUNT(DISTINCT x)` | Contar valores distintos |
| `df.groupby("f").x.shift(1)` | `LAG(x) OVER (PARTITION BY f ORDER BY ...)` | Fila anterior del mismo grupo (*función de ventana*) |

Ejecuta `python3 scripts/ejecutar_sql.py`: crea `datos/vtc.sqlite` y muestra cada resultado. **Comprueba que coinciden con el cuaderno**: si SQL y pandas dan lo mismo, tienes más confianza en el resultado.

---

## 7. Excel (`analisis_vtc.xlsx`)

- **Hoja Resumen**: todo con **fórmulas** (`SUMIFS`, `COUNTIFS`, `AVERAGEIFS`), no con números pegados. Si cambias un dato en la hoja Viajes, se recalcula todo.
  - `SUMIFS(lo_que_sumas; columna_criterio1; criterio1; ...)` = «suma si se cumplen estas condiciones». En Excel en español se llama `SUMAR.SI.CONJUNTO`.
- **Tablas dinámicas** (hojas TD_…): resúmenes que se reorganizan arrastrando campos. Es el `groupby` de Excel. Haz clic dentro y juega con el panel de campos.
- **Hoja Escenarios**: celdas amarillas para tus costes → calcula tu **neto**.
- **Colores**: texto azul = valor fijo o supuesto; negro = fórmula; fondo amarillo = lo rellenas tú.

> Al abrir el libro, si las tablas dinámicas salen vacías: *Datos → Actualizar todo*.

---

## 8. El dashboard (`dashboard.html`)

Un **dashboard** es un panel con indicadores y gráficos que se filtran. Este es un único archivo HTML con los datos dentro: ábrelo con doble clic, sin internet. Los **KPI** (*Key Performance Indicators*, indicadores clave) arriba; los filtros cambian todo a la vez. Los títulos de los gráficos se recalculan con el filtro (por ejemplo, la mejor franja de esa semana).

---

## 9. Comunicar: el resumen ejecutivo

Un **resumen ejecutivo** es una página para alguien con poco tiempo: hallazgos con su cifra y su base (n), 3 recomendaciones **accionables** (que se puedan hacer mañana) y qué datos faltan. Ver `RESUMEN_EJECUTIVO.md`. Fíjate en que cada recomendación dice **cuánto se gana o se pierde** y **cuánto fiarse**.

---

## 10. Git: guardar la historia del proyecto

**Git** guarda «fotos» (*commits*) del proyecto. Cada fase tiene su commit con un mensaje claro:
```bash
git log --oneline
```
El archivo `.gitignore` dice qué **no** se guarda: aquí, las fotos y el OCR bruto (tienen tu nombre). Antes de subir el proyecto a GitHub, revisa siempre que no haya datos personales.

---

## 11. Errores que cometí en este proyecto (y cómo los detecté)

Aprender de los errores es parte del oficio:

1. **Un viaje duplicado** por un tipo de servicio mal leído → detectado porque septiembre no cuadraba con la app.
2. **Lecturas dudosas en una foto movida** (18,98 frente a 18,38 €) → resueltas ampliando la foto y confirmadas con el total mensual.
3. **Una jornada «no cerrada»** (02/10, 11,6 h) que hundía el €/hora → detectada comparando la duración con la hora del último viaje y con los otros días.
4. **Etiquetas de gráficos superpuestas** → detectadas mirando los gráficos uno a uno: **mira siempre tus gráficos antes de entregarlos**.
5. **Recuentos mal escritos en el LOG** (12 en vez de 11) → detectados al comparar con la salida real del cuaderno. No escribas cifras de memoria: cópialas del resultado.

---

## 12. Diez ejercicios cortos

Trabaja en un cuaderno nuevo (`ejercicios.ipynb`) en la carpeta del proyecto. Empieza siempre por:
```python
import pandas as pd
v = pd.read_csv("datos/limpios/viajes_limpios.csv")
j = pd.read_csv("datos/limpios/jornadas_limpias.csv")
d = pd.read_csv("datos/limpios/resumen_diario.csv")
```

1. **Explorar.** ¿Cuántas filas y columnas tiene `v`? ¿Qué tipo tiene `importe_eur`? ¿Cuántos viajes hay de cada `producto`? *(Pista: `shape`, `dtypes`, `value_counts()`)*
2. **Filtrar.** ¿Cuántos viajes se pagaron en efectivo y cuánto suman? ¿Coincide con la app (122,61 € en septiembre + 57,79 € en octubre)?
3. **Media frente a mediana.** Calcula la media y la mediana del importe de los viajes con ingreso (> 0). ¿Por qué no son iguales?
4. **Agregar por semana.** Ingresos totales y nº de días trabajados por `semana_iso` (solo días completos). ¿Qué semana tuvo más € por día?
5. **Porcentaje por grupo.** ¿Qué % de viajes son de 0 € en cada `producto`? ¿Cuál tiene más cancelaciones?
6. **SQL.** Escribe una consulta que devuelva, por `metodo_pago`, el nº de viajes y el importe medio. Ejecútala con `sqlite3` contra `datos/vtc.sqlite`.
7. **€/hora.** Con `j` y `d`, calcula el €/hora de cada jornada y el global (cociente de sumas), **incluyendo** el 02/10. ¿Cuánto cambia?
8. **Gráfico.** Haz un gráfico de barras del nº de viajes por `franja_horaria` con un título que diga la conclusión.
9. **Atípicos.** Calcula Q1, Q3 y el IQR de los importes > 0 y lista los viajes por encima de Q3 + 1,5·IQR. ¿Cuántos son de aeropuerto?
10. **Excel.** En `analisis_vtc.xlsx`, crea una tabla dinámica nueva con Filas = `semana_iso`, Columnas = `metodo_pago`, Valores = Suma de `importe_eur`. Compárala con el ejercicio 4.

---

## 13. Glosario

| Término | Significado sencillo |
|---|---|
| **Agregación** | Resumir muchas filas en pocas (suma, media, recuento por grupo). |
| **Atípico (*outlier*)** | Valor muy alejado del resto. Se marca y se decide; no se borra sin más. |
| **Booleano** | Dato que solo puede ser Verdadero o Falso. |
| **Bootstrap** | Calcular la incertidumbre repitiendo el cálculo miles de veces con remuestreos al azar de los propios datos. |
| **Checksum / suma de control** | Total conocido con el que comparas tus datos para detectar errores. |
| **Coste de oportunidad** | Lo que dejas de ganar por dedicar el tiempo a otra cosa. |
| **CSV** | Archivo de texto con una tabla; las columnas van separadas por comas. |
| **Cuartil (Q1, Q3)** | Valores que dejan por debajo al 25 % y al 75 % de los datos. |
| **Dashboard** | Panel con indicadores y gráficos que se pueden filtrar. |
| **DAX** | Lenguaje de fórmulas de Power BI. |
| **Desviación típica** | Medida de lo dispersos que están los datos alrededor de la media. |
| **Diccionario de datos** | Documento que explica cada columna de cada tabla. |
| **Duplicado** | El mismo registro repetido. |
| **EDA (análisis exploratorio)** | Mirar los datos con resúmenes y gráficos antes de concluir. |
| **Función de ventana** | En SQL, cálculo que mira otras filas relacionadas (la anterior, el total del grupo) sin agrupar. |
| **Granularidad** | Qué representa una fila: un viaje, un día, una semana… |
| **IC 95 % (intervalo de confianza)** | Rango donde probablemente está el valor real. |
| **IQR (rango intercuartílico)** | Q3 − Q1: anchura del 50 % central de los datos. |
| **JOIN / merge** | Unir dos tablas por una columna común. |
| **KPI** | Indicador clave (por ejemplo, €/hora). |
| **Limpieza de datos** | Corregir, completar, quitar duplicados y dar formato para que los datos sean fiables. |
| **Media** | Suma ÷ número de casos. |
| **Mediana** | Valor central de los datos ordenados. |
| **Muestra (n)** | Los casos que tienes. Con n pequeño, conclusiones prudentes. |
| **Nulo (NaN)** | Celda sin dato. |
| **OCR** | Convertir texto de una imagen en texto editable. |
| **Pandas** | Librería de Python para trabajar con tablas. |
| **Percentil** | Valor que deja por debajo un % de los datos (P25, P75, P90…). |
| **Power Query** | Herramienta de Excel/Power BI para importar y transformar datos. |
| **RGPD** | Reglamento General de Protección de Datos: te da derecho a pedir tus datos a una empresa. |
| **SQL** | Lenguaje para consultar bases de datos. |
| **Tabla dinámica** | Resumen interactivo de Excel que agrupa y agrega arrastrando campos. |
| **Trazabilidad** | Poder seguir el rastro de cada dato y de cada cambio. |
| **UTC** | Hora universal de referencia (Madrid es UTC+2 en verano y UTC+1 en invierno). |
| **Variable derivada** | Columna nueva calculada a partir de otras. |
| **Zona horaria** | Región con la misma hora oficial (Europe/Madrid). |

---

## 14. Soluciones de los ejercicios

<details>
<summary>Ver soluciones (inténtalo antes)</summary>

```python
# 1
print(v.shape, v.importe_eur.dtype)                 # (212, 22) float64
print(v.producto.value_counts())

# 2
ef = v[v.metodo_pago == "efectivo"]
print(len(ef), ef.importe_eur.sum())                 # 20 viajes, 180.40 € (= 122.61 + 57.79)

# 3
pos = v[v.importe_eur > 0].importe_eur
print(pos.mean(), pos.median())                      # la media es mayor: unos pocos viajes caros la suben

# 4
vc = v[v.dia_completo]
sem = vc.groupby("semana_iso").agg(ingresos=("importe_eur", "sum"), dias=("fecha", "nunique"))
sem["eur_dia"] = sem.ingresos / sem.dias
print(sem.sort_values("eur_dia", ascending=False))   # la 41 (solo 3 días: ojo con n)

# 5
print(v.groupby("producto").sin_ingreso.mean().mul(100).round(1).sort_values(ascending=False))

# 6  (en la terminal: sqlite3 datos/vtc.sqlite)
#   SELECT metodo_pago, COUNT(*) AS viajes, ROUND(AVG(importe_eur), 2) AS medio
#   FROM viajes GROUP BY metodo_pago;

# 7
jd = j.merge(d[["fecha", "ingresos_eur"]], on="fecha")
jd["eur_h"] = jd.ingresos_eur / (jd.tiempo_total_app_min / 60)
print(jd[["fecha", "eur_h"]])
print(jd.ingresos_eur.sum() / (jd.tiempo_total_app_min.sum() / 60))   # 11,70 €/h con el 02/10 (13,09 sin él)

# 8
import matplotlib.pyplot as plt
cuenta = vc.franja_horaria.value_counts().sort_index()
ax = cuenta.plot.bar(color="#2a78d6")
ax.set_title("De 7 a 10 h es cuando más viajes haces")
ax.set_ylabel("Nº de viajes"); plt.tight_layout(); plt.show()

# 9
q1, q3 = pos.quantile([.25, .75]); lim = q3 + 1.5 * (q3 - q1)
at = v[v.importe_eur > lim]
print(lim, len(at), at.es_aeropuerto.sum())          # 28.56 €, 6 viajes, 2 de aeropuerto
```

10: debería dar las mismas sumas por semana que el ejercicio 4 (más la semana 36 con la noche del 31/08 si no filtras `dia_completo`).
</details>

---

## 15. Cómo seguir

- Rellena `parametros_costes.csv` y vuelve a ejecutar `02_analisis.ipynb`: tendrás tu **neto** real.
- Pide tus datos a la plataforma por RGPD (ver `LIMITACIONES.md` §5) y repite el pipeline con datos completos: mismo código, más filas.
- Haz el experimento de las noches y añade esas jornadas.
- Monta el panel en Power BI con `GUIA_POWER_BI.md`.
