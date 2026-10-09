"""
Paso 1 (extracción): convierte el texto OCR de las capturas del "Historial de viajes"
en una tabla de viajes candidatos (una fila por viaje visto en cada captura).

- Entrada: datos/ocr_bruto/IMG_xxxx.txt  (líneas "y|x|texto" generadas por ocr_vision.swift)
- Salida : datos/intermedios/viajes_ocr_candidatos.csv

La revisión manual posterior corrige lo que el OCR leyó mal (ver datos/intermedios/correcciones_manuales.csv).
"""
import re
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
OCR = BASE / "datos" / "ocr_bruto"
OUT = BASE / "datos" / "intermedios" / "viajes_ocr_candidatos.csv"

MESES = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7,
         "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
# Las capturas se hicieron el miércoles 7 de octubre de 2026 (lo dicen las pantallas de "Turnos").
RELATIVOS = {"hoy": "2026-10-07", "ayer": "2026-10-06", "lunes": "2026-10-05"}

RE_FECHA = re.compile(r"(?P<dia>\d{1,2}) de (?P<mes>[A-Za-zé]+)\W+(?P<hora>[\dOoBé]{1,2}\W?[\dOoB]{2})", re.I)
RE_REL = re.compile(r"^(?P<rel>Hoy|Ayer|Lunes)\W+(?P<hora>[\dUOo]{1,2}\W?[\dOo]{2})", re.I)
RE_IMPORTE = re.compile(r"(\d{1,3}(?:[.,]\d{2})?)\s?€")
PRODUCTOS = ["VTC Prioritario", "VTC Airport", "VTC Promo", "VTC Eco", "Envíos en coche",
             "Electric", "VTC"]


def normaliza_hora(txt):
    t = txt.replace("O", "0").replace("o", "0").replace("U", "0").replace("B", "8").replace("é", "6")
    d = re.sub(r"\D", "", t)
    if len(d) == 3:
        d = "0" + d
    if len(d) != 4:
        return None
    hh, mm = int(d[:2]), int(d[2:])
    if hh > 23 or mm > 59:
        return None
    return f"{hh:02d}:{mm:02d}"


def producto_de(txt):
    for p in PRODUCTOS:
        if p.lower() in txt.lower():
            return p
    if re.search(r"ca[bh]i", txt, re.I):  # variantes de OCR del nombre del servicio estándar
        return "VTC"
    return None


filas = []
for f in sorted(OCR.glob("IMG_*.txt")):
    lineas = []
    for l in f.read_text().splitlines():
        y, x, t = l.split("|", 2)
        lineas.append((float(y), float(x), t.strip()))
    textos = " ".join(t for _, _, t in lineas)
    if "Historial de viajes" not in textos and "Historial de vidjes" not in textos:
        continue
    fechas, importes, productos = [], [], []
    for y, x, t in lineas:
        m = RE_FECHA.search(t) or RE_REL.search(t)
        if m and x < 0.45:
            if "rel" in m.groupdict() and m.group("rel"):
                fecha = RELATIVOS[m.group("rel").lower()]
            else:
                mes = MESES.get(m.group("mes").lower())
                fecha = f"2026-{mes:02d}-{int(m.group('dia')):02d}" if mes else None
            fechas.append(dict(y=y, texto=t, fecha=fecha, hora=normaliza_hora(m.group("hora"))))
            continue
        mi = RE_IMPORTE.search(t)
        if mi and x > 0.4:
            importes.append(dict(y=y, texto=t, importe=float(mi.group(1).replace(",", "."))))
            continue
        p = producto_de(t)
        if p and x < 0.45:
            productos.append(dict(y=y, texto=t, producto=p))
    for fe in fechas:
        # el tipo de servicio y el importe están ~0.026 por debajo de la línea de fecha
        objetivo = fe["y"] + 0.026
        prod = min((p for p in productos if 0.005 < p["y"] - fe["y"] < 0.05),
                   key=lambda p: abs(p["y"] - objetivo), default=None)
        imp = min((i for i in importes if -0.01 < i["y"] - fe["y"] < 0.06),
                  key=lambda i: abs(i["y"] - objetivo), default=None)
        filas.append(dict(imagen=f.stem, y=round(fe["y"], 3), texto_fecha=fe["texto"],
                          fecha=fe["fecha"], hora=fe["hora"],
                          producto=prod["producto"] if prod else None,
                          texto_importe=imp["texto"] if imp else None,
                          importe_eur=imp["importe"] if imp else None))

df = pd.DataFrame(filas)
df.to_csv(OUT, index=False)
print(f"{len(df)} filas candidatas en {df.imagen.nunique()} imágenes -> {OUT}")
print("Filas con algún hueco:", df[["fecha", "hora", "producto", "importe_eur"]].isna().any(axis=1).sum())
