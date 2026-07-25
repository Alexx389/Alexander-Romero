# Builder del deck de Edificio Olmedo (line-art tenible).
# Puertas redibujadas bold, ventanas y cotas de abertura desde textos, etiquetas crisp.

import ezdxf, re, os, math
import ezdxf.bbox as bb
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing import svg, layout, config
F="/root/.claude/uploads/0f0a35b5-99e2-5d68-bef2-cda187185a16/3dc7b7c6-SALON_DPTO.OLMEDO_NUEVO.dxf"
BLK="/home/user/Alexander-Romero/cad/blocks/default"
GR=['#d3d3d3','#4c4c4c','#ffffff','#aeaeae','#a6a6a6','#f4f4f4']
VBd={"bed":(1400,2000),"sofa":(2000,900),"table":(1200,800),"fridge":(700,700),
     "stove":(600,600),"sink":(500,400),"toilet":(400,700),"shower":(900,900),"chair":(450,450)}
REPLACE={'Cama1p~1':'bed','Cama2plaComp3_160':'bed','sofa':'sofa','Heladpl':'fridge',
         'A$C492F21F0':'stove','bacha':'sink','1bacha3':'sink','1wc2':'toilet','Duchapl1':'shower'}
TABLE={'MESA'}; WASHER={'LAVARROPA'}
KEEP={'ventanna','v0.6','*U62','pil'}
DOORS={'puert-080':0.80,'puert-070':0.70,'puerta aula':0.80,'*U52':0.80}
NAT={'sink':(0.5,0.4),'toilet':(0.4,0.7),'shower':(0.9,0.9),'fridge':(0.7,0.7),'stove':(0.6,0.6)}
BEDSZ={'Cama1p~1':(0.95,1.90),'Cama2plaComp3_160':(1.60,2.00)}
DOORW={0.70,0.80}
FSTROKE="0.9"   # grosor de muebles (px, no escala)

def load_sym(t):
    s=open(os.path.join(BLK,t+".svg")).read()
    inner=re.sub(r'(?is)^.*?<svg[^>]*>','',s); inner=re.sub(r'(?is)</svg>\s*$','',inner)
    inner=re.sub(r'fill="[^"]*"','fill="none"',inner)
    inner=re.sub(r'stroke="[^"]*"','stroke="currentColor"',inner)
    inner=re.sub(r'stroke-width="[^"]*"',f'stroke-width="{FSTROKE}" vector-effect="non-scaling-stroke"',inner)
    w,h=VBd[t]
    return f'<symbol id="pc_{t}" viewBox="0 0 {w} {h}" overflow="visible">{inner}</symbol>'

