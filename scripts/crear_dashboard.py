"""
Genera dashboard.html: un informe autocontenido (un solo archivo, sin internet) con filtros
por semana, día de la semana, plataforma, tipo de servicio y método de pago.

Los datos (viajes y jornadas limpios, ya anonimizados) van incrustados como JSON.
Los gráficos se dibujan con SVG y JavaScript sencillo, sin librerías externas.

Uso (desde proyecto_vtc/):  python3 scripts/crear_dashboard.py
"""
import json
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
L = BASE / "datos" / "limpios"
v = pd.read_csv(L / "viajes_limpios.csv")
j = pd.read_csv(L / "jornadas_limpias.csv")

viajes = [dict(f=r.fecha, h=r.hora, s=int(r.semana_iso), d=r.dia_semana, nd=int(r.num_dia_semana), hd=int(r.hora_del_dia),
               p=r.producto, e=round(float(r.importe_eur), 2), pg=r.metodo_pago, c=bool(r.dia_completo))
          for r in v.itertuples()]
jornadas = [dict(f=r.fecha, d=r.dia_semana, ini=r.inicio, fin=r.fin, ce=int(r.conduccion_efectiva_min),
                 re=int(r.recarga_electrica_min), cu=int(r.cuidado_vehiculo_min), ne=int(r.conduccion_no_efectiva_min),
                 sc=int(r.sin_clasificar_min), tot=int(r.tiempo_total_app_min), ef=int(r.tiempo_efectivo_min),
                 an=bool(r.jornada_anomala)) for r in j.itertuples()]

HTML = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Panel VTC</title>
<style>
:root {
  color-scheme: light;
  --bg: #f4f3ef; --surface: #fcfcfb; --surface-2: #f0efec; --border: #e1dfd9; --grid: #e6e4df;
  --text: #0b0b0b; --text-2: #52514e; --muted: #7a7974;
  --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a; --s4: #eda100; --neutral: #b4b2ad;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --bg: #111110; --surface: #1a1a19; --surface-2: #232321; --border: #33332f; --grid: #2c2c29;
    --text: #ffffff; --text-2: #c3c2b7; --muted: #8f8e86;
    --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --neutral: #5f5e59;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #111110; --surface: #1a1a19; --surface-2: #232321; --border: #33332f; --grid: #2c2c29;
  --text: #ffffff; --text-2: #c3c2b7; --muted: #8f8e86;
  --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --neutral: #5f5e59;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font: 15px/1.45 system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; }
.wrap { max-width: 1180px; margin: 0 auto; padding: 20px 16px 48px; }
header h1 { font-size: 1.55rem; margin: 0 0 4px; letter-spacing: -0.01em; }
header p { margin: 0; color: var(--text-2); }
.aviso { margin-top: 10px; font-size: .86rem; color: var(--text-2); background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px; padding: 8px 12px; }
.filtros { display: flex; flex-wrap: wrap; gap: 10px 14px; align-items: end; margin: 18px 0; padding: 12px; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; }
.filtros label { display: flex; flex-direction: column; gap: 3px; font-size: .78rem; color: var(--text-2); font-weight: 600; }
.filtros select { font: inherit; font-size: .9rem; padding: 6px 8px; border-radius: 7px; border: 1px solid var(--border); background: var(--surface); color: var(--text); min-width: 130px; }
.filtros .check { flex-direction: row; align-items: center; gap: 6px; font-weight: 500; padding-bottom: 6px; }
.filtros button { font: inherit; font-size: .85rem; padding: 7px 12px; border-radius: 7px; border: 1px solid var(--border); background: var(--surface-2); color: var(--text); cursor: pointer; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
.kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 12px 14px; }
.kpi .lab { font-size: .78rem; color: var(--text-2); font-weight: 600; }
.kpi .val { font-size: 1.6rem; font-weight: 700; font-variant-numeric: tabular-nums; margin-top: 2px; }
.kpi .sub { font-size: .76rem; color: var(--muted); }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-top: 14px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 14px 14px 10px; min-width: 0; }
.card.ancha { grid-column: 1 / -1; }
.card h2 { font-size: 1.02rem; margin: 0; }
.card .nota { font-size: .8rem; color: var(--text-2); margin: 2px 0 8px; }
.chart { width: 100%; position: relative; }
.chart svg { display: block; width: 100%; height: auto; overflow: visible; }
.chart text { fill: var(--text-2); font-size: 11px; font-variant-numeric: tabular-nums; }
.chart .vlab { fill: var(--text); font-size: 10.5px; }
.chart .grid-l { stroke: var(--grid); stroke-width: 1; }
.chart .eje { stroke: var(--border); stroke-width: 1; }
.chart rect.bar { transition: opacity .12s; }
.chart rect.hit { fill: transparent; cursor: default; }
.tip { position: fixed; pointer-events: none; background: var(--surface); color: var(--text); border: 1px solid var(--border); border-radius: 8px; padding: 7px 10px; font-size: .8rem; box-shadow: 0 4px 16px rgba(0,0,0,.16); display: none; z-index: 10; max-width: 260px; }
.leyenda { display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: .78rem; color: var(--text-2); margin-top: 6px; }
.leyenda span::before { content: ""; display: inline-block; width: 10px; height: 10px; border-radius: 2px; background: var(--c); margin-right: 5px; vertical-align: -1px; }
details { margin-top: 14px; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 10px 14px; }
summary { cursor: pointer; font-weight: 600; }
.tabla { max-height: 380px; overflow: auto; margin-top: 8px; }
table { border-collapse: collapse; width: 100%; font-size: .82rem; font-variant-numeric: tabular-nums; }
th, td { text-align: left; padding: 5px 8px; border-bottom: 1px solid var(--border); white-space: nowrap; }
th { position: sticky; top: 0; background: var(--surface-2); }
td.num, th.num { text-align: right; }
footer { margin-top: 22px; font-size: .78rem; color: var(--muted); }
.vacio { color: var(--muted); font-size: .9rem; padding: 30px 0; text-align: center; }
@media (max-width: 760px) { .grid { grid-template-columns: 1fr; } .kpi .val { font-size: 1.35rem; } }
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>¿Cuándo gano más conduciendo en VTC?</h1>
  <p>Mis viajes reales del 31/08 al 07/10/2026 · 212 viajes · datos anonimizados (sin pasajeros, matrículas ni direcciones)</p>
  <div class="aviso"><strong>Ingresos</strong> = importe que muestra el historial de la plataforma por viaje (incluye propinas y peajes; no se sabe si descuenta comisiones). <strong>No hay datos de Uber</strong> ni de zonas. El €/hora solo existe para 8 jornadas con horas de la app de la flota.</div>
