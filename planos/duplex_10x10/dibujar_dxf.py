"""
Genera el plano en DXF (AutoCAD, unidades en METROS, escala 1:1 en modelo).

    python3 dibujar_dxf.py

Notas de implementacion:
  - No se usan BLOCKs ni entidades DIMENSION: las cotas se dibujan explotadas
    (lineas + marcas + TEXT) para que el archivo abra sin sorpresas en
    AutoCAD 2026 en espanol.
  - Los huecos de puertas y ventanas se restan de los muros, en lugar de
    taparse con relleno, para que el DXF quede limpio al editar.
"""
import math
import os

import ezdxf

import geometria as G

AQUI = os.path.dirname(os.path.abspath(__file__))

# altura de texto en metros -> milimetros de papel a escala 1:50
H_AMBIENTE = 0.16
H_MEDIDA = 0.115
H_COTA = 0.125
H_TITULO = 0.30

CAPAS = [
    ("MUROS", 7),
    ("MUROS-RELLENO", 8),
    ("ABERTURAS", 4),
    ("ESCALERA", 3),
    ("COTAS", 5),
    ("TEXTOS", 2),
    ("TERRENO", 1),
    ("ROTULO", 7),
]


# ------------------------------------------------------- resta de huecos ---
def _huecos_todos():
    h = []
    for p in G.PUERTAS:
        h.append(p["hueco"])
    h.extend(G.VANOS)
    h.extend(v[:4] for v in G.VENTANAS)
    return h


def restar_huecos(muro, huecos):
    """Parte un muro rectangular en tramos, quitando los huecos que lo cruzan.

    Devuelve la lista de rectangulos macizos resultantes.
    """
    x0, y0, x1, y1 = muro
    horizontal = (x1 - x0) >= (y1 - y0)
    a0, a1 = (x0, x1) if horizontal else (y0, y1)

    cortes = []
    for (hx0, hy0, hx1, hy1) in huecos:
        # el hueco debe solaparse con el muro en los dos ejes
        if hx1 <= x0 + 1e-9 or hx0 >= x1 - 1e-9:
            continue
        if hy1 <= y0 + 1e-9 or hy0 >= y1 - 1e-9:
            continue
        c0, c1 = (hx0, hx1) if horizontal else (hy0, hy1)
        cortes.append((max(c0, a0), min(c1, a1)))

    tramos = []
    cursor = a0
    for c0, c1 in sorted(cortes):
        if c0 > cursor + 1e-9:
            tramos.append((cursor, c0))
        cursor = max(cursor, c1)
    if cursor < a1 - 1e-9:
        tramos.append((cursor, a1))

    if horizontal:
        return [(t0, y0, t1, y1) for t0, t1 in tramos]
    return [(x0, t0, x1, t1) for t0, t1 in tramos]


# ------------------------------------------------------------- dibujo ------
def rect(msp, r, capa, cerrado=True):
    x0, y0, x1, y1 = r
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return msp.add_lwpolyline(pts, close=cerrado,
                              dxfattribs={"layer": capa})


def rellenar(msp, r, capa="MUROS-RELLENO"):
    x0, y0, x1, y1 = r
    h = msp.add_hatch(color=8, dxfattribs={"layer": capa})
    h.paths.add_polyline_path(
        [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], is_closed=True)


def texto(msp, s, pos, altura, capa="TEXTOS", rot=0.0, alineado="centro"):
    t = msp.add_text(s, height=altura,
                     rotation=rot,
                     dxfattribs={"layer": capa})
    anclas = {"centro": ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER,
              "izq": ezdxf.enums.TextEntityAlignment.MIDDLE_LEFT,
              "der": ezdxf.enums.TextEntityAlignment.MIDDLE_RIGHT}
    t.set_placement(pos, align=anclas[alineado])
    return t


def fmt(v):
    return f"{round(v, 4):.2f}".replace(".", ",")


def dibujar_muros(msp):
    huecos = _huecos_todos()
    for muro in G.MUROS:
        for tramo in restar_huecos(muro, huecos):
            rect(msp, tramo, "MUROS")
            rellenar(msp, tramo)


def dibujar_ambientes(msp):
    for ambientes in (G.AMBIENTES_1, G.AMBIENTES_2):
        for nombre, medida, area, poly, (tx, ty), compacto in ambientes:
            msp.add_lwpolyline(poly, close=True,
                               dxfattribs={"layer": "TEXTOS"})
            if compacto:
                texto(msp, nombre, (tx, ty + 0.13), H_AMBIENTE)
                texto(msp, f"{medida}  -  {fmt(area)} m2",
                      (tx, ty - 0.15), H_MEDIDA)
            else:
                texto(msp, nombre, (tx, ty + 0.26), H_AMBIENTE)
                texto(msp, medida, (tx, ty), H_MEDIDA)
                texto(msp, f"{fmt(area)} m2", (tx, ty - 0.26), H_MEDIDA)


