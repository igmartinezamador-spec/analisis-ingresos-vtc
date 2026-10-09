"""
Control de calidad final.

1. Recalcula cifras clave de forma INDEPENDIENTE: parte de los CSV transcritos
   (datos/intermedios), no de los limpios, y usa solo Python estándar (sin pandas).
   Compara con metricas_clave.json y con el texto de los informes.
2. Busca datos personales en todos los archivos que van a Git.
3. Ejecuta los dos cuadernos de principio a fin (en una copia temporal) y comprueba que no hay errores.

Uso (desde proyecto_vtc/):  python3 scripts/control_calidad.py
"""
import csv
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
INT = BASE / "datos" / "intermedios"
m = json.loads((BASE / "datos" / "limpios" / "metricas_clave.json").read_text())
fallos = []


def ok(cond, texto):
    print(("  ✔ " if cond else "  ✘ ") + texto)
    if not cond:
        fallos.append(texto)


# ------------------------------------------------------------------ 1. Recalcular cifras
print("1) Recalculo independiente de cifras clave")
viajes = list(csv.DictReader(open(INT / "viajes_transcritos.csv", encoding="utf-8")))
for v in viajes:
    v["importe"] = float(v["importe_eur"])
app = {(r["concepto"], r["periodo"]): float(r["valor"]) for r in csv.DictReader(open(INT / "resumen_app_transcrito.csv", encoding="utf-8"))}
jornadas = list(csv.DictReader(open(INT / "jornadas_flota_transcritas.csv", encoding="utf-8")))

# Cifra 1: totales por mes y método de pago frente a la app
for mes in ["2026-09", "2026-10"]:
    for metodo, concepto in [("app", "viajes_pago_app"), ("efectivo", "viajes_efectivo")]:
        s = round(sum(v["importe"] for v in viajes if v["fecha"][:7] == mes and v["metodo_pago"] == metodo), 2)
        ok(abs(s - app[(concepto, mes)]) < 0.005, f"Cifra 1 · {mes} {metodo}: {s:.2f} € = app {app[(concepto, mes)]:.2f} €")

# Solo días completos (sin el 31/08)
comp = [v for v in viajes if v["fecha"] != "2026-08-31"]
por_dia = defaultdict(float)
for v in comp:
    por_dia[v["fecha"]] += v["importe"]

# Cifra 2: ingreso medio por día
media_dia = sum(por_dia.values()) / len(por_dia)
ok(abs(media_dia - m["ingreso_medio_dia"]) < 0.01, f"Cifra 2 · ingreso medio por día: {media_dia:.2f} € (cuaderno {m['ingreso_medio_dia']})")

# Cifra 3: € por hora de jornada (7 jornadas, sin la anómala)
eur = horas = 0
for j in jornadas:
    ini, fin = (datetime.strptime(j[k], "%H:%M") for k in ("inicio", "fin"))
    if (fin - ini).seconds / 60 > 600:     # la jornada del 02/10 (sesión > 10 h): anómala
        continue
    eur += por_dia[j["fecha"]]
    horas += int(j["tiempo_total_app_min"]) / 60
eur_h = eur / horas
ok(abs(eur_h - m["eur_hora_tiempo_total"]) < 0.01, f"Cifra 3 · € por hora de jornada: {eur_h:.2f} (cuaderno {m['eur_hora_tiempo_total']})")

# Cifra 4: % de viajes a 0 €
pct0 = 100 * sum(v["importe"] == 0 for v in comp) / len(comp)
ok(abs(pct0 - m["pct_viajes_0_eur"]) < 0.05, f"Cifra 4 · % viajes a 0 €: {pct0:.1f} % (cuaderno {m['pct_viajes_0_eur']})")

# Cifra 5: importe medio de aeropuerto frente al resto (sin ceros)
aer = [v["importe"] for v in comp if v["producto"] == "VTC Airport" and v["importe"] > 0]
resto = [v["importe"] for v in comp if v["producto"] != "VTC Airport" and v["importe"] > 0]
ok(abs(sum(aer) / len(aer) - m["ticket_medio_aeropuerto"]) < 0.01 and abs(sum(resto) / len(resto) - m["ticket_medio_resto"]) < 0.01,
   f"Cifra 5 · importe medio aeropuerto {sum(aer) / len(aer):.2f} € / resto {sum(resto) / len(resto):.2f} €")

# Cifra 6: minutos sin conducción efectiva (recarga + cuidado + no efectiva + sin clasificar)
mins = []
for j in jornadas:
    ini, fin = (datetime.strptime(j[k], "%H:%M") for k in ("inicio", "fin"))
    ses = (fin - ini).seconds / 60
    if ses > 600:
        continue
    sin_clas = ses - int(j["conduccion_efectiva_min"]) - int(j["conduccion_no_efectiva_min"]) - int(j["descansos_min"])
    mins.append(int(j["recarga_electrica_min"]) + int(j["cuidado_vehiculo_min"]) + int(j["conduccion_no_efectiva_min"]) + sin_clas)