</header>

<section class="filtros" aria-label="Filtros">
  <label>Semana <select id="fSemana"></select></label>
  <label>Día de la semana <select id="fDia"></select></label>
  <label>Plataforma <select id="fPlat"><option value="VTC">VTC</option><option value="Uber" disabled>Uber (sin datos)</option></select></label>
  <label>Tipo de servicio <select id="fProd"></select></label>
  <label>Método de pago <select id="fPago"><option value="">Todos</option><option value="app">App</option><option value="efectivo">Efectivo</option></select></label>
  <label class="check"><input type="checkbox" id="fNoche"> Incluir la noche del 31/08 (día incompleto)</label>
  <button id="reset" type="button">Quitar filtros</button>
</section>

<section class="kpis" id="kpis" aria-live="polite"></section>

<section class="grid">
  <div class="card ancha"><h2 id="t1"></h2><p class="nota">Suma de importes por día. La línea es la media del periodo filtrado.</p><div class="chart" id="c1"></div></div>
  <div class="card"><h2 id="t2"></h2><p class="nota">€ de los viajes que empiezan en cada hora ÷ días en que trabajaste esa hora (entre tu primer y tu último viaje). n = días.</p><div class="chart" id="c2"></div></div>
  <div class="card"><h2 id="t3"></h2><p class="nota">Ingreso medio por día trabajado. n = días (con tan pocos días, diferencias pequeñas no son concluyentes).</p><div class="chart" id="c3"></div></div>
  <div class="card"><h2 id="t4"></h2><p class="nota">Importe medio por viaje sin contar los de 0 €. Solo tipos con 5 o más viajes (con menos, la media no es fiable). n = viajes.</p><div class="chart" id="c4"></div></div>
  <div class="card"><h2 id="t5"></h2><p class="nota">Desglose de cada jornada con horas (app de la flota). Solo días del filtro que tienen ese dato.</p><div class="chart" id="c5"></div><div class="leyenda" id="ley5"></div></div>
