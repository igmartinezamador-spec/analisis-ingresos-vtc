"""
Paso 2 (consolidación): aplica las correcciones manuales a los viajes candidatos del OCR
y elimina los duplicados que aparecen por el solape entre capturas.

Regla de duplicados: un mismo viaje (fecha, hora, tipo, importe) puede salir en 2 capturas
seguidas. Se cuenta cuántas veces aparece como máximo DENTRO de una misma captura y se
conserva ese número (así no se borran dos viajes reales idénticos, como los dos de
14/09 09:13 VTC Eco 0 € que aparecen juntos en la misma foto).

Salida: datos/intermedios/viajes_transcritos.csv (aún con datos de pago, sin limpieza final)
"""
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
INT = BASE / "datos" / "intermedios"

cand = pd.read_csv(INT / "viajes_ocr_candidatos.csv")
corr = pd.read_csv(INT / "correcciones_manuales.csv")
cand["origen"] = "ocr"

# 1) eliminar y corregir filas concretas (clave: imagen + texto de fecha leído por el OCR)
for _, c in corr.iterrows():
    m = (cand.imagen == c.imagen) & (cand.texto_fecha == c.texto_fecha)
    if c.accion == "eliminar":
        assert m.sum() == 1, f"No encuentro {c.imagen} {c.texto_fecha}"
        cand = cand[~m]
    elif c.accion == "corregir":
        assert m.sum() == 1, f"No encuentro {c.imagen} {c.texto_fecha}"
        for col in ["fecha", "hora", "producto", "importe_eur"]:
            cand.loc[m, col] = c[col]
        cand.loc[m, "origen"] = "ocr+corrección manual"
    elif c.accion == "añadir":
        nueva = dict(imagen=c.imagen, y=None, texto_fecha=c.texto_fecha, fecha=c.fecha, hora=c.hora,
                     producto=c.producto, texto_importe=None, importe_eur=c.importe_eur,
                     origen="transcripción manual")
        cand = pd.concat([cand, pd.DataFrame([nueva])], ignore_index=True)

assert cand[["fecha", "hora", "producto", "importe_eur"]].notna().all().all(), "Quedan huecos"

# 2) deduplicar
clave = ["fecha", "hora", "producto", "importe_eur"]
max_por_imagen = cand.groupby(clave + ["imagen"]).size().groupby(level=clave).max().rename("n")
origenes = cand.groupby(clave).agg(imagenes=("imagen", lambda s: ";".join(sorted(set(s)))),
                                   origen=("origen", lambda s: "/".join(sorted(set(s)))))
viajes = max_por_imagen.reset_index().merge(origenes.reset_index(), on=clave)
viajes = viajes.loc[viajes.index.repeat(viajes.n)].drop(columns="n")

# 3) método de pago (icono de la fila: móvil = app, monedas = efectivo), anotado a mano
ef = pd.read_csv(INT / "pagos_efectivo_manual.csv")
ef["metodo_pago"] = "efectivo"
viajes = viajes.merge(ef[["fecha", "hora", "importe_eur", "metodo_pago"]],
                      on=["fecha", "hora", "importe_eur"], how="left")
assert viajes.metodo_pago.eq("efectivo").sum() == len(ef), "Algún pago en efectivo no casa"
viajes["metodo_pago"] = viajes.metodo_pago.fillna("app")

viajes = viajes.sort_values(["fecha", "hora"]).reset_index(drop=True)
viajes.to_csv(INT / "viajes_transcritos.csv", index=False)
print(f"Candidatas tras correcciones: {len(cand)} -> viajes únicos: {len(viajes)}")
