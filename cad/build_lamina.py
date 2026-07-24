#!/usr/bin/env python3
"""Genera una lamina branded (SVG) de un departamento usando los bloques de Plancraft."""
import re, os

BLOCKS_DIR = "/home/user/Alexander-Romero/cad/blocks/default"
OUT = "/home/user/Alexander-Romero/cad/demo-olmedo.html"

# --- viewBox reales (mm) por bloque (del manifest) ---
VB = {
 "bed":(1400,2000),"wardrobe":(1000,500),"sofa":(2000,900),"coffee_table":(1200,600),
 "table":(1200,800),"chair":(450,450),"counter":(3000,600),"fridge":(700,700),
 "stove":(600,600),"sink":(500,400),"toilet":(400,700),"shower":(900,900),
}

def load_symbol(name):
    with open(os.path.join(BLOCKS_DIR, name+".svg")) as f:
        s = f.read()
    inner = re.sub(r'(?is)^.*?<svg[^>]*>', '', s)
    inner = re.sub(r'(?is)</svg>\s*$', '', inner)
    # recolorear: relleno fuera, trazo al color del proyecto
    inner = re.sub(r'fill="[^"]*"', 'fill="none"', inner)
    inner = re.sub(r'stroke="[^"]*"', 'stroke="currentColor"', inner)
    # engrosar trazo de mobiliario para que lea a escala de plano
    inner = re.sub(r'stroke-width="([\d.]+)"',
                   lambda m: f'stroke-width="{float(m.group(1))*3:.0f}"', inner)
    w,h = VB[name]
    return f'<symbol id="b_{name}" viewBox="0 0 {w} {h}" overflow="visible">{inner}</symbol>'

# --- placements: (bloque, x, y, ancho, alto, rot) en coords locales mm (y hacia abajo) ---
FURN = [
 # cocina
 ("counter", 120, 120, 1900, 560, 0),
 ("stove",   1250, 150, 520, 520, 0),
 ("fridge",  140, 900, 640, 640, 0),
 # bano
 ("toilet",  180, 3980, 380, 660, 0),
 ("sink",    760, 4000, 480, 380, 0),
 ("shower",  1180, 4560, 880, 880, 0),
 # comedor
 ("table",   3550, 780, 1200, 800, 0),
 ("chair",   3680, 250, 420, 420, 0),
 ("chair",   4200, 250, 420, 420, 0),
 ("chair",   3680, 1650, 420, 420, 0),
 ("chair",   4200, 1650, 420, 420, 0),
 ("chair",   3150, 950, 420, 420, 90),
 ("chair",   4850, 950, 420, 420, 90),
 # sala
 ("sofa",    3200, 4650, 2000, 880, 0),
 ("coffee_table", 3600, 3820, 1200, 600, 0),
 # dormitorio 2
 ("bed",     360, 6100, 1400, 2000, 0),
 ("wardrobe",2000, 5820, 1000, 480, 0),
 # dormitorio 1
 ("bed",     3400, 6100, 1400, 2000, 0),
 ("wardrobe",5000, 5820, 1000, 480, 0),
]

USED = sorted(set(f[0] for f in FURN))
symbols = "\n".join(load_symbol(n) for n in USED)

def use(name,x,y,w,h,rot):
    t = f'translate({x} {y})'
    if rot: t += f' rotate({rot} {w/2} {h/2})'
    return f'<use href="#b_{name}" x="0" y="0" width="{w}" height="{h}" transform="{t}"/>'
uses = "\n".join(use(*f) for f in FURN)

# --- muros ---
AW, AH = 6000, 9000
EXT = f'<rect x="0" y="0" width="{AW}" height="{AH}" fill="none" stroke="currentColor" stroke-width="150"/>'
# particiones (lineas): (x1,y1,x2,y2)
PART = [
 (2200,0,2200,5600),        # servicios | living
 (0,2600,2200,2600),        # cocina | lavadero
 (0,3800,2200,3800),        # lavadero | bano
 (0,5600,6000,5600),        # superior | dormitorios
 (3000,5600,3000,9000),     # dorm2 | dorm1
]
walls = EXT + "".join(
  f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" stroke="currentColor" stroke-width="105" stroke-linecap="square"/>'
  for a,b,c,d in PART)