</section>

<details>
  <summary>Ver los datos en tabla (viajes del filtro)</summary>
  <div class="tabla"><table><thead><tr><th>Fecha</th><th>Hora</th><th>Día</th><th>Tipo de servicio</th><th>Pago</th><th class="num">Importe</th></tr></thead><tbody id="tbody"></tbody></table></div>
</details>

<footer>Generado con Python a partir de capturas de la app (OCR local y revisión manual; totales validados al céntimo con la app). Proyecto de aprendizaje de análisis de datos.</footer>
</div>
<div class="tip" id="tip" role="tooltip"></div>

<script>
const VIAJES = __VIAJES__;
const JORNADAS = __JORNADAS__;
const DIAS = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"];
const $ = id => document.getElementById(id);
const eur = (x, d = 0) => x.toLocaleString("es-ES", {minimumFractionDigits: d, maximumFractionDigits: d}) + " €";
const num = (x, d = 1) => x.toLocaleString("es-ES", {minimumFractionDigits: d, maximumFractionDigits: d});
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const fechaCorta = f => f.slice(8, 10) + "/" + f.slice(5, 7);

// ---------- filtros ----------
function rellenaFiltros() {
  const semanas = [...new Set(VIAJES.map(v => v.s))].sort((a, b) => a - b);
  $("fSemana").innerHTML = '<option value="">Todas</option>' + semanas.map(s => {
    const fs = VIAJES.filter(v => v.s === s).map(v => v.f).sort();
    return `<option value="${s}">Sem. ${s} (${fechaCorta(fs[0])}–${fechaCorta(fs[fs.length - 1])})</option>`;
  }).join("");
  const dias = DIAS.filter(d => VIAJES.some(v => v.d === d));
  $("fDia").innerHTML = '<option value="">Todos</option>' + dias.map(d => `<option>${d}</option>`).join("");
  const prods = Object.entries(VIAJES.reduce((a, v) => (a[v.p] = (a[v.p] || 0) + 1, a), {})).sort((a, b) => b[1] - a[1]);
  $("fProd").innerHTML = '<option value="">Todos</option>' + prods.map(([p, n]) => `<option value="${p}">${p} (${n})</option>`).join("");
}
function filtrados() {
  const s = $("fSemana").value, d = $("fDia").value, p = $("fProd").value, pg = $("fPago").value, noche = $("fNoche").checked;
  return VIAJES.filter(v => (noche || v.c) && (!s || v.s == s) && (!d || v.d === d) && (!p || v.p === p) && (!pg || v.pg === pg));
}

// ---------- tooltip ----------
const tip = $("tip");
function muestraTip(ev, html) {
  tip.innerHTML = html; tip.style.display = "block";
  const w = tip.offsetWidth, h = tip.offsetHeight;
  let x = ev.clientX + 14, y = ev.clientY - h - 10;
  if (x + w > innerWidth - 8) x = ev.clientX - w - 14;
  if (y < 8) y = ev.clientY + 16;
  tip.style.left = x + "px"; tip.style.top = y + "px";
}
const ocultaTip = () => tip.style.display = "none";

