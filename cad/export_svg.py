# Builder del deck de Edificio Olmedo (line-art tenible).
# Puertas redibujadas bold, ventanas y cotas de abertura desde textos, etiquetas crisp.
# Simbolos de ducha/heladera propios; ventanas ubicadas sobre el muro mas cercano al vano.

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
         'A$C492F21F0':'stove','1bacha3':'sink','1wc2':'toilet','Duchapl1':'shower'}
# 'bacha' (bacha de cocina) NO se reemplaza: el DXF ya trae un dibujo limpio de la pileta.
TABLE={'MESA'}; WASHER={'LAVARROPA'}
KEEP={'ventanna','v0.6','*U62','pil'}
DOORS={'puert-080':0.80,'puert-070':0.70,'puerta aula':0.80,'*U52':0.80}
NAT={'sink':(0.5,0.4),'toilet':(0.4,0.7),'shower':(0.85,0.85),'fridge':(0.7,0.7),'stove':(0.6,0.6)}
BEDSZ={'Cama1p~1':(0.95,1.90),'Cama2plaComp3_160':(1.60,2.00)}
DOORW={0.70,0.80}
FSTROKE="0.9"   # grosor de muebles (px, no escala)
_VE='vector-effect="non-scaling-stroke"'
CUSTOM={
 'shower': f'<symbol id="pc_shower" viewBox="0 0 900 900" overflow="visible">'
   f'<rect x="30" y="30" width="840" height="840" fill="none" stroke="currentColor" stroke-width="{FSTROKE}" {_VE}/>'
   f'<line x1="30" y1="30" x2="870" y2="870" stroke="currentColor" stroke-width="{FSTROKE}" {_VE}/>'
   f'<circle cx="450" cy="450" r="55" fill="none" stroke="currentColor" stroke-width="{FSTROKE}" {_VE}/></symbol>',
 'fridge': f'<symbol id="pc_fridge" viewBox="0 0 700 700" overflow="visible">'
   f'<rect x="30" y="30" width="640" height="640" fill="none" stroke="currentColor" stroke-width="{FSTROKE}" {_VE}/>'
   f'<line x1="30" y1="210" x2="670" y2="210" stroke="currentColor" stroke-width="{FSTROKE}" {_VE}/>'
   f'<line x1="560" y1="90" x2="560" y2="160" stroke="currentColor" stroke-width="{FSTROKE}" {_VE}/></symbol>',
}

def load_sym(t):
    if t in CUSTOM: return CUSTOM[t]
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
    WALLS=[]
    for e in msp.query('LINE[layer=="A-MURO"]'):
        a,b=e.dxf.start,e.dxf.end
        if (x0-2<=a.x<=x1+2 and y0-2<=a.y<=y1+2): WALLS.append((a.x,a.y,b.x,b.y))
    for e in msp.query('LWPOLYLINE[layer=="A-MURO"]'):
        pts=[(p[0],p[1]) for p in e.get_points()]
        if getattr(e,'closed',False) and len(pts)>2: pts=pts+[pts[0]]
        for i in range(len(pts)-1):
            a,b=pts[i],pts[i+1]
            if (x0-2<=a[0]<=x1+2 and y0-2<=a[1]<=y1+2): WALLS.append((a[0],a[1],b[0],b[1]))
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
    # Una abertura es un HUECO en el muro, asi que no sirve el segmento mas cercano
    # (puede ganar un muro perpendicular). Clasifico segmentos por orientacion y
    # ubico la ventana sobre la LINEA de muro (horizontal o vertical) mas cercana en
    # perpendicular, tolerando el hueco con una ventana de +/-4 m a lo largo del muro.
    HSEGS=[]; VSEGS=[]
    for (ax,ay,bx,by) in WALLS:
        dx=bx-ax; dy=by-ay
        if abs(dx)>=abs(dy): HSEGS.append((min(ax,bx),max(ax,bx),(ay+by)/2))
        else:                VSEGS.append((min(ay,by),max(ay,by),(ax+bx)/2))
    def near_h(tx,ty):
        best=None; bd=1e18
        for (a,b,y) in HSEGS:
            if a-4<=tx<=b+4:
                d=abs(ty-y)
                if d<bd: bd=d; best=y
        return best,bd
    def near_v(tx,ty):
        best=None; bd=1e18
        for (a,b,x) in VSEGS:
            if a-4<=ty<=b+4:
                d=abs(tx-x)
                if d<bd: bd=d; best=x
        return best,bd
    wins=[]
    for (tx,ty,w) in wintexts:
        hy,dh=near_h(tx,ty); vx,dv=near_v(tx,ty)
        if hy is not None and (vx is None or dh<=dv):
            wins.append((tx,hy,1.0,0.0,w))   # sobre muro horizontal
        elif vx is not None:
            wins.append((vx,ty,0.0,1.0,w))   # sobre muro vertical
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
        color_policy=config.ColorPolicy.MONOCHROME_DARK_BG, text_policy=config.TextPolicy.OUTLINE,
        hatch_policy=config.HatchPolicy.SHOW_OUTLINE)
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
    # ventanas: sobre el muro (segun direccion), en la posicion del vano
    st='stroke="currentColor" stroke-width="0.9" vector-effect="non-scaling-stroke"'
    for (cx,cy,ux,uy,w) in wins:
        thm=0.055
        ax,ay=cx-ux*w/2, cy-uy*w/2; bx,by=cx+ux*w/2, cy+uy*w/2
        px,py=-uy,ux
        def L(x1,y1,x2,y2):
            p1=P(x1,y1); p2=P(x2,y2)
            return f'<line x1="{p1[0]:.0f}" y1="{p1[1]:.0f}" x2="{p2[0]:.0f}" y2="{p2[1]:.0f}" {st}/>'
        seg=[L(ax+px*thm,ay+py*thm, bx+px*thm,by+py*thm),
             L(ax,ay, bx,by),
             L(ax-px*thm,ay-py*thm, bx-px*thm,by-py*thm),
             L(ax+px*thm,ay+py*thm, ax-px*thm,ay-py*thm),
             L(bx+px*thm,by+py*thm, bx-px*thm,by-py*thm)]
        els.append('<g fill="none">'+"".join(seg)+'</g>')
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


# ---- Exporta cada planta como SVG standalone editable (Illustrator/Inkscape/Figma) ----
def export_svg(crop, out, weight=900, wpx=2400):
    s,K,VBW,VBH,furn,wins,labels,doors,apdims = render_walls(crop, weight=weight)
    ov = overlay(furn,wins,labels,doors,apdims,K,VBW)
    svg = re.sub(r'</svg>\s*$', ov+'</svg>', s, count=1)
    svg = svg.replace('currentColor', '#1a1a1a')            # color explicito
    svg = re.sub(r'<svg ', f'<svg width="{wpx}" style="background:#ffffff" ', svg, count=1)
    open(out,'w').write(svg); print("OK", out, len(svg))

if __name__=="__main__":
    export_svg((19,65,47,85), "/home/user/Alexander-Romero/cad/planta-alta.svg")
    export_svg((48,53,81,86), "/home/user/Alexander-Romero/cad/planta-baja.svg")