# --- vanos (punch del color de la hoja) + arco de barrido ---
# (orientacion 'v'/'h', pos_fija, desde, hasta)
DOORS = [
 ('h', 3600, 0, 0),   # entrada (pared superior) -> se maneja aparte
]
def punch_and_swing():
    out=[]
    # entrada en pared superior, x 3200..4100
    out.append(f'<rect x="3200" y="-80" width="900" height="160" fill="var(--sheet)"/>')
    out.append(f'<path d="M3200 0 A900 900 0 0 1 4100 0" fill="none" stroke="currentColor" stroke-width="30" opacity=".7"/>')
    # puerta cocina (pared vertical x=2200, y 900..1700)
    out.append(f'<rect x="2120" y="900" width="160" height="800" fill="var(--sheet)"/>')
    out.append(f'<path d="M2200 900 A800 800 0 0 1 2200 1700" fill="none" stroke="currentColor" stroke-width="30" opacity=".7"/>')
    # puerta bano (x=2200, y 4300..5100)
    out.append(f'<rect x="2120" y="4300" width="160" height="800" fill="var(--sheet)"/>')
    # puerta dorm2 (pared horizontal y=5600, x 900..1700)
    out.append(f'<rect x="900" y="5520" width="800" height="160" fill="var(--sheet)"/>')
    # puerta dorm1 (y=5600, x 4200..5000)
    out.append(f'<rect x="4200" y="5520" width="800" height="160" fill="var(--sheet)"/>')
    return "".join(out)
doors = punch_and_swing()

# --- labels ---
LABELS = [
 ("cocina",1100,1500),("lavadero",1100,3300),("baño",1100,4750),
 ("comedor",4300,2050),("sala",4900,5050),
 ("dormitorio 2",1500,7650),("dormitorio 1",4500,7650),
]
labels = "".join(
  f'<text x="{x}" y="{y}" text-anchor="middle" class="rlabel">{t}</text>' for t,x,y in LABELS)

# --- cotas + norte + escala (dentro del SVG) ---
extras = f'''
<!-- cota total ancho -->
<text x="{AW/2}" y="-260" text-anchor="middle" class="dim">6.00</text>
<line x1="0" y1="-180" x2="{AW}" y2="-180" stroke="var(--ink)" stroke-width="6"/>
<!-- cota total alto -->
<text x="-320" y="{AH/2}" text-anchor="middle" class="dim" transform="rotate(-90 -320 {AH/2})">9.00</text>
<line x1="-220" y1="0" x2="-220" y2="{AH}" stroke="var(--ink)" stroke-width="6"/>
'''

OX, OY = 900, 760
VBW, VBH = 8100, 10600
mode_default = "dark"