// ---------- gráfico de barras (vertical u horizontal) en SVG ----------
function barras(el, datos, op = {}) {
  el.innerHTML = "";
  if (!datos.length) { el.innerHTML = '<div class="vacio">Sin datos para este filtro</div>'; return; }
  const W = Math.max(el.clientWidth, 280), horiz = !!op.horizontal;
  const NS = "http://www.w3.org/2000/svg";
  const mk = (t, a) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); return e; };
  const bruto = Math.max(...datos.map(d => d.v), op.linea || 0) * 1.1 || 1;
  const paso = (() => { const p = Math.pow(10, Math.floor(Math.log10(bruto / 4))); const f = bruto / 4 / p;
                        return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * p; })();  // marcas redondas: 1, 2, 2,5, 5, 10...
  const max = Math.ceil(bruto / paso) * paso;
  let H, svg;
  if (!horiz) {
    H = op.alto || 230;
    const m = {t: 16, r: op.linea != null ? 46 : 10, b: 34, l: 46}, iw = W - m.l - m.r, ih = H - m.t - m.b;
    svg = mk("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": op.aria || ""});
    const ticks = Math.round(max / paso);
    for (let i = 0; i <= ticks; i++) {
      const val = paso * i, y = m.t + ih - ih * i / ticks;
      svg.append(mk("line", {x1: m.l, x2: W - m.r, y1: y, y2: y, class: i ? "grid-l" : "eje"}));
      const t = mk("text", {x: m.l - 6, y: y + 4, "text-anchor": "end"}); t.textContent = op.fmtEje ? op.fmtEje(val) : Math.round(val); svg.append(t);
    }
    const bw = iw / datos.length, gap = Math.min(bw * 0.28, 14), ancho = Math.max(bw - gap, 2);
    const cadaEtiq = Math.ceil(datos.length / Math.max(1, Math.floor(iw / 44)));
    datos.forEach((d, i) => {
      const x = m.l + i * bw + gap / 2, h = ih * d.v / max, y = m.t + ih - h;
      const r = Math.min(4, ancho / 2, h);
      const path = mk("path", {d: `M${x},${m.t + ih} V${y + r} Q${x},${y} ${x + r},${y} H${x + ancho - r} Q${x + ancho},${y} ${x + ancho},${y + r} V${m.t + ih} Z`,
                              fill: d.c ? css(d.c) : css("--s1"), class: "bar"});
      svg.append(path);
      if (op.etiquetas && datos.length <= 12) { const t = mk("text", {x: x + ancho / 2, y: y - 4, "text-anchor": "middle", class: "vlab"}); t.textContent = op.fmt(d.v); svg.append(t); }
      if (i % cadaEtiq === 0) { const t = mk("text", {x: x + ancho / 2, y: H - m.b + 15, "text-anchor": "middle"}); t.textContent = d.l; svg.append(t); }
      if (d.n != null && datos.length <= 12) { const t = mk("text", {x: x + ancho / 2, y: H - m.b + 28, "text-anchor": "middle", style: "font-size:9.5px"}); t.textContent = "n=" + d.n; svg.append(t); }
      const hit = mk("rect", {x: m.l + i * bw, y: m.t, width: bw, height: ih, class: "hit"});
      hit.addEventListener("mousemove", ev => { path.style.opacity = .78; muestraTip(ev, d.tip); });
      hit.addEventListener("mouseleave", () => { path.style.opacity = 1; ocultaTip(); });
      svg.append(hit);
    });
    if (op.linea != null) {
      const y = m.t + ih - ih * op.linea / max;
      svg.append(mk("line", {x1: m.l, x2: W - m.r, y1: y, y2: y, stroke: css("--text-2"), "stroke-width": 1}));
      const t = mk("text", {x: W - m.r + 4, y: y + 4}); t.textContent = op.fmt(op.linea); svg.append(t);
    }
  } else {
    const fila = 30, m = {t: 4, r: 110, b: 4, l: Math.min(150, W * 0.36)};
    H = m.t + m.b + fila * datos.length;
    const iw = W - m.l - m.r;
    svg = mk("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": op.aria || ""});
    datos.forEach((d, i) => {
      const y = m.t + i * fila + 6, h = fila - 12, w = iw * d.v / max, r = Math.min(4, h / 2, w);
      const path = mk("path", {d: `M${m.l},${y} H${m.l + w - r} Q${m.l + w},${y} ${m.l + w},${y + r} V${y + h - r} Q${m.l + w},${y + h} ${m.l + w - r},${y + h} H${m.l} Z`,
                              fill: d.c ? css(d.c) : css("--s1"), class: "bar"});
      svg.append(path);
      const tl = mk("text", {x: m.l - 8, y: y + h / 2 + 4, "text-anchor": "end"}); tl.textContent = d.l; svg.append(tl);
      const tv = mk("text", {x: m.l + w + 6, y: y + h / 2 + 4, class: "vlab"}); tv.textContent = op.fmt(d.v) + (d.n != null ? `  (n=${d.n})` : ""); svg.append(tv);
      const hit = mk("rect", {x: 0, y: m.t + i * fila, width: W, height: fila, class: "hit"});
      hit.addEventListener("mousemove", ev => { path.style.opacity = .78; muestraTip(ev, d.tip); });
      hit.addEventListener("mouseleave", () => { path.style.opacity = 1; ocultaTip(); });
      svg.append(hit);
    });
  }
  el.append(svg);
}

