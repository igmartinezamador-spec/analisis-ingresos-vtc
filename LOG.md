# LOG del proyecto (bitácora)

Puntos de control cada 30–40 min: qué se hizo, qué falló y qué sigue.

---

## 19:50 — Punto de control 1: inventario y extracción

**Qué hice**
- La carpeta no tenía `datos/` ni `proyecto_vtc/`: solo 55 fotos HEIC sueltas (hechas con iPhone a la pantalla del móvil de trabajo).
  - Decisión: creé `proyecto_vtc/` y copié las fotos a `proyecto_vtc/datos/originales/` (en modo solo lectura, `chmod a-w`). **Las fotos originales de la carpeta padre no se han tocado ni movido.**
- Las convertí a JPG (`datos/jpg/`) con `sips` (herramienta de macOS) para poder leerlas.
- OCR: no hay `tesseract` instalado y no quise descargar nada. Usé el motor de OCR **local** de macOS (framework Vision) con un pequeño script en Swift (`scripts/ocr_vision.swift`). Ningún dato salió del ordenador.
- Extraje automáticamente los viajes del historial (`scripts/extraer_viajes_ocr.py`): 245 filas candidatas en 25 capturas.
- **Validación a mano**: revisé visualmente las 25 capturas del historial (no solo una muestra). Corregí 11 filas, eliminé 11 filas cortadas en el borde y añadí 2 viajes que el OCR no detectó (todo registrado en `datos/intermedios/correcciones_manuales.csv`).
- Anoté a mano el método de pago de cada viaje (icono de móvil = app, icono de monedas = efectivo).
- Consolidé y quité duplicados (`scripts/consolidar_viajes.py`): **212 viajes únicos** del 31/08 al 07/10/2026.

**Comprobaciones que cuadran al céntimo con la app**
- Septiembre pago app 1.620,42 € y efectivo 122,61 € ✔
- Octubre pago app 394,87 € y efectivo 57,79 € ✔

**Qué falló**
- La foto IMG_7843 está movida: el OCR leyó mal 6 filas. Las corregí ampliando la foto original; el total mensual confirma las lecturas.
- Un viaje se duplicaba (02/09 08:55) porque el OCR leyó mal el tipo en una captura. Lo detecté porque septiembre no cuadraba (+12,18 €). Corregido.

**Qué sigue**
- Leer las pantallas de Turnos (horas trabajadas) y de Finanzas (totales diarios y desglose).
- INVENTARIO.md, limpieza en cuaderno, análisis.

---

## 20:02 — Punto de control 2: limpieza y análisis

**Qué hice**
- Transcribí las pantallas de turnos de la flota (8 jornadas) y de Finanzas/perfil a CSV (`datos/intermedios/`). Comprobé que en la app de la flota «Tiempo total = (fin − inicio) + recarga + cuidado» en los 8 días.
- `01_limpieza.ipynb`: correcciones, deduplicado, método de pago, tipos y zona horaria Europe/Madrid, columnas derivadas, atípicos (marcados, no borrados), validación contra la app, jornadas, tabla diaria. Genera `datos/limpios/` y `registro_cambios.csv` (32 cambios).
- `02_analisis.ipynb`: las 7 preguntas, con n, mediana, percentiles e IC 95 % (bootstrap). 8 gráficos en `graficos/`. SQL comprobado frente a pandas.
- Instalé `openpyxl` con pip (solo descarga la librería desde PyPI; no se envió ningún dato).
- `INVENTARIO.md`, `diccionario_de_datos.md`, `parametros_costes.csv` (vacío para que pongas tus costes).

**Decisiones dudosas (para validar)**
- 02/10 excluido del €/hora (sesión 6:30–18:06 con el último viaje a las 11:33: parece una jornada que no se cerró). Si no fue así, el €/hora baja de 13,1 a 11,7.
- 31/08 excluido de los análisis por día (solo hay la noche).
- «Ingreso» = importe del historial (incluye peajes, 11 € en total).

**Qué falló**
- Varios retoques de gráficos (subtítulos que se solapaban y etiquetas). Resueltos.

**Qué sigue**
- SQL, Excel con tablas dinámicas, dashboard HTML, documentos (README, guía, resumen, limitaciones, Power BI), control de calidad.

---

## 20:11 — Punto de control 3: SQL, Excel y dashboard