def render_walls(crop, weight=1600, margin=0.6):
    doc=ezdxf.readfile(F)
    SKIP={"A-VIEWPORT","PRESENTACION","REVISION","Defpoints"}
    msp=doc.modelspace(); x0,y0,x1,y1=crop
    furn=[]; labels=[]; wintexts=[]; doors=[]; apdims=[]
    TOPY=-1e9; BOTY=1e9; LEFTX=1e9; RIGHTX=-1e9
    for e in msp.query('LINE[layer=="A-MURO"]'):
        for pt in (e.dxf.start, e.dxf.end):
            if x0<=pt.x<=x1 and y0<=pt.y<=y1:
                TOPY=max(TOPY,pt.y); BOTY=min(BOTY,pt.y); LEFTX=min(LEFTX,pt.x); RIGHTX=max(RIGHTX,pt.x)
    # ventanas desde textos de medida
    for e in list(msp.query('TEXT'))+list(msp.query('MTEXT')):
        t=(e.dxf.text if e.dxftype()=='TEXT' else e.text).strip()
        p=e.dxf.insert
        if not(x0<=p.x<=x1 and y0<=p.y<=y1): continue
        m=re.match(r'^(\d\.\d+)x(\d\.\d+)', t)
        if not m: continue
        w=float(m.group(1)); h=float(m.group(2))
        hgt=(e.dxf.height if e.dxftype()=='TEXT' else e.dxf.char_height)
        apdims.append((t, p.x, p.y, hgt, e.dxf.rotation))
        if not (w in DOORW and abs(h-2.10)<0.2):
            wintexts.append((p.x,p.y,w))
        msp.delete_entity(e)
    wins=[]
    for (tx,ty,w) in wintexts:
        d={'h_t':abs(TOPY-ty),'h_b':abs(ty-BOTY),'v_l':abs(tx-LEFTX),'v_r':abs(RIGHTX-tx)}
        k=min(d,key=d.get)
        if k=='h_t': wins.append(('h',tx,TOPY,w))
        elif k=='h_b': wins.append(('h',tx,BOTY,w))
        elif k=='v_l': wins.append(('v',LEFTX,ty,w))
        else: wins.append(('v',RIGHTX,ty,w))
    # borrar/registrar
    for e in list(msp):
        try:
            if e.dxf.layer in SKIP: msp.delete_entity(e); continue
            # etiquetas de zona (texto con palabras) -> las redibujo crisp
            if e.dxftype() in ('TEXT','MTEXT'):
                t=(e.dxf.text if e.dxftype()=='TEXT' else e.text).strip()
                p=e.dxf.insert
                if re.search(r'[A-Za-zÁÉÍÓÚÜÑáéíóúñ]{3,}', t) and x0<=p.x<=x1 and y0<=p.y<=y1:
                    hh=(e.dxf.height if e.dxftype()=='TEXT' else e.dxf.char_height)
                    labels.append((t, p.x, p.y, hh)); msp.delete_entity(e); continue
            b=bb.extents([e],fast=True)
            if not b.has_data: msp.delete_entity(e); continue
            cx=(b.extmin.x+b.extmax.x)/2; cy=(b.extmin.y+b.extmax.y)/2
            keep=(x0-margin<=cx<=x1+margin and y0-margin<=cy<=y1+margin)
            if e.dxftype()=='INSERT':
                n=e.dxf.name
                if n in DOORS:
                    if keep: doors.append(dict(x=e.dxf.insert.x, y=e.dxf.insert.y,
                        rot=e.dxf.rotation, mir=(e.dxf.xscale<0), w=DOORS[n]))
                    msp.delete_entity(e); continue
                if n in KEEP:
                    if not keep: msp.delete_entity(e)
                    continue
                if keep and (n in REPLACE or n in TABLE or n in WASHER):
                    furn.append(dict(name=n, cx=cx, cy=cy, rot=e.dxf.rotation, mx=(e.dxf.xscale<0),
                                     fw=b.extmax.x-b.extmin.x, fh=b.extmax.y-b.extmin.y))
                msp.delete_entity(e); continue
            if not keep: msp.delete_entity(e)
        except: pass
    kb=bb.extents(msp,fast=True); K=(kb.extmin.x,kb.extmin.y,kb.extmax.x,kb.extmax.y)
    ctx=RenderContext(doc); be=svg.SVGBackend()
    cfg=config.Configuration(background_policy=config.BackgroundPolicy.OFF,
        color_policy=config.ColorPolicy.MONOCHROME_DARK_BG, text_policy=config.TextPolicy.OUTLINE)
    Frontend(ctx,be,config=cfg).draw_layout(msp)
    s=be.get_string(layout.Page(0,0,layout.Units.mm,margins=layout.Margins.all(0)),
        settings=layout.Settings(fit_page=True, fixed_stroke_width=0.2))
    s=re.sub(r'stroke-width:\s*[\d.]+', f'stroke-width: {weight}', s)
    for c in GR: s=s.replace(c,'currentColor')
    s=s.replace('fill: currentColor','fill: none')  # sin poché: line-art
    m=re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', s); VBW,VBH=float(m.group(1)),float(m.group(2))
    s=re.sub(r'(<svg[^>]*?)\swidth="[^"]*"\s*height="[^"]*"', r'\1', s, count=1)
    return s, K, VBW, VBH, furn, wins, labels, doors, apdims