// ---------- barras apiladas horizontales (desglose de jornada) ----------
const PARTES = [["ce", "Conducción efectiva", "--s1"], ["re", "Recarga eléctrica", "--s2"], ["cu", "Cuidado del vehículo", "--s3"],
                ["ne", "Conducción no efectiva", "--s4"], ["sc", "Sin clasificar (esperas)", "--neutral"]];
function apiladas(el, jor) {
  el.innerHTML = "";
  if (!jor.length) { el.innerHTML = '<div class="vacio">Ninguna jornada con horas en este filtro (solo hay del 28/09 al 07/10)</div>'; return; }
  const W = Math.max(el.clientWidth, 280), fila = 28, m = {t: 4, r: 12, b: 22, l: 56};
  const H = m.t + m.b + fila * jor.length, iw = W - m.l - m.r;
  const max = Math.max(...jor.map(j => PARTES.reduce((a, [k]) => a + j[k], 0))) * 1.04;
  const NS = "http://www.w3.org/2000/svg";
  const mk = (t, a) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); return e; };
  const svg = mk("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Desglose de minutos de cada jornada"});
  for (let mnt = 0; mnt <= max; mnt += 60) {
    const x = m.l + iw * mnt / max;
    svg.append(mk("line", {x1: x, x2: x, y1: m.t, y2: H - m.b, class: mnt ? "grid-l" : "eje"}));
    const t = mk("text", {x, y: H - 6, "text-anchor": "middle"}); t.textContent = (mnt / 60) + " h"; svg.append(t);
  }
  jor.forEach((j, i) => {
    const y = m.t + i * fila + 5, h = fila - 10; let x = m.l;
    const t = mk("text", {x: m.l - 8, y: y + h / 2 + 4, "text-anchor": "end"}); t.textContent = fechaCorta(j.f) + (j.an ? "*" : ""); svg.append(t);
    PARTES.forEach(([k, , c]) => {
      const w = iw * j[k] / max; if (w <= 0) return;
      svg.append(mk("rect", {x: x, y, width: Math.max(w - 2, 0.5), height: h, fill: css(c), rx: 2}));
      x += w;
    });
    const hit = mk("rect", {x: 0, y: m.t + i * fila, width: W, height: fila, class: "hit"});
    const tipHtml = `<strong>${j.d} ${fechaCorta(j.f)}</strong> (${j.ini}–${j.fin})${j.an ? "<br><em>Jornada anómala: probablemente no se cerró</em>" : ""}<br>` +
      PARTES.map(([k, n]) => `${n}: ${j[k]} min`).join("<br>") + `<br>Tiempo total (app): ${j.tot} min`;
    hit.addEventListener("mousemove", ev => muestraTip(ev, tipHtml));
    hit.addEventListener("mouseleave", ocultaTip);
    svg.append(hit);
  });
  el.append(svg);
}
$("ley5").innerHTML = PARTES.map(([, n, c]) => `<span style="--c:var(${c})">${n}</span>`).join("") + '<span style="--c:transparent">* jornada anómala (excluida del €/hora)</span>';

