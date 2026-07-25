import ezdxf, re, html as H, json
import ezdxf.bbox as bb
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing import svg, layout, config
F="/root/.claude/uploads/0f0a35b5-99e2-5d68-bef2-cda187185a16/3dc7b7c6-SALON_DPTO.OLMEDO_NUEVO.dxf"
GR=['#d3d3d3','#4c4c4c','#ffffff','#aeaeae','#a6a6a6','#f4f4f4']

def render(crop, weight=1100, margin=0.6):
    doc=ezdxf.readfile(F)
    SKIP={"A-VIEWPORT","PRESENTACION","REVISION","Defpoints"}
    msp=doc.modelspace(); x0,y0,x1,y1=crop
    for e in list(msp):
        try:
            if e.dxf.layer in SKIP: msp.delete_entity(e); continue
            b=bb.extents([e],fast=True)
            if not b.has_data: msp.delete_entity(e); continue
            cx=(b.extmin.x+b.extmax.x)/2; cy=(b.extmin.y+b.extmax.y)/2
            if not (x0-margin<=cx<=x1+margin and y0-margin<=cy<=y1+margin): msp.delete_entity(e)
        except: pass
    kb=bb.extents(msp, fast=True)
    KX0,KY0,KX1,KY1=kb.extmin.x,kb.extmin.y,kb.extmax.x,kb.extmax.y
    ctx=RenderContext(doc); be=svg.SVGBackend()
    cfg=config.Configuration(background_policy=config.BackgroundPolicy.OFF,
        color_policy=config.ColorPolicy.MONOCHROME_DARK_BG, text_policy=config.TextPolicy.OUTLINE)
    Frontend(ctx,be,config=cfg).draw_layout(msp)
    s=be.get_string(layout.Page(0,0,layout.Units.mm,margins=layout.Margins.all(0)),
        settings=layout.Settings(fit_page=True, fixed_stroke_width=0.2))
    s=re.sub(r'stroke-width:\s*[\d.]+', f'stroke-width: {weight}', s)
    s=re.sub(r'fill-opacity:\s*[\d.]+', 'fill-opacity: 0.26', s)
    for c in GR: s=s.replace(c,'currentColor')
    m=re.search(r'viewBox="([\d.\- ]+)"', s); VBW,VBH=[float(v) for v in m.group(2 if False else 1).split()[2:]]
    s=re.sub(r'(<svg[^>]*?)\swidth="[^"]*"\s*height="[^"]*"', r'\1', s, count=1)  # sacar width/height fijos
    return dict(svg=s, K=(KX0,KY0,KX1,KY1), VBW=VBW, VBH=VBH)

def inner(s):
    s=re.sub(r'<\?xml[^?]*\?>','',s).strip()
    s=re.sub(r'^<svg[^>]*>','',s,count=1)
    s=re.sub(r'</svg>\s*$','',s,count=1)
    return s

PA=render((19,65,47,85))
PB=render((48,53,81,86))
KX0,KY0,KX1,KY1=PA["K"]; VBW=PA["VBW"]
sx=VBW/(KX1-KX0)
def vb(r):
    rx0,ry0,rx1,ry1=r
    return [round((rx0-KX0)*sx,1), round((KY1-ry1)*sx,1), round((rx1-rx0)*sx,1), round((ry1-ry0)*sx,1)]

VIEWS=[
 dict(plan="PA", vbx=None, num="01", tit="Planta Alta", sub="Nivel superior · 4 departamentos",
      cap="Cuatro unidades espejadas de a pares. Escalera central de acceso. Envolvente 24.00 × 12.90 m."),
 dict(plan="PA", vbx=vb((20.7,67.0,26.95,80.6)), num="02", tit="Unidad tipo", sub="Departamento de 2 dormitorios",
      cap="La unidad se organiza en franjas: al frente cocina y comedor integrados; en el medio sala y baño; al fondo, dos dormitorios. El área húmeda (cocina · lavadero · baño) se alinea sobre un mismo eje para concentrar instalaciones."),
 dict(plan="PA", vbx=vb((22.35,73.7,26.95,80.6)), num="03", tit="Cocina · Comedor · Sala", sub="Núcleo social integrado · frente 4.08 m",
      cap="Ambiente único de 4.08 m de frente: la cocina se apoya sobre el muro húmedo (mesada, anafe y heladera) y se abre al comedor y a la sala. La continuidad visual amplía el espacio y favorece la ventilación cruzada hacia el frente."),
 dict(plan="PA", vbx=vb((20.6,76.1,22.75,80.6)), num="04", tit="Lavadero", sub="Servicio · frente 1.49 m",
      cap="Lavadero compacto contiguo a la cocina, sobre el muro de instalaciones. Aloja pileta y lavarropas, con acceso directo desde el área de cocina."),
 dict(plan="PA", vbx=vb((20.6,72.65,22.75,76.7)), num="05", tit="Baño", sub="Completo · profundidad 2.44 m",
      cap="Baño alineado con cocina y lavadero para compartir instalaciones sanitarias. Inodoro, bacha y ducha con blindex. Puerta de 0.70 m desde la circulación interna."),
 dict(plan="PA", vbx=vb((23.45,66.9,26.95,74.2)), num="06", tit="Dormitorio 1", sub="Principal · frente 2.78 m",
      cap="Dormitorio principal al fondo de la unidad. Espacio para cama de dos plazas y placard, con ventana de 1.50 × 2.10 m al contrafrente para luz y ventilación natural. Puerta de 0.80 m."),
 dict(plan="PA", vbx=vb((20.6,66.9,23.65,74.2)), num="07", tit="Dormitorio 2", sub="Secundario · frente 2.82 m",
      cap="Segundo dormitorio con cama y placard. Comparte el muro de fondo y recibe luz y ventilación por ventana de 1.50 × 2.10 m al contrafrente. Puerta de 0.80 m."),
 dict(plan="PB", vbx=None, num="08", tit="Planta Baja", sub="Nivel acceso · salón comercial + estacionamiento",
      cap="Dos salones comerciales con accesos independientes (entrada 1 y 2), módulos de estacionamiento y servicios existentes. Linderos acotados: 24.00 × 28.20 m."),
]
for i,v in enumerate(VIEWS): v["i"]=i
N=len(VIEWS)
views_js=json.dumps([{k:v[k] for k in ("plan","vbx","num","tit","sub","cap")} for v in VIEWS], ensure_ascii=False)

