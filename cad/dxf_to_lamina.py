#!/usr/bin/env python3
"""
Pipeline: DXF de AutoCAD  ->  lámina branded (HTML/SVG teñible por color de proyecto).

Uso:
    python3 dxf_to_lamina.py planos/SALON_DPTO_OLMEDO.dxf lamina-olmedo.html "Edificio Olmedo"

Qué hace:
  1) Lee el DXF, apaga capas de presentación y borra entidades "outlier" (lejos del plano).
  2) Renderiza a SVG monocromático (escala de grises) con ezdxf.
  3) Reemplaza los grises por `currentColor`  ->  el trazo se tiñe del color del proyecto.
  4) Envuelve el SVG en una lámina HTML con rótulo, selector de color y modo claro/oscuro.

Requiere: ezdxf, pillow  (pip install ezdxf pillow)
"""
import sys, re
import ezdxf
import ezdxf.bbox as bb
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing import svg, layout, config

GRISES = ['#d3d3d3','#4c4c4c','#ffffff','#aeaeae','#a6a6a6','#f4f4f4']
SKIP_LAYERS = ["A-VIEWPORT","PRESENTACION","REVISION","Defpoints"]

def dxf_to_tinted_svg(dxf_path, outlier=150.0, stroke=0.35):
    doc = ezdxf.readfile(dxf_path)
    for name in SKIP_LAYERS:
        if name in doc.layers:
            doc.layers.get(name).off()
    msp = doc.modelspace()
    # borrar entidades perdidas lejos del plano real
    for e in list(msp):
        try:
            b = bb.extents([e], fast=True)
            if b.has_data and (b.extmin.x > outlier or b.extmin.y > outlier):
                msp.delete_entity(e)
        except Exception:
            pass
    ctx = RenderContext(doc)
    backend = svg.SVGBackend()
    cfg = config.Configuration(
        background_policy=config.BackgroundPolicy.OFF,
        color_policy=config.ColorPolicy.MONOCHROME_DARK_BG,
    )
    Frontend(ctx, backend, config=cfg).draw_layout(msp)
    page = layout.Page(0, 0, layout.Units.mm, margins=layout.Margins.all(2))
    settings = layout.Settings(fit_page=True, fixed_stroke_width=stroke)
    s = backend.get_string(page, settings=settings)
    for c in GRISES:
        s = s.replace(c, 'currentColor')
    s = re.sub(r'(<svg[^>]*?)width="[^"]*"\s*height="[^"]*"', r'\1width="100%"', s, count=1)
    return s

def wrap_lamina(svg_str, titulo="Proyecto", sub="PL-01", foot=""):
    return f'''<title>{sub} · {titulo} — lámina branded</title>
<style>
  :root{{ --acc:#4f7fb0; }}
  *{{box-sizing:border-box;}} html,body{{margin:0;height:100%;}}
  .sheet{{ position:relative; min-height:100svh; padding:clamp(14px,3vw,30px);
    font-family:'Helvetica Neue',Helvetica,Arial,system-ui,sans-serif;
    --paper:#0d0e10; --ink:#ECE8E0; --muted:#8A867C;
    background:var(--paper); color:var(--ink); transition:background .4s,color .4s; }}
  .sheet[data-mode="light"]{{ --paper:#F4F2EC; --ink:#1A1918; --muted:#7C766B; }}
  .wrap{{ max-width:1200px; margin:0 auto; }}
  .planbox{{ color:var(--acc); }} .planbox svg{{ width:100%; height:auto; display:block; }}
  .head{{ display:flex; align-items:baseline; justify-content:space-between; gap:16px;
    border-bottom:2px solid var(--ink); padding-bottom:10px; margin-bottom:14px; flex-wrap:wrap; }}
  .head h1{{ margin:0; font-size:clamp(20px,3.4vw,32px); font-weight:800; letter-spacing:-.01em; text-transform:uppercase; }}
  .head .sub{{ font-family:ui-monospace,Menlo,monospace; font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); }}
  .foot{{ display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap;
    border-top:1px solid var(--muted); margin-top:14px; padding-top:12px;
    font-family:ui-monospace,Menlo,monospace; font-size:12px; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); }}
  .foot b{{ color:var(--ink); font-weight:600; }}
  .ctl{{ display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin:0 0 16px; }}
  .lbl{{ font-family:ui-monospace,Menlo,monospace; font-size:11px; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); }}
  .chip{{ font-family:ui-monospace,Menlo,monospace; font-size:11px; letter-spacing:.06em; text-transform:uppercase;
    color:var(--ink); background:transparent; border:1px solid var(--muted); padding:7px 12px; border-radius:999px; cursor:pointer; transition:.2s; }}
  .chip[aria-pressed="true"]{{ background:var(--acc); border-color:var(--acc); color:#0d0e10; font-weight:700; }}
  .chip:hover{{ border-color:var(--acc); }} .sp{{ flex:1; }}
</style>
<div class="sheet" data-mode="dark" id="sheet"><div class="wrap">
  <div class="ctl"><span class="lbl">Color del proyecto:</span>
    <button class="chip" data-c="#4f7fb0" aria-pressed="true">Hormigón</button>
    <button class="chip" data-c="#e0863a" aria-pressed="false">Atardecer</button>
    <button class="chip" data-c="#8caf3f" aria-pressed="false">Vegetación</button>
    <button class="chip" data-c="#a45cc9" aria-pressed="false">Noche</button>
    <button class="chip" data-c="#d8433a" aria-pressed="false">Brasa</button>
    <span class="sp"></span><button class="chip" id="mode">Modo claro</button></div>
  <div class="head"><h1>{titulo}</h1><span class="sub">{sub}</span></div>
  <div class="planbox">{svg_str}</div>
  <div class="foot"><div>{foot}</div><div>AR STUDIO · アイコン · 2026</div><div>COLOR · <b id="hex">#4F7FB0</b></div></div>
</div></div>
<script>
  const sheet=document.getElementById('sheet');const chips=[...document.querySelectorAll('.chip[data-c]')];
  function setC(h){{document.documentElement.style.setProperty('--acc',h);document.getElementById('hex').textContent=h.toUpperCase();}}
  chips.forEach(c=>c.onclick=()=>{{chips.forEach(x=>x.setAttribute('aria-pressed','false'));c.setAttribute('aria-pressed','true');setC(c.dataset.c);}});
  const mb=document.getElementById('mode');
  mb.onclick=()=>{{const m=sheet.getAttribute('data-mode')==='dark'?'light':'dark';sheet.setAttribute('data-mode',m);mb.textContent=m==='dark'?'Modo claro':'Modo oscuro';}};
</script>'''

if __name__ == "__main__":
    dxf = sys.argv[1] if len(sys.argv) > 1 else "planos/SALON_DPTO_OLMEDO.dxf"
    out = sys.argv[2] if len(sys.argv) > 2 else "lamina-olmedo.html"
    titulo = sys.argv[3] if len(sys.argv) > 3 else "Edificio Olmedo"
    svg_str = dxf_to_tinted_svg(dxf)
    html = wrap_lamina(svg_str, titulo=titulo,
                       sub="PL-01 · Planta baja + Planta alta · ESC según cotas",
                       foot="PLANTA BAJA: salón comercial + entradas · PLANTA ALTA: 4 deptos (2 dorm.)")
    open(out, "w").write(html)
    print("OK ->", out, "| bytes:", len(html))