html = f'''<title>PL-01 · Edificio Olmedo — lámina branded</title>
<style>
  :root{{ --acc:#4f7fb0; }}
  *{{box-sizing:border-box;}} html,body{{margin:0;height:100%;}}
  .sheet{{ position:relative; min-height:100svh; padding:clamp(14px,3vw,30px);
    font-family:'Helvetica Neue',Helvetica,Arial,system-ui,sans-serif;
    --sheet:#0d0e10; --ink:#ECE8E0; --muted:#8A867C;
    background:var(--sheet); color:var(--ink); transition:background .4s,color .4s; }}
  .sheet[data-mode="light"]{{ --sheet:#F4F2EC; --ink:#1A1918; --muted:#7C766B; }}
  .wrap{{ max-width:1100px; margin:0 auto; }}
  .plan{{ width:100%; height:auto; display:block; }}
  .plan text.rlabel{{ font-size:230px; letter-spacing:6px; fill:var(--ink); opacity:.85;
    font-family:'Helvetica Neue',Arial,sans-serif; }}
  .plan text.dim{{ font-size:200px; fill:var(--muted); font-family:ui-monospace,Menlo,monospace; }}

  .head{{ display:flex; align-items:baseline; justify-content:space-between; gap:16px;
    border-bottom:2px solid var(--ink); padding-bottom:10px; margin-bottom:6px; flex-wrap:wrap; }}
  .head h1{{ margin:0; font-size:clamp(20px,3.2vw,30px); font-weight:800; letter-spacing:-.01em; text-transform:uppercase; }}
  .head .sub{{ font-family:ui-monospace,Menlo,monospace; font-size:12px; letter-spacing:.14em;
    text-transform:uppercase; color:var(--muted); }}

  .foot{{ display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap;
    border-top:1px solid var(--muted); margin-top:6px; padding-top:12px;
    font-family:ui-monospace,Menlo,monospace; font-size:12px; letter-spacing:.1em;
    text-transform:uppercase; color:var(--muted); }}
  .foot b{{ color:var(--ink); font-weight:600; }}
  .scalebar{{ display:flex; align-items:center; gap:8px; }}
  .scalebar i{{ display:inline-block; width:90px; height:8px; background:var(--ink);
    border-left:2px solid var(--ink); border-right:2px solid var(--ink); }}

  .ctl{{ display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin:16px 0 10px; }}
  .chip{{ font-family:ui-monospace,Menlo,monospace; font-size:11px; letter-spacing:.06em;
    text-transform:uppercase; color:var(--ink); background:transparent;
    border:1px solid var(--muted); padding:7px 12px; border-radius:999px; cursor:pointer; transition:.2s; }}
  .chip[aria-pressed="true"]{{ background:var(--acc); border-color:var(--acc); color:#0d0e10; font-weight:700; }}
  .chip:hover{{ border-color:var(--acc); }}
  .sp{{ flex:1; }}
  .north{{ text-align:center; }}
</style>

<div class="sheet" data-mode="{mode_default}" id="sheet">
 <div class="wrap">

  <div class="ctl">
    <span class="sub" style="font-family:ui-monospace,Menlo,monospace;color:var(--muted)">COLOR DEL PROYECTO:</span>
    <button class="chip" data-c="#4f7fb0" aria-pressed="true">Hormigón</button>
    <button class="chip" data-c="#e0863a" aria-pressed="false">Atardecer</button>
    <button class="chip" data-c="#8caf3f" aria-pressed="false">Vegetación</button>
    <button class="chip" data-c="#a45cc9" aria-pressed="false">Noche</button>
    <button class="chip" data-c="#d8433a" aria-pressed="false">Brasa</button>
    <span class="sp"></span>
    <button class="chip" id="mode">Modo claro</button>
  </div>

  <div class="head">
    <h1>Edificio Olmedo</h1>
    <span class="sub">PL-01 · Planta tipo (depto) · ESC 1:75 aprox</span>
  </div>

  <svg class="plan" viewBox="0 0 {VBW} {VBH}" style="color:var(--acc)">
    <defs>{symbols}</defs>
    <g transform="translate({OX} {OY})">
      {extras}
      {walls}
      {doors}
      {uses}
    </g>
    <g transform="translate({OX} {OY})">
      {labels}
    </g>
    <!-- norte -->
    <g transform="translate({VBW-520} 360)" style="color:var(--acc)">
      <line x1="0" y1="220" x2="0" y2="-40" stroke="currentColor" stroke-width="26"/>
      <path d="M0 -90 L60 30 L-60 30 Z" fill="currentColor"/>
      <text x="0" y="-140" text-anchor="middle" class="dim" style="fill:var(--ink)">N</text>
    </g>
  </svg>

  <div class="foot">
    <div class="scalebar"><i></i><span>5 m</span></div>
    <div>AR STUDIO · アイコン · 2026</div>
    <div>COLOR · <b id="hex">#4F7FB0</b></div>
  </div>

 </div>
</div>

<script>
  const sheet=document.getElementById('sheet');
  const chips=[...document.querySelectorAll('.chip[data-c]')];
  function setC(hex){{ document.documentElement.style.setProperty('--acc',hex);
    document.getElementById('hex').textContent=hex.toUpperCase(); }}
  chips.forEach(c=>c.onclick=()=>{{ chips.forEach(x=>x.setAttribute('aria-pressed','false'));
    c.setAttribute('aria-pressed','true'); setC(c.dataset.c); }});
  const mb=document.getElementById('mode');
  mb.onclick=()=>{{ const m=sheet.getAttribute('data-mode')==='dark'?'light':'dark';
    sheet.setAttribute('data-mode',m); mb.textContent = m==='dark'?'Modo claro':'Modo oscuro'; }};
</script>
'''

with open(OUT,"w") as f:
    f.write(html)
print("OK ->", OUT, "| bloques usados:", USED)