def dibujar_ventanas(msp):
    for (x0, y0, x1, y1, eje) in G.VENTANAS:
        rect(msp, (x0, y0, x1, y1), "ABERTURAS")
        if eje == "h":
            ym = (y0 + y1) / 2
            msp.add_line((x0, ym), (x1, ym), dxfattribs={"layer": "ABERTURAS"})
        else:
            xm = (x0 + x1) / 2
            msp.add_line((xm, y0), (xm, y1), dxfattribs={"layer": "ABERTURAS"})


def dibujar_puertas(msp):
    for p in G.PUERTAS:
        x0, y0, x1, y1 = p["hueco"]
        ancho = (x1 - x0) if p["eje"] == "h" else (y1 - y0)
        bx, by = p["bisagra"]
        a1 = math.radians(p["ang0"] + p["barrido"])
        msp.add_line((bx, by),
                     (bx + ancho * math.cos(a1), by + ancho * math.sin(a1)),
                     dxfattribs={"layer": "ABERTURAS"})
        th0, th1 = sorted([p["ang0"], p["ang0"] + p["barrido"]])
        msp.add_arc(center=(bx, by), radius=ancho,
                    start_angle=th0, end_angle=th1,
                    dxfattribs={"layer": "ABERTURAS"})


def dibujar_escalera(msp):
    e = G.ESC
    rect(msp, (e["x0"], e["y0"], e["x1"], e["y1"]), "ESCALERA")
    for (x0, y, x1, _) in G.escalones():
        msp.add_line((x0, y), (x1, y), dxfattribs={"layer": "ESCALERA"})
    rect(msp, (e["x0"] + e["ancho_tramo"], e["y_descanso_int"],
               e["x0"] + e["ancho_tramo"] + e["ojo"], e["y_descanso_sup"]),
         "ESCALERA")
    # flecha de subida
    xc = e["x0"] + e["ancho_tramo"] / 2
    msp.add_line((xc, 8.60), (xc, 7.00), dxfattribs={"layer": "ESCALERA"})
    for dx in (-0.09, 0.09):
        msp.add_line((xc, 7.00), (xc + dx, 7.18),
                     dxfattribs={"layer": "ESCALERA"})
    texto(msp, "SUBE", (xc, 8.75), H_MEDIDA, "ESCALERA")
    texto(msp, "ESCALERA COMUN", (5.00, 9.55), H_AMBIENTE, "ESCALERA")
    texto(msp, "2,60 x 4,25  -  tramos de 1,20", (5.00, 9.30),
          H_MEDIDA, "ESCALERA")
    texto(msp, "16 alzadas de 0,175  -  pedada 0,275", (5.00, 6.20),
          H_MEDIDA, "ESCALERA")


# ------------------------------------------------------------- cotas -------
def marca(msp, x, y, largo=0.12):
    d = largo / math.sqrt(2)
    msp.add_line((x - d, y - d), (x + d, y + d),
                 dxfattribs={"layer": "COTAS"})


def cadena(msp, pos, fijo, eje, texto_lado):
    """Dibuja una cadena de cotas explotada.

    eje = 'h' -> cadena horizontal a la altura y = fijo
    eje = 'v' -> cadena vertical en x = fijo
    """
    if eje == "h":
        msp.add_line((pos[0], fijo), (pos[-1], fijo),
                     dxfattribs={"layer": "COTAS"})
    else:
        msp.add_line((fijo, pos[0]), (fijo, pos[-1]),
                     dxfattribs={"layer": "COTAS"})

    for p in pos:
        marca(msp, p if eje == "h" else fijo, fijo if eje == "h" else p)

    for a, b in zip(pos, pos[1:]):
        d = b - a
        if d <= 0.001:
            continue
        m = (a + b) / 2
        chico = d < 0.45
        off = 0.12 * (1 if texto_lado > 0 else -1)
        if eje == "h":
            if chico:
                texto(msp, fmt(d), (m, fijo + off * 2.2), H_COTA * 0.85,
                      "COTAS", rot=90)
            else:
                texto(msp, fmt(d), (m, fijo + off), H_COTA, "COTAS")
        else:
            if chico:
                texto(msp, fmt(d), (fijo + off * 2.2, m), H_COTA * 0.85,
                      "COTAS")
            else:
                texto(msp, fmt(d), (fijo + off, m), H_COTA, "COTAS", rot=90)


def auxiliares(msp, pos, desde, hasta, eje):
    for p in pos:
        if eje == "h":
            msp.add_line((p, desde), (p, hasta), dxfattribs={"layer": "COTAS"})
        else:
            msp.add_line((desde, p), (hasta, p), dxfattribs={"layer": "COTAS"})