def overlay(furn, wins, labels, doors, apdims, K, VBW):
    KX0,KY0,KX1,KY1=K; sx=VBW/(KX1-KX0)
    def P(x,y): return ((x-KX0)*sx, (KY1-y)*sx)
    def place(t,cx,cy,wm,hm,rot,mir):
        scx,scy=P(cx,cy); Wp=wm*sx; Hp=hm*sx; sgn=-1 if mir else 1
        return (f'<g transform="translate({scx:.0f},{scy:.0f}) rotate({-rot:.0f}) scale({sgn},1)">'
                f'<use href="#pc_{t}" x="{-Wp/2:.0f}" y="{-Hp/2:.0f}" width="{Wp:.0f}" height="{Hp:.0f}"/></g>')
    els=[]; used=set()
    # puertas (redibujadas bold, geometria del bloque del arquitecto)
    for d in doors:
        ins=(d['x'],d['y']); rot=d['rot']; mir=d['mir']; W=d['w']; hx,hy=0.04,0.15
        def tp(px,py):
            if mir: px=-px
            a=math.radians(rot); ca=math.cos(a); sa=math.sin(a)
            return P(ins[0]+px*ca-py*sa, ins[1]+px*sa+py*ca)
        L0=tp(hx,hy); L1=tp(hx,hy+W)
        arc=[tp(hx+W*math.cos(math.radians(90*k/14)), hy+W*math.sin(math.radians(90*k/14))) for k in range(15)]
        dleaf=f'M{L0[0]:.0f},{L0[1]:.0f} L{L1[0]:.0f},{L1[1]:.0f}'
        darc='M'+' L'.join(f'{p[0]:.0f},{p[1]:.0f}' for p in arc)
        els.append(f'<path d="{dleaf} {darc}" fill="none" stroke="currentColor" '
                   f'stroke-width="1.7" vector-effect="non-scaling-stroke"/>')
    # ventanas
    for (kind,X,Y,w) in wins:
        cxs,cys=P(X,Y); half=w/2*sx; th=0.06*sx
        st='stroke="currentColor" stroke-width="0.9" vector-effect="non-scaling-stroke"'
        if kind=='h':
            els.append(f'<g fill="none"><line x1="{cxs-half:.0f}" y1="{cys-th:.0f}" x2="{cxs+half:.0f}" y2="{cys-th:.0f}" {st}/>'
                f'<line x1="{cxs-half:.0f}" y1="{cys:.0f}" x2="{cxs+half:.0f}" y2="{cys:.0f}" {st}/>'
                f'<line x1="{cxs-half:.0f}" y1="{cys+th:.0f}" x2="{cxs+half:.0f}" y2="{cys+th:.0f}" {st}/>'
                f'<line x1="{cxs-half:.0f}" y1="{cys-th:.0f}" x2="{cxs-half:.0f}" y2="{cys+th:.0f}" {st}/>'
                f'<line x1="{cxs+half:.0f}" y1="{cys-th:.0f}" x2="{cxs+half:.0f}" y2="{cys+th:.0f}" {st}/></g>')
        else:
            els.append(f'<g fill="none"><line x1="{cxs-th:.0f}" y1="{cys-half:.0f}" x2="{cxs-th:.0f}" y2="{cys+half:.0f}" {st}/>'
                f'<line x1="{cxs:.0f}" y1="{cys-half:.0f}" x2="{cxs:.0f}" y2="{cys+half:.0f}" {st}/>'
                f'<line x1="{cxs+th:.0f}" y1="{cys-half:.0f}" x2="{cxs+th:.0f}" y2="{cys+half:.0f}" {st}/>'
                f'<line x1="{cxs-th:.0f}" y1="{cys-half:.0f}" x2="{cxs+th:.0f}" y2="{cys-half:.0f}" {st}/>'
                f'<line x1="{cxs-th:.0f}" y1="{cys+half:.0f}" x2="{cxs+th:.0f}" y2="{cys+half:.0f}" {st}/></g>')
    # muebles: separar camas y deduplicar la cama doble (dos mitades)
    beds=[it for it in furn if REPLACE.get(it['name'])=='bed']
    rest=[it for it in furn if REPLACE.get(it['name'])!='bed']
    usedb=set(); bedplaced=[]
    for i,b in enumerate(beds):
        if i in usedb: continue
        grp=[b]
        for j in range(i+1,len(beds)):
            if j not in usedb and abs(beds[j]['cx']-b['cx'])<0.45 and abs(beds[j]['cy']-b['cy'])<0.45:
                grp.append(beds[j]); usedb.add(j)
        usedb.add(i)
        cx=sum(g['cx'] for g in grp)/len(grp); cy=sum(g['cy'] for g in grp)/len(grp)
        w,h=BEDSZ.get(b['name'],(1.4,2.0))
        bedplaced.append(dict(cx=cx,cy=cy,w=w,h=h,rot=b['rot'],mx=b['mx']))
    used.add('bed')
    for bp in bedplaced:
        r=bp['rot']%360; rotd=abs(r-90)<45 or abs(r-270)<45
        wm,hm=(bp['h'],bp['w']) if False else (bp['w'],bp['h'])  # tamaño natural, se rota por transform
        els.append(place('bed',bp['cx'],bp['cy'],wm,hm,bp['rot'],bp['mx']))
    for it in rest:
        n=it['name']; cx,cy=it['cx'],it['cy']; rot=it['rot']; mir=it['mx']; fw,fh=it['fw'],it['fh']
        r=rot%360; rotd=abs(r-90)<45 or abs(r-270)<45
        if n in REPLACE:
            t=REPLACE[n]; used.add(t)
            if t in NAT: wm,hm=NAT[t]
            else: wm,hm=(fh,fw) if rotd else (fw,fh)
            els.append(place(t,cx,cy,wm,hm,rot,mir))
        elif n in TABLE:
            used.add('table'); used.add('chair')
            scx,scy=P(cx,cy); sgn=-1 if mir else 1
            g=[f'<g transform="translate({scx:.0f},{scy:.0f}) rotate({-rot:.0f}) scale({sgn},1)">']
            tw,th2=1.40*sx,0.85*sx
            g.append(f'<use href="#pc_table" x="{-tw/2:.0f}" y="{-th2/2:.0f}" width="{tw:.0f}" height="{th2:.0f}"/>')
            cw=0.45*sx
            for (dx,dy) in [(-0.40,-0.62),(0.40,-0.62),(-0.40,0.62),(0.40,0.62),(-0.92,0),(0.92,0)]:
                g.append(f'<use href="#pc_chair" x="{dx*sx-cw/2:.0f}" y="{dy*sx-cw/2:.0f}" width="{cw:.0f}" height="{cw:.0f}"/>')
            g.append('</g>'); els.append("".join(g))
        elif n in WASHER:
            w,h=fw*sx,fh*sx; scx,scy=P(cx,cy)
            els.append(f'<g fill="none" stroke="currentColor">'
                f'<rect x="{scx-w/2:.0f}" y="{scy-h/2:.0f}" width="{w:.0f}" height="{h:.0f}" rx="4" stroke-width="0.9" vector-effect="non-scaling-stroke"/>'
                f'<circle cx="{scx:.0f}" cy="{scy:.0f}" r="{min(w,h)*0.30:.0f}" stroke-width="0.9" vector-effect="non-scaling-stroke"/></g>')
    # etiquetas de zona (crisp, solidas)
    for (t,x,y,h) in labels:
        scx,scy=P(x,y); fs=h*sx*1.35
        els.append(f'<text x="{scx:.0f}" y="{scy:.0f}" font-size="{fs:.0f}" fill="currentColor" '
                   f'font-family="Helvetica,Arial,sans-serif" font-weight="500">{t}</text>')
    # cotas de abertura (crisp, solidas, respetando rotacion)
    for (t,x,y,h,rot) in apdims:
        scx,scy=P(x,y); fs=max(h*sx*1.4, 0.16*sx)
        els.append(f'<text transform="translate({scx:.0f},{scy:.0f}) rotate({-rot:.0f})" '
                   f'font-size="{fs:.0f}" fill="currentColor" font-family="Helvetica,Arial,sans-serif">{t}</text>')
    defs="".join(load_sym(t) for t in sorted(used))
    return f'<defs>{defs}</defs><g>'+"".join(els)+'</g>'