ok(abs(sum(mins) / len(mins) - m["min_muertos_dia"]) < 0.1, f"Cifra 6 · minutos/día sin conducción efectiva: {sum(mins) / len(mins):.1f} (cuaderno {m['min_muertos_dia']})")

# Las cifras aparecen bien escritas en los informes
print("\n   Cifras en los informes:")
textos = {f: (BASE / f).read_text(encoding="utf-8") for f in ["README.md", "RESUMEN_EJECUTIVO.md"]}
es = lambda x, d=1: f"{x:.{d}f}".replace(".", ",")
esperado = {
    "13,1 €/h": es(eur_h) + " €/h",
    "84 €": f"{media_dia:.0f} €",
    "15 % a 0 €": f"{pct0:.0f} % a 0 €",
    "17,39 €": es(sum(aer) / len(aer), 2) + " €",
    "1 h 49 min": f"{round(sum(mins) / len(mins)) // 60} h {round(sum(mins) / len(mins)) % 60} min",
}
for nombre, cadena in esperado.items():
    donde = [f for f, t in textos.items() if cadena in t]
    ok(bool(donde), f"«{cadena}» aparece en {', '.join(donde) if donde else 'NINGÚN informe'}")

# ------------------------------------------------------------------ 2. Privacidad
print("\n2) Búsqueda de datos personales en los archivos versionados")
versionados = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=BASE,
                             capture_output=True, text=True).stdout.split("\n")
patrones = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "teléfono español": re.compile(r"(?<![\d.,])(?:\+34\s?)?[6789]\d{2}\s?\d{3}\s?\d{3}(?![\d.,])"),
    "matrícula (0000 XXX)": re.compile(r"\b\d{4}\s?[BCDFGHJKLMNPRSTVWXYZ]{3}\b"),
    "dirección": re.compile(r"\b(calle|c/|avda\.?|avenida|plaza|paseo|n[ºo]\s?\d+)\s+[A-ZÁÉÍÓÚ]", re.I),
}
# El nombre del conductor NO se escribe aquí (este archivo va a Git): se lee de un archivo privado no versionado.
privado = BASE / "datos" / "privado" / "terminos_privados.txt"
if privado.exists():
    terminos = [t.strip() for t in privado.read_text(encoding="utf-8").splitlines() if t.strip()]
    patrones["nombre o apellidos del conductor"] = re.compile(r"\b(" + "|".join(map(re.escape, terminos)) + r")\b", re.I)
else:
    print("   (aviso: falta datos/privado/terminos_privados.txt; no se busca el nombre)")
correo_local = subprocess.run(["git", "config", "user.email"], cwd=BASE, capture_output=True, text=True).stdout.strip()
excepciones = {"noreply@anthropic.com", correo_local}
hallazgos = []
for f in versionados:
    p = BASE / f
    if not f or not p.is_file() or f.startswith("scripts/control_calidad"):
        continue
    if p.suffix == ".xlsx":
        with zipfile.ZipFile(p) as z:
            contenido = " ".join(z.read(n).decode("utf-8", "ignore") for n in z.namelist() if n.endswith(".xml"))
    elif p.suffix in {".png", ".sqlite"}:
        contenido = p.read_bytes().decode("latin-1", "ignore") if p.suffix == ".sqlite" else ""
    else:
        contenido = p.read_text(encoding="utf-8", errors="ignore")
    if p.suffix == ".ipynb":   # las imágenes de los cuadernos son base64: se quitan para no dar falsos positivos
        contenido = re.sub(r'"image/png": "[^"]*"', "", contenido)
    for nombre, pat in patrones.items():
        for mt in pat.finditer(contenido):
            if mt.group(0) in excepciones:
                continue
            hallazgos.append((f, nombre, mt.group(0)))
for h in hallazgos[:20]:
    print("   ·", h)
ok(not hallazgos, f"Sin datos personales en {len([f for f in versionados if f])} archivos versionados")
autor = subprocess.run(["git", "log", "--format=%an <%ae>"], cwd=BASE, capture_output=True, text=True).stdout.split("\n")[0]
print(f"   (Autor de los commits: «{autor}». Solo nombre de pila y correo local: cámbialo si lo prefieres)")

# ------------------------------------------------------------------ 3. Cuadernos de principio a fin
print("\n3) Ejecución de los cuadernos de principio a fin (en copia temporal)")
with tempfile.TemporaryDirectory() as tmp:
    for nb in ["01_limpieza.ipynb", "02_analisis.ipynb"]:
        r = subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute",
                            "--output-dir", tmp, nb], cwd=BASE, capture_output=True, text=True)
        salida = json.loads((Path(tmp) / nb).read_text()) if r.returncode == 0 else None
        errores = [o for c in (salida or {}).get("cells", []) for o in c.get("outputs", []) if o.get("output_type") == "error"]
        ok(r.returncode == 0 and not errores, f"{nb} se ejecuta sin errores")

print("\n" + ("TODO CORRECTO" if not fallos else f"{len(fallos)} PROBLEMA(S): " + " | ".join(fallos)))
sys.exit(1 if fallos else 0)