def dibujar_cotas(msp):
    for c in G.COTAS_H:
        y = c.get("base", 0.00) + c["off"]
        arriba = c["lado"] == "arriba"
        cadena(msp, c["pos"], y, "h", 1 if arriba else -1)
        auxiliares(msp, c["pos"], 0.00 if not arriba else 10.00, y, "h")
    for c in G.COTAS_V:
        x = c.get("base", 0.00) + c["off"]
        der = c["lado"] == "der"
        cadena(msp, c["pos"], x, "v", 1 if der else -1)
        auxiliares(msp, c["pos"], 0.00 if not der else 10.00, x, "v")


# ------------------------------------------------------------- rotulo ------
def dibujar_rotulo(msp):
    texto(msp, "EDIFICIO DE DOS DEPARTAMENTOS", (5.00, 12.60), H_TITULO)
    texto(msp, "Terreno de 10,00 x 10,00 m  -  Planta acotada  -  Esc. 1:50",
          (5.00, 12.20), H_AMBIENTE)
    texto(msp, "DEPARTAMENTO 1", (2.50, 11.60), H_AMBIENTE * 1.2)
    texto(msp, "5,00 x 10,00 m", (2.50, 11.32), H_MEDIDA)
    texto(msp, "DEPARTAMENTO 2", (7.50, 11.60), H_AMBIENTE * 1.2)
    texto(msp, "5,00 x 10,00 m", (7.50, 11.32), H_MEDIDA)
    texto(msp, "CALLE  -  LINEA MUNICIPAL", (5.00, -3.20), H_AMBIENTE)

    x = 13.00
    y = 10.00
    texto(msp, "PLANILLA DE SUPERFICIES (por departamento)", (x, y),
          H_AMBIENTE, "ROTULO", alineado="izq")
    y -= 0.45
    for nombre, medida, area, _, _, _ in G.AMBIENTES_UNIDAD:
        texto(msp, nombre, (x, y), H_MEDIDA, "ROTULO", alineado="izq")
        texto(msp, medida, (x + 3.00, y), H_MEDIDA, "ROTULO", alineado="izq")
        texto(msp, f"{fmt(area)} m2", (x + 5.20, y), H_MEDIDA, "ROTULO",
              alineado="izq")
        y -= 0.32
    y -= 0.15
    texto(msp, f"SUPERFICIE CUBIERTA           {fmt(G.SUP_INTERIOR)} m2",
          (x, y), H_MEDIDA, "ROTULO", alineado="izq")
    y -= 0.32
    texto(msp, "TOTAL CON BALCON              "
               f"{fmt(G.SUP_INTERIOR + G.SUP_BALCON)} m2",
          (x, y), H_MEDIDA, "ROTULO", alineado="izq")

    y -= 0.70
    texto(msp, "NOTAS", (x, y), H_AMBIENTE, "ROTULO", alineado="izq")
    y -= 0.40
    notas = [
        "1. Medidas en metros, a cara de muro terminado.",
        "2. Muros exteriores y medianeras 0,15 - divisorio 0,20 - tabiques 0,10.",
        "3. Altura piso a piso 2,80 m.",
        "4. Los dos departamentos son espejo respecto del muro divisorio.",
        "5. Acceso a planta alta por escalera comun al fondo, de dos tramos",
        "   con descanso, y balcon corredor de 1,20 m.",
        "6. Muros sobre medianera sin aberturas: iluminacion y ventilacion",
        "   por frente y por fondo.",
        "7. El bano ventila a la caja de escalera (patio de aire y luz).",
        "8. Verificar retiros y factor de ocupacion con la ordenanza municipal.",
        "9. Cotas a confirmar con relevamiento en obra.",
    ]
    for n in notas:
        texto(msp, n, (x, y), H_MEDIDA, "ROTULO", alineado="izq")
        y -= 0.30


def construir():
    doc = ezdxf.new("R2010", setup=True)
    doc.units = 6  # metros
    for nombre, color in CAPAS:
        doc.layers.add(name=nombre, color=color)
    msp = doc.modelspace()

    # limite del terreno
    p = rect(msp, (0, 0, 10, 10), "TERRENO")
    p.dxf.linetype = "DASHDOT" if "DASHDOT" in doc.linetypes else "CONTINUOUS"

    dibujar_ambientes(msp)
    dibujar_escalera(msp)
    dibujar_muros(msp)
    dibujar_ventanas(msp)
    dibujar_puertas(msp)
    dibujar_cotas(msp)
    dibujar_rotulo(msp)
    return doc


if __name__ == "__main__":
    doc = construir()
    salida = os.path.join(AQUI, "plano_duplex_10x10.dxf")
    doc.saveas(salida)
    print("OK ->", salida)