import re, json

def inner(s):
    s=re.sub(r'<\?xml[^?]*\?>','',s).strip()
    s=re.sub(r'^<svg[^>]*>','',s,count=1); s=re.sub(r'</svg>\s*$','',s,count=1)
    return s

def plan(crop):
    walls,K,VBW,VBH,furn,wins,labels,doors,apdims = render_walls(crop)
    ov = overlay(furn,wins,labels,doors,apdims,K,VBW)
    svg = re.sub(r'</svg>\s*$', ov+'</svg>', walls, count=1)
    return dict(svg=svg, K=K, VBW=VBW, VBH=VBH)

PA=plan((19,65,47,85)); PB=plan((48,53,81,86))
KX0,KY0,KX1,KY1=PA["K"]; VBW=PA["VBW"]; sx=VBW/(KX1-KX0)
def vb(r):
    a,b,c,d=r
    return [round((a-KX0)*sx,1), round((KY1-d)*sx,1), round((c-a)*sx,1), round((d-b)*sx,1)]

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
      cap="Segundo dormitorio con dos camas y placard. Comparte el muro de fondo y recibe luz y ventilación por ventana de 1.50 × 2.10 m al contrafrente. Puerta de 0.80 m."),
 dict(plan="PB", vbx=None, num="08", tit="Planta Baja", sub="Nivel acceso · salón comercial + estacionamiento",
      cap="Dos salones comerciales con accesos independientes (entrada 1 y 2), módulos de estacionamiento y servicios existentes. Linderos acotados: 24.00 × 28.20 m."),
]
N=len(VIEWS)
views_js=json.dumps([{k:v[k] for k in ("plan","vbx","num","tit","sub","cap")} for v in VIEWS], ensure_ascii=False)
PAvb=f"0 0 {PA['VBW']:.0f} {PA['VBH']:.0f}"; PBvb=f"0 0 {PB['VBW']:.0f} {PB['VBH']:.0f}"