**Qué hice**
- `consultas.sql` (14 consultas explicadas) + `scripts/ejecutar_sql.py` → `datos/vtc.sqlite`. Resultados iguales a pandas.
- `analisis_vtc.xlsx` (`scripts/crear_excel.py`): resumen con fórmulas, 3 gráficos nativos, escenarios de neto y **4 tablas dinámicas reales**.
- `dashboard.html` (`scripts/crear_dashboard.py`): un solo archivo, filtros por semana/día/plataforma/tipo/pago, 6 KPI, 5 gráficos con tooltip, modo oscuro, tabla. Revisado en escritorio y en móvil; sin errores en consola.

**Qué falló**
- openpyxl no crea tablas dinámicas → las añadí escribiendo el XML del .xlsx. Validado con el lector de openpyxl (que comprueba el esquema de Office) e ida y vuelta (abrir → guardar → abrir).
- **No pude abrir el Excel en Microsoft Excel para verificarlo**: copiar el archivo a la carpeta de Excel pidió un permiso de macOS («acceder a datos de otras apps»). Cancelé el proceso; puede que veas ese aviso en pantalla: puedes ignorarlo o denegarlo. Puede haber quedado una carpeta vacía `~/Library/Containers/com.microsoft.Excel/Data/tmp_verificacion_vtc` (no la toqué por el mismo permiso).
- No hay LibreOffice para recalcular las fórmulas; las verifiqué con `pycel` (evaluador de fórmulas en Python): **todas coinciden con pandas**. Sustituí una fórmula matricial (`SUMPRODUCT/COUNTIF`) que pycel no evalúa por una columna auxiliar más sencilla.
- Instalé `pycel` con pip (solo descarga).

## 20:20 — Punto de control 4: documentación y control de calidad

**Qué hice**
- README, RESUMEN_EJECUTIVO, LIMITACIONES, GUIA_DE_APRENDIZAJE (con glosario y 10 ejercicios + soluciones comprobadas), GUIA_POWER_BI.
- Nuevo hallazgo, añadido al cuaderno 02: de 11:00 al cierre de la sesión solo entran ~6 €/día (3,9 €/h).
- `scripts/control_calidad.py`: recalcula 6 cifras clave **sin pandas y desde los datos transcritos** → todas coinciden; comprueba que las cifras de los informes están bien escritas; busca datos personales; ejecuta los dos cuadernos de principio a fin → **TODO CORRECTO**.

**Qué falló**
- El propio script de control llevaba tu nombre escrito (en el patrón de búsqueda). Lo detecté antes de hacer el commit y lo moví a `datos/privado/` (excluido de Git).

---

## RESUMEN FINAL (para que lo valides)

1. **Hecho:** 55 fotos → 212 viajes y 8 jornadas, validados al céntimo con la app; limpieza y análisis en 2 cuadernos que se ejecutan sin errores; 14 consultas SQL; Excel con fórmulas, gráficos y 4 tablas dinámicas; dashboard HTML; 8 gráficos; toda la documentación; 5 commits locales, uno por fase (sin push).
2. **Resultado clave:** ~13,1 €/h brutos por hora de jornada (IC 95 %: 11,2–14,7); la franja de 8 a 9 h es la mejor; de 11:00 al cierre, ~3,9 €/h; ~1 h 49 min por jornada sin conducción efectiva.
3. **Pendiente (faltan datos):** neto (rellena `parametros_costes.csv` o la hoja Escenarios), zonas, Uber y horas del resto de jornadas. Cómo conseguirlos: `LIMITACIONES.md` §5.
4. **Pendiente (verificación):** abre `analisis_vtc.xlsx` en Excel y confirma que las tablas dinámicas se ven (si salen vacías: Datos → Actualizar todo; si Excel pide «reparar», avísame).
5. **Decisión dudosa:** 02/10 excluido del €/hora (jornada aparentemente no cerrada: 6:30–18:06 con el último viaje a las 11:33). Si trabajaste de verdad hasta las 18:06, el €/hora baja a 11,7 €.
6. **Decisión dudosa:** los viajes de 0 € se tratan como cancelaciones y los de 6 € como importe mínimo; la app no lo confirma.
7. **Decisión dudosa:** «sin clasificar» (56 min/día) lo interpreto como esperas con el coche parado; también podría incluir otras cosas (por ejemplo, devolver el coche).
8. **Decisión dudosa:** no creé un dataset sintético porque los datos reales son suficientes para un análisis acotado; los límites están en LIMITACIONES.md.
9. **Privacidad:** las fotos, el OCR bruto y el nombre real están fuera de Git. Los commits de esta copia pública usan el usuario de GitHub como autor.
10. **Fuera de `proyecto_vtc/`:** solo leí las fotos originales (no las moví ni las borré) y quedó el posible aviso de permiso de Excel del punto 3.
