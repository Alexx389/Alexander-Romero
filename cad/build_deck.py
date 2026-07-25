import ezdxf, re, html as H
import ezdxf.bbox as bb
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing import svg, layout, config
F="/root/.claude/uploads/0f0a35b5-99e2-5d68-bef2-cda187185a16/3dc7b7c6-SALON_DPTO.OLMEDO_NUEVO.dxf"
GRISES=['#d3d3d3','#4c4c4c','#ffffff','#aeaeae','#a6a6a6','#f4f4f4']

def plan_svg(crop, weight=1100, margin=0.6):
    doc=ezdxf.readfile(F)
    for n in ["A-VIEWPORT","PRESENTACION","REVISION","Defpoints"]:
        if n in doc.layers: doc.layers.get(n).off()
    msp=doc.modelspace(); x0,y0,x1,y1=crop
    for e in list(msp):
        try:
            b=bb.extents([e],fast=True)
            if not b.has_data: msp.delete_entity(e); continue
            cx=(b.extmin.x+b.extmax.x)/2; cy=(b.extmin.y+b.extmax.y)/2
            if not (x0-margin<=cx<=x1+margin and y0-margin<=cy<=y1+margin): msp.delete_entity(e)
        except: pass
    ctx=RenderContext(doc); be=svg.SVGBackend()
    cfg=config.Configuration(background_policy=config.BackgroundPolicy.OFF,
        color_policy=config.ColorPolicy.MONOCHROME_DARK_BG, text_policy=config.TextPolicy.OUTLINE)
    Frontend(ctx,be,config=cfg).draw_layout(msp)
    s=be.get_string(layout.Page(0,0,layout.Units.mm,margins=layout.Margins.all(2)),
        settings=layout.Settings(fit_page=True, fixed_stroke_width=0.2))
    s=re.sub(r'stroke-width:\s*[\d.]+', f'stroke-width: {weight}', s)
    s=re.sub(r'fill:\s*#(?:d3d3d3|f4f4f4|ffffff|aeaeae|a6a6a6)', 'fill: none', s)
    for c in GRISES: s=s.replace(c,'currentColor')
    return re.sub(r'(<svg[^>]*?)width="[^"]*"\s*height="[^"]*"', r'\1width="100%"', s, count=1)

SLIDES=[
 dict(num="01", tit="Planta Alta", sub="Nivel superior · 4 departamentos (2 dorm. c/u)",
      cap="Cuatro unidades espejadas de a pares. Cada departamento integra cocina, comedor y sala, con lavadero, baño y dos dormitorios. Escalera central de acceso. Envolvente 24.00 × 12.90 m.",
      crop=(20,66,46,84.5)),
 dict(num="02", tit="Planta Baja", sub="Nivel acceso · salón comercial + estacionamiento",
      cap="Dos salones comerciales con accesos independientes (entrada 1 y 2), módulos de estacionamiento y servicios existentes (vivienda y lavadero). Linderos acotados: 24.00 × 28.20 m.",
      crop=(48,53,81,86)),
]
for s in SLIDES: s["svg"]=plan_svg(s["crop"])

slides_html=""
for i,s in enumerate(SLIDES):
    slides_html+=f'''<section class="slide" data-i="{i}">
      <div class="cap">
        <div class="num">{s['num']}<span>/ {len(SLIDES):02d}</span></div>
        <h2>{H.escape(s['tit'])}</h2>
        <div class="sub">{H.escape(s['sub'])}</div>
        <p>{H.escape(s['cap'])}</p>
      </div>
      <div class="planbox">{s['svg']}</div>
    </section>'''

