"""
Crea la base de datos SQLite datos/vtc.sqlite a partir de los CSV limpios
y ejecuta todas las consultas de consultas.sql, mostrando el resultado de cada una.

Uso (desde la carpeta proyecto_vtc/):   python3 scripts/ejecutar_sql.py
"""
import re
import sqlite3
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
LIMPIOS = BASE / "datos" / "limpios"
DB = BASE / "datos" / "vtc.sqlite"

if DB.exists():
    DB.unlink()  # se regenera siempre desde los CSV (es un archivo derivado)
con = sqlite3.connect(DB)
tablas = {"viajes": "viajes_limpios.csv", "jornadas": "jornadas_limpias.csv",
          "dias": "resumen_diario.csv", "app": "resumen_app.csv"}
for nombre, archivo in tablas.items():
    df = pd.read_csv(LIMPIOS / archivo)
    df.to_sql(nombre, con, index=False)          # pandas crea la tabla y la rellena
    print(f"Tabla {nombre}: {len(df)} filas")

texto = (BASE / "consultas.sql").read_text()
bloques = re.split(r"^-- @", texto, flags=re.M)[1:]   # cada bloque empieza por "-- @nombre:"
pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 20)
for b in bloques:
    nombre, resto = b.split(":", 1)
    sql = resto.split("\n", 1)[1]                 # quitar la línea del título
    print(f"\n=== {nombre} ===")
    print(pd.read_sql(sql, con).to_string(index=False))
con.close()
print(f"\nBase de datos creada en {DB.relative_to(BASE)}")