deck=f'''<title>Edificio Olmedo — Plantas + secciones</title>
<style>
  :root{{ --acc:#4f7fb0; }}
  *{{box-sizing:border-box;}} html,body{{margin:0;height:100%;}}
  .deck{{ position:relative; min-height:100svh; overflow:hidden;
    font-family:'Helvetica Neue',Helvetica,Arial,system-ui,sans-serif;
    --paper:#0c0d0f; --ink:#ECE8E0; --muted:#8A867C; --line:rgba(255,255,255,.14);
    background:var(--paper); color:var(--ink); transition:background .4s,color .4s; display:flex; flex-direction:column; }}
  .deck[data-mode="light"]{{ --paper:#F4F2EC; --ink:#1A1918; --muted:#7C766B; --line:rgba(0,0,0,.16); }}
  .top{{ display:flex; align-items:center; justify-content:space-between; gap:12px;
    padding:16px clamp(16px,3vw,34px); font-size:11px; letter-spacing:.22em; text-transform:uppercase; font-weight:300; border-bottom:1px solid var(--line); }}
  .top .mid{{ color:var(--muted); }}
  .stage{{ flex:1; display:grid; grid-template-columns:minmax(240px,.75fr) 1.6fr; gap:clamp(16px,3vw,40px); align-items:center; padding:clamp(16px,3vw,40px); }}
  @media (max-width:820px){{ .stage{{ grid-template-columns:1fr; align-content:center; overflow:auto; }} }}
  .cap .num{{ font-weight:200; font-size:clamp(40px,7vw,84px); line-height:.85; letter-spacing:-.02em; }}
  .cap .num span{{ font-size:.28em; color:var(--muted); letter-spacing:.1em; margin-left:.3em; }}
  .cap h2{{ margin:.2em 0 .1em; font-size:clamp(22px,3.2vw,38px); font-weight:800; letter-spacing:-.02em; text-transform:uppercase; text-wrap:balance; }}
  .cap .sub{{ font-family:ui-monospace,Menlo,monospace; font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--acc); margin-bottom:14px; transition:color .4s; }}
  .cap p{{ font-size:14px; line-height:1.65; color:var(--muted); max-width:44ch; }}
  .planwrap{{ position:relative; height:78vh; display:flex; align-items:center; justify-content:center; color:var(--acc); }}
  .planwrap svg{{ max-width:100%; max-height:100%; width:auto; height:auto; display:none; }}
  .planwrap svg.on{{ display:block; }}
  .bottom{{ display:flex; align-items:center; gap:12px; flex-wrap:wrap; padding:12px clamp(16px,3vw,34px); border-top:1px solid var(--line); }}
  .lbl{{ font-family:ui-monospace,Menlo,monospace; font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-right:4px; }}
  .chip{{ font-family:ui-monospace,Menlo,monospace; font-size:11px; letter-spacing:.06em; text-transform:uppercase;
    color:var(--ink); background:transparent; border:1px solid var(--line); padding:6px 11px; border-radius:999px; cursor:pointer; transition:.2s; }}
  .chip[aria-pressed="true"]{{ background:var(--acc); border-color:var(--acc); color:var(--paper); font-weight:700; }}
  .chip:hover{{ border-color:var(--acc); }}
  .sp{{ flex:1; }}
  .nav{{ display:flex; align-items:center; gap:10px; font-family:ui-monospace,Menlo,monospace; font-size:13px; }}
  .nav button{{ width:38px; height:38px; border-radius:50%; border:1px solid var(--line); background:transparent; color:var(--ink); cursor:pointer; font-size:16px; transition:.2s; }}
  .nav button:hover{{ border-color:var(--acc); color:var(--acc); }}
  .count{{ color:var(--muted); letter-spacing:.1em; min-width:56px; text-align:center; }}
</style>
<div class="deck" data-mode="dark" id="deck">
  <div class="top"><span>AR STUDIO</span><span class="mid">Edificio Olmedo</span><span>アイコン 2026</span></div>
  <div class="stage">
    <div class="cap"><div class="num" id="num">01<span id="of">/ {N:02d}</span></div>
      <h2 id="tit">—</h2><div class="sub" id="sub">—</div><p id="cap">—</p></div>
    <div class="planwrap">
      <svg id="planPA" viewBox="{PAvb}" preserveAspectRatio="xMidYMid meet">{inner(PA['svg'])}</svg>
      <svg id="planPB" viewBox="{PBvb}" preserveAspectRatio="xMidYMid meet">{inner(PB['svg'])}</svg>
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
  const PAfull="{PAvb}", PBfull="{PBvb}";
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
    (usePA?planPA:planPB).setAttribute('viewBox', v.vbx? v.vbx.join(' ') : (usePA?PAfull:PBfull));
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
print("OK deck bytes:", len(deck))