// ---------- cálculo y pintado ----------
function agrupa(arr, k) { return arr.reduce((a, x) => ((a[k(x)] = a[k(x)] || []).push(x), a), {}); }
function render() {
  const V = filtrados();
  const porDia = agrupa(V, v => v.f);
  const fechas = Object.keys(porDia).sort();
  const total = V.reduce((a, v) => a + v.e, 0);
  const conIng = V.filter(v => v.e > 0);
  const nDias = fechas.length;
  // €/hora: jornadas con horas cuyas fechas están en el filtro (sin la anómala).
  // Ojo: con filtro de tipo de servicio o pago, los € de la jornada son solo los de ese tipo.
  const J = JORNADAS.filter(j => porDia[j.f]);
  const Jok = J.filter(j => !j.an);
  const eurJ = Jok.reduce((a, j) => a + porDia[j.f].reduce((s, v) => s + v.e, 0), 0);
  const hJ = Jok.reduce((a, j) => a + j.tot, 0) / 60;
  const kpis = [
    ["Ingresos", eur(total, 0), `${V.length} viajes`],
    ["Días trabajados", nDias, nDias ? `${num(V.length / nDias)} viajes/día` : "—"],
    ["Ingreso medio por día", nDias ? eur(total / nDias, 0) : "—", "suma ÷ días"],
    ($("fProd").value || $("fPago").value)
      ? ["€ por hora de jornada", "—", "no aplica con filtro de tipo de servicio o de pago"]
      : ["€ por hora de jornada", hJ ? eur(eurJ / hJ, 2) : "—", hJ ? `${Jok.length} jornada(s) con horas` : "sin jornadas con horas en el filtro"],
    ["Importe medio por viaje", conIng.length ? eur(conIng.reduce((a, v) => a + v.e, 0) / conIng.length, 2) : "—", "sin contar los de 0 €"],
    ["Viajes a 0 €", V.length ? num(100 * (V.length - conIng.length) / V.length) + " %" : "—", `${V.length - conIng.length} probables cancelaciones`],
  ];
  $("kpis").innerHTML = kpis.map(([l, v, s]) => `<div class="kpi"><div class="lab">${l}</div><div class="val">${v}</div><div class="sub">${s}</div></div>`).join("");

  // 1) ingresos por día
  const d1 = fechas.map(f => { const s = porDia[f].reduce((a, v) => a + v.e, 0);
    return {l: fechaCorta(f), v: s, tip: `<strong>${porDia[f][0].d} ${fechaCorta(f)}</strong><br>${eur(s, 2)} · ${porDia[f].length} viajes`}; });
  const media = nDias ? total / nDias : 0;
  $("t1").textContent = nDias ? `Ganas de media ${eur(media)} por día trabajado (${nDias} días)` : "Ingresos por día";
  barras($("c1"), d1, {linea: media, fmt: x => eur(x), fmtEje: x => eur(x), aria: "Ingresos por día", alto: 220});

  // 2) € por hora trabajada según la hora del día
  const sumH = {}, diasH = {};
  fechas.forEach(f => { const hs = porDia[f].map(v => v.hd); const a = Math.min(...hs), b = Math.max(...hs);
    for (let h = a; h <= b; h++) { diasH[h] = (diasH[h] || 0) + 1; sumH[h] = sumH[h] || 0; }
    porDia[f].forEach(v => sumH[v.hd] += v.e); });
  const horas = Object.keys(diasH).map(Number).sort((a, b) => a - b);
  const d2raw = horas.map(h => ({h, v: sumH[h] / diasH[h], n: diasH[h]}));
  const fiables = d2raw.filter(d => d.n >= 3);
  const mejor = fiables.length ? fiables.reduce((a, b) => b.v > a.v ? b : a) : null;
  const d2 = d2raw.map(d => ({l: String(d.h).padStart(2, "0") + "h", v: d.v, n: d.n, c: mejor && d.h === mejor.h ? "--s2" : null,
    tip: `<strong>${String(d.h).padStart(2, "0")}:00–${String(d.h).padStart(2, "0")}:59</strong><br>${eur(d.v, 2)} por hora trabajada<br>${d.n} días${d.n < 3 ? " (muestra muy pequeña)" : ""}`}));
  $("t2").textContent = mejor ? `La franja de las ${String(mejor.h).padStart(2, "0")}:00 es la que más rinde (${eur(mejor.v)}/h)` : "€ por hora trabajada según la hora";
  barras($("c2"), d2, {etiquetas: true, fmt: x => eur(x), fmtEje: x => eur(x), aria: "Euros por hora trabajada según la hora del día"});

  // 3) día de la semana
  const porDS = agrupa(fechas, f => porDia[f][0].d);
  const d3 = DIAS.filter(d => porDS[d]).map(d => { const fs = porDS[d]; const s = fs.reduce((a, f) => a + porDia[f].reduce((x, v) => x + v.e, 0), 0);
    return {l: d.slice(0, 3), v: s / fs.length, n: fs.length, tip: `<strong>${d}</strong><br>${eur(s / fs.length, 2)} de media por día<br>${fs.length} días`}; });
  const top3 = d3.length ? d3.reduce((a, b) => b.v > a.v ? b : a) : null;
  const rango = d3.length > 1 ? Math.max(...d3.map(d => d.v)) - Math.min(...d3.map(d => d.v)) : 0;
  $("t3").textContent = d3.length > 1 ? (Math.min(...d3.map(d => d.n)) < 7 ? `Diferencias de hasta ${eur(rango)} entre días, con pocos días por grupo: no concluyente` : `El ${DIAS.find(x => x.startsWith(top3.l))} es el mejor día`) : "Ingreso medio por día de la semana";
  barras($("c3"), d3, {etiquetas: true, fmt: x => eur(x), fmtEje: x => eur(x), aria: "Ingreso medio por día de la semana"});

  // 4) tipos de servicio
  const porP = agrupa(V, v => v.p);
  const d4 = Object.entries(porP).map(([p, vs]) => { const ci = vs.filter(v => v.e > 0);
      return {l: p, v: ci.length ? ci.reduce((a, v) => a + v.e, 0) / ci.length : 0, n: vs.length, c: p === "VTC Airport" ? "--s2" : null,
              tip: `<strong>${p}</strong><br>${vs.length} viajes (${vs.length - ci.length} a 0 €)<br>Importe medio sin ceros: ${ci.length ? eur(ci.reduce((a, v) => a + v.e, 0) / ci.length, 2) : "—"}`}; })
    .sort((a, b) => b.v - a.v);
  const d4f = d4.filter(d => d.n >= 5).length ? d4.filter(d => d.n >= 5) : d4;   // con < 5 viajes la media no es fiable
  const aer = d4.find(d => d.l === "VTC Airport"), norm = d4.find(d => d.l === "VTC");
  $("t4").textContent = aer && norm && norm.v ? `Un viaje de aeropuerto vale un ${Math.round(100 * (aer.v / norm.v - 1))} % más que uno normal` : "Importe medio por tipo de servicio";
  barras($("c4"), d4f, {horizontal: true, fmt: x => eur(x, 2), aria: "Importe medio por tipo de servicio"});

  // 5) desglose de jornadas
  const muertos = Jok.length ? Jok.reduce((a, j) => a + j.re + j.cu + j.ne + j.sc, 0) / Jok.length : 0;
  $("t5").textContent = Jok.length ? `~${Math.floor(Math.round(muertos) / 60)} h ${Math.round(muertos) % 60} min por jornada sin conducción efectiva` : "Desglose de la jornada";
  apiladas($("c5"), J);

  // tabla
  $("tbody").innerHTML = V.slice().sort((a, b) => (b.f + b.h).localeCompare(a.f + a.h)).map(v =>
    `<tr><td>${fechaCorta(v.f)}</td><td>${v.h}</td><td>${v.d}</td><td>${v.p}</td><td>${v.pg}</td><td class="num">${eur(v.e, 2)}</td></tr>`).join("");
}

rellenaFiltros();
["fSemana", "fDia", "fProd", "fPago", "fNoche"].forEach(id => $(id).addEventListener("change", render));
$("reset").addEventListener("click", () => { ["fSemana", "fDia", "fProd", "fPago"].forEach(id => $(id).value = ""); $("fNoche").checked = false; render(); });
let t; addEventListener("resize", () => { clearTimeout(t); t = setTimeout(render, 150); });
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);
render();
</script>
</body>
</html>
"""

html = HTML.replace("__VIAJES__", json.dumps(viajes, ensure_ascii=False)).replace("__JORNADAS__", json.dumps(jornadas, ensure_ascii=False))
(BASE / "dashboard.html").write_text(html, encoding="utf-8")
print(f"dashboard.html creado ({len(html) / 1024:.0f} KB, {len(viajes)} viajes, {len(jornadas)} jornadas)")