deck=f'''<title>Edificio Olmedo — Plantas (deck)</title>
<style>
  :root{{ --acc:#4f7fb0; }}
  *{{box-sizing:border-box;}} html,body{{margin:0;height:100%;}}
  .deck{{ position:relative; min-height:100svh; overflow:hidden;
    font-family:'Helvetica Neue',Helvetica,Arial,system-ui,sans-serif;
    --paper:#0c0d0f; --ink:#ECE8E0; --muted:#8A867C; --line:rgba(255,255,255,.14);
    background:var(--paper); color:var(--ink); transition:background .4s,color .4s;
    display:flex; flex-direction:column; }}
  .deck[data-mode="light"]{{ --paper:#F4F2EC; --ink:#1A1918; --muted:#7C766B; --line:rgba(0,0,0,.16); }}
  .top{{ display:flex; align-items:center; justify-content:space-between; gap:12px;
    padding:16px clamp(16px,3vw,34px); font-size:11px; letter-spacing:.22em;
    text-transform:uppercase; font-weight:300; border-bottom:1px solid var(--line); }}
  .top .mid{{ color:var(--muted); }}
  .stage{{ flex:1; position:relative; }}
  .slide{{ position:absolute; inset:0; display:grid; grid-template-columns:minmax(240px,.8fr) 1.6fr;
    gap:clamp(16px,3vw,40px); align-items:center; padding:clamp(16px,3vw,40px);
    opacity:0; visibility:hidden; transition:opacity .45s ease; }}
  .slide.on{{ opacity:1; visibility:visible; }}
  @media (max-width:820px){{ .slide{{ grid-template-columns:1fr; align-content:center; overflow:auto; }} }}
  .cap .num{{ font-weight:200; font-size:clamp(40px,7vw,84px); line-height:.85; letter-spacing:-.02em; }}
  .cap .num span{{ font-size:.28em; color:var(--muted); letter-spacing:.1em; margin-left:.3em; }}
  .cap h2{{ margin:.2em 0 .1em; font-size:clamp(22px,3.4vw,40px); font-weight:800; letter-spacing:-.02em; text-transform:uppercase; }}
  .cap .sub{{ font-family:ui-monospace,Menlo,monospace; font-size:12px; letter-spacing:.08em;
    text-transform:uppercase; color:var(--acc); margin-bottom:14px; transition:color .4s; }}
  .cap p{{ font-size:14px; line-height:1.6; color:var(--muted); max-width:42ch; }}
  .planbox{{ color:var(--acc); }} .planbox svg{{ width:100%; height:auto; max-height:74vh; display:block; }}
  .bottom{{ display:flex; align-items:center; gap:12px; flex-wrap:wrap;
    padding:12px clamp(16px,3vw,34px); border-top:1px solid var(--line); }}
  .chips{{ display:flex; gap:7px; flex-wrap:wrap; align-items:center; }}
  .lbl{{ font-family:ui-monospace,Menlo,monospace; font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-right:4px; }}
  .chip{{ font-family:ui-monospace,Menlo,monospace; font-size:11px; letter-spacing:.06em; text-transform:uppercase;
    color:var(--ink); background:transparent; border:1px solid var(--line); padding:6px 11px; border-radius:999px; cursor:pointer; transition:.2s; }}
  .chip[aria-pressed="true"]{{ background:var(--acc); border-color:var(--acc); color:var(--paper); font-weight:700; }}
  .chip:hover{{ border-color:var(--acc); }}
  .sp{{ flex:1; }}
  .nav{{ display:flex; align-items:center; gap:10px; font-family:ui-monospace,Menlo,monospace; font-size:13px; }}
  .nav button{{ width:38px; height:38px; border-radius:50%; border:1px solid var(--line);
    background:transparent; color:var(--ink); cursor:pointer; font-size:16px; transition:.2s; }}
  .nav button:hover{{ border-color:var(--acc); color:var(--acc); }}
  .count{{ color:var(--muted); letter-spacing:.1em; min-width:56px; text-align:center; }}
</style>
<div class="deck" data-mode="dark" id="deck">
  <div class="top"><span>AR STUDIO</span><span class="mid">Edificio Olmedo · Plantas</span><span>アイコン 2026</span></div>
  <div class="stage" id="stage">{slides_html}</div>
  <div class="bottom">
    <div class="chips"><span class="lbl">Color:</span>
      <button class="chip" data-c="#4f7fb0" aria-pressed="true">Hormigón</button>
      <button class="chip" data-c="#e0863a">Atardecer</button>
      <button class="chip" data-c="#8caf3f">Vegetación</button>
      <button class="chip" data-c="#a45cc9">Noche</button>
      <button class="chip" data-c="#d8433a">Brasa</button>
      <button class="chip" id="mode" style="margin-left:6px">Modo claro</button>
    </div>
    <div class="sp"></div>
    <div class="nav"><button id="prev">‹</button><span class="count" id="count">01 / {len(SLIDES):02d}</span><button id="next">›</button></div>
  </div>
</div>
<script>
  const N={len(SLIDES)}; let i=0;
  const slides=[...document.querySelectorAll('.slide')];
  const count=document.getElementById('count');
  function show(k){{ i=(k+N)%N; slides.forEach((s,j)=>s.classList.toggle('on',j===i));
    count.textContent=String(i+1).padStart(2,'0')+' / '+String(N).padStart(2,'0'); }}
  document.getElementById('prev').onclick=()=>show(i-1);
  document.getElementById('next').onclick=()=>show(i+1);
  addEventListener('keydown',e=>{{ if(e.key==='ArrowRight')show(i+1); if(e.key==='ArrowLeft')show(i-1); }});
  const deck=document.getElementById('deck');
  const chips=[...document.querySelectorAll('.chip[data-c]')];
  chips.forEach(c=>c.onclick=()=>{{ chips.forEach(x=>x.setAttribute('aria-pressed','false'));
    c.setAttribute('aria-pressed','true'); document.documentElement.style.setProperty('--acc',c.dataset.c); }});
  const mb=document.getElementById('mode');
  mb.onclick=()=>{{ const m=deck.getAttribute('data-mode')==='dark'?'light':'dark';
    deck.setAttribute('data-mode',m); mb.textContent=m==='dark'?'Modo claro':'Modo oscuro'; }};
  show(0);
</script>'''
open("/home/user/Alexander-Romero/cad/deck-olmedo.html","w").write(deck)
print("OK deck bytes:", len(deck))