deck=f'''<title>Edificio Olmedo — Plantas + secciones</title>
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
  .stage{{ flex:1; display:grid; grid-template-columns:minmax(240px,.75fr) 1.6fr;
    gap:clamp(16px,3vw,40px); align-items:center; padding:clamp(16px,3vw,40px); }}
  @media (max-width:820px){{ .stage{{ grid-template-columns:1fr; align-content:center; overflow:auto; }} }}
  .cap .num{{ font-weight:200; font-size:clamp(40px,7vw,84px); line-height:.85; letter-spacing:-.02em; }}
  .cap .num span{{ font-size:.28em; color:var(--muted); letter-spacing:.1em; margin-left:.3em; }}
  .cap h2{{ margin:.2em 0 .1em; font-size:clamp(22px,3.2vw,38px); font-weight:800; letter-spacing:-.02em; text-transform:uppercase; text-wrap:balance; }}
  .cap .sub{{ font-family:ui-monospace,Menlo,monospace; font-size:12px; letter-spacing:.06em;
    text-transform:uppercase; color:var(--acc); margin-bottom:14px; transition:color .4s; }}
  .cap p{{ font-size:14px; line-height:1.65; color:var(--muted); max-width:44ch; }}
  .planwrap{{ position:relative; height:78vh; display:flex; align-items:center; justify-content:center; color:var(--acc); }}
  .planwrap svg{{ max-width:100%; max-height:100%; width:auto; height:auto; display:none; }}
  .planwrap svg.on{{ display:block; }}
  .bottom{{ display:flex; align-items:center; gap:12px; flex-wrap:wrap;
    padding:12px clamp(16px,3vw,34px); border-top:1px solid var(--line); }}
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
  <div class="top"><span>AR STUDIO</span><span class="mid">Edificio Olmedo</span><span>アイコン 2026</span></div>
  <div class="stage">
    <div class="cap">
      <div class="num" id="num">01<span id="of">/ {N:02d}</span></div>
      <h2 id="tit">—</h2><div class="sub" id="sub">—</div><p id="cap">—</p>
    </div>
    <div class="planwrap">
      <svg id="planPA" viewBox="0 0 {PA['VBW']:.0f} {PA['VBH']:.0f}" preserveAspectRatio="xMidYMid meet">{inner(PA['svg'])}</svg>
      <svg id="planPB" viewBox="0 0 {PB['VBW']:.0f} {PB['VBH']:.0f}" preserveAspectRatio="xMidYMid meet">{inner(PB['svg'])}</svg>
    </div>
  </div>
  <div class="bottom">
    <span class="lbl">Color:</span>
    <button class="chip" data-c="#4f7fb0" aria-pressed="true">Hormigón</button>
    <button class="chip" data-c="#e0863a">Atardecer</button>
    <button class="chip" data-c="#8caf3f">Vegetación</button>
    <button class="chip" data-c="#a45cc9">Noche</button>
    <button class="chip" data-c="#d8433a">Brasa</button>
    <button class="chip" id="mode" style="margin-left:6px">Modo claro</button>
    <div class="sp"></div>
    <div class="nav"><button id="prev">‹</button><span class="count" id="count">01 / {N:02d}</span><button id="next">›</button></div>
  </div>
</div>
<script>
  const VIEWS={views_js}, N=VIEWS.length;
  const PAfull="0 0 {PA['VBW']:.0f} {PA['VBH']:.0f}", PBfull="0 0 {PB['VBW']:.0f} {PB['VBH']:.0f}";
  const planPA=document.getElementById('planPA'), planPB=document.getElementById('planPB');
  let i=0;
  function show(k){{ i=(k+N)%N; const v=VIEWS[i];
    document.getElementById('num').firstChild.textContent=v.num;
    document.getElementById('tit').textContent=v.tit;
    document.getElementById('sub').textContent=v.sub;
    document.getElementById('cap').textContent=v.cap;
    document.getElementById('count').textContent=v.num+' / '+String(N).padStart(2,'0');
    const usePA=v.plan==='PA';
    planPA.classList.toggle('on',usePA); planPB.classList.toggle('on',!usePA);
    const el=usePA?planPA:planPB;
    el.setAttribute('viewBox', v.vbx? v.vbx.join(' ') : (usePA?PAfull:PBfull));
  }}
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
print("OK bytes:", len(deck), "| PA VB:", PA["VBW"],PA["VBH"], "| baño vb:", vb((20.6,72.65,22.75,76.7)))
