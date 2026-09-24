# -*- coding: utf-8 -*-
"""04 Dibujar DXF: elevación en línea de una fachada, en metros, para AutoCAD.

Lee la escala del json de estado y los elementos de <nombre>_elementos.json
(bbox en píxeles de la rectificada). El origen es la esquina abajo-izquierda
del contorno, con Y hacia arriba. DXF R2018 en metros.

Capas: FACH-CONTORNO, FACH-PUERTA, FACH-VENTANA, FACH-BARANDA, FACH-CORNISA,
FACH-ZOCALO, FACH-DETALLE, FACH-COTAS, FACH-TEXTO y FACH-FOTO (apagada, con
la rectificada para calcar a mano).

Uso:
  python src/04_dibujar_dxf.py input/01_casa.jpg
"""
import argparse
import os
import re
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment

sys.path.insert(0, os.path.dirname(__file__))
import comun  # noqa: E402

# capa: (color ACI, grosor en centésimas de mm)
CAPAS = {
    'FACH-CONTORNO': (7, 50),
    'FACH-PUERTA': (1, 35),
    'FACH-VENTANA': (5, 35),
    'FACH-BARANDA': (3, 25),
    'FACH-CORNISA': (2, 35),
    'FACH-ZOCALO': (8, 25),
    'FACH-DETALLE': (6, 18),
    'FACH-COTAS': (4, 13),
    'FACH-TEXTO': (7, 18),
    'FACH-FOTO': (9, 13),
}
CAPA_DE = {'puerta': 'FACH-PUERTA', 'porton': 'FACH-PUERTA', 'ventana': 'FACH-VENTANA',
           'baranda': 'FACH-BARANDA', 'cornisa': 'FACH-CORNISA', 'zocalo': 'FACH-ZOCALO'}
ABERTURAS = ('puerta', 'porton', 'ventana')

H_TEXTO = 0.15      # texto del rótulo, en metros de dibujo
H_COTA = 0.10
SEP_COTA = 0.50     # distancia de las cotas generales a la fachada
PASO_BARROTE = 0.12 # barandas y rejas: un barrote cada 12 cm


def _bloques(doc):
    """PUERTA y VENTANA de 1 x 1 m; se insertan escalados al tamaño del hueco."""
    p = doc.blocks.new('FUGA_PUERTA')
    p.add_lwpolyline([(0, 0), (1, 0), (1, 1), (0, 1)], close=True)
    p.add_lwpolyline([(0.07, 0), (0.07, 0.95), (0.93, 0.95), (0.93, 0)])  # marco, abierto al piso
    v = doc.blocks.new('FUGA_VENTANA')
    v.add_lwpolyline([(0, 0), (1, 0), (1, 1), (0, 1)], close=True)
    v.add_lwpolyline([(0.07, 0.07), (0.93, 0.07), (0.93, 0.93), (0.07, 0.93)], close=True)
    v.add_line((0, 0.07), (1, 0.07))  # alféizar


def _estilos(doc):
    doc.styles.add('FUGA', font='arial.ttf')
    ds = doc.dimstyles.new('FUGA')
    ds.dxf.dimtxsty = 'FUGA'
    ds.dxf.dimtxt = H_COTA
    ds.dxf.dimasz = 0.06
    ds.dxf.dimblk = 'ARCHTICK'
    ds.dxf.dimexe = 0.05
    ds.dxf.dimexo = 0.04
    ds.dxf.dimgap = 0.03
    ds.dxf.dimdec = 2
    ds.dxf.dimdsep = ord(',')
    ds.dxf.dimzin = 0   # 5,60 y no 5,6
    ds.dxf.dimtad = 1   # texto arriba de la línea
    ds.dxf.dimclrd = ds.dxf.dimclre = ds.dxf.dimclrt = 256  # por capa


def _rotulo_defecto(nom):
    """Solo el número de orden: el nombre del archivo puede traer la dirección."""
    m = re.match(r'^(\d+)', nom)
    return 'FACHADA %s' % (m.group(1) if m else '')


def dibujar(foto, rotulo=None):
    nom = comun.nombre(foto)
    est = comun.estado(nom)
    if 'px_por_m_x' not in est:
        raise SystemExit('%s: primero correr 01_rectificar y 02_escalar' % nom)
    ej = comun.leer_json(comun.ruta_elementos(nom))
    if not ej:
        raise SystemExit('%s: falta %s' % (nom, os.path.relpath(comun.ruta_elementos(nom), comun.RAIZ)))

    W, H = est['ancho_px'], est['alto_px']
    sx, sy = est['px_por_m_x'], est['px_por_m_y']
    cx0, cy0, cx1, cy1 = ej.get('contorno') or [0, 0, W, H]

    def m(x, y):  # píxel de la rectificada -> metros, origen abajo-izquierda del contorno
        return ((x - cx0) / sx, (cy1 - y) / sy)

    doc = ezdxf.new('R2018', setup=True)
    doc.units = ezdxf.units.M
    doc.header['$MEASUREMENT'] = 1
    doc.header['$LWDISPLAY'] = 1
    for nombre_capa, (color, lw) in CAPAS.items():
        doc.layers.add(nombre_capa, color=color, lineweight=lw)
    doc.layers.get('FACH-FOTO').off()
    _estilos(doc)
    _bloques(doc)
    msp = doc.modelspace()

    ancho_m, alto_m = m(cx1, cy0)
    msp.add_lwpolyline([(0, 0), (ancho_m, 0), (ancho_m, alto_m), (0, alto_m)], close=True,
                       dxfattribs={'layer': 'FACH-CONTORNO'})
    msp.add_line((-0.5, 0), (ancho_m + 0.5, 0), dxfattribs={'layer': 'FACH-CONTORNO'})  # vereda

    fuera, aberturas = 0, []
    for e in ej.get('elementos', []):
        tipo = e.get('tipo', 'otro')
        x0, y0, x1, y1 = e['bbox']
        if x1 < cx0 or x0 > cx1 or y1 < cy0 or y0 > cy1:
            fuera += 1
            continue
        (a, b), (c, d) = m(min(x0, x1), max(y0, y1)), m(max(x0, x1), min(y0, y1))
        capa = CAPA_DE.get(tipo, 'FACH-DETALLE')
        w, h = c - a, d - b
        if tipo in ('puerta', 'porton'):
            msp.add_blockref('FUGA_PUERTA', (a, b), dxfattribs={'layer': capa, 'xscale': w, 'yscale': h})
        elif tipo == 'ventana':
            msp.add_blockref('FUGA_VENTANA', (a, b), dxfattribs={'layer': capa, 'xscale': w, 'yscale': h})
        else:
            msp.add_lwpolyline([(a, b), (c, b), (c, d), (a, d)], close=True, dxfattribs={'layer': capa})
            if tipo in ('baranda', 'reja'):
                n = max(1, int(w / PASO_BARROTE))
                for i in range(1, n):
                    x = a + w * i / n
                    msp.add_line((x, b), (x, d), dxfattribs={'layer': capa})
        if tipo in ABERTURAS:
            aberturas.append((a, b, c, d))

    cota = {'dimstyle': 'FUGA', 'dxfattribs': {'layer': 'FACH-COTAS'}}
    msp.add_linear_dim(base=(0, -SEP_COTA), p1=(0, 0), p2=(ancho_m, 0), **cota).render()
    msp.add_linear_dim(base=(-SEP_COTA, 0), p1=(0, 0), p2=(0, alto_m), angle=90, **cota).render()
    for a, b, c, d in aberturas:
        msp.add_linear_dim(base=(c + 0.15, b), p1=(c, b), p2=(c, d), angle=90, **cota).render()

    rot = rotulo or _rotulo_defecto(nom)
    t = {'layer': 'FACH-TEXTO', 'style': 'FUGA'}
    msp.add_text('%s · ELEVACIÓN · RELEVAMIENTO FOTOGRÁFICO · FUGA TECH 001' % rot.upper(),
                 height=H_TEXTO, dxfattribs=t).set_placement((0, -SEP_COTA - 0.45), align=TextEntityAlignment.LEFT)
    msp.add_text('Medidas en metros · precisión esperada ±5-10 cm · escala desde %s'
                 % ', '.join(est.get('escala_origen', [])),
                 height=H_TEXTO * 0.6, dxfattribs=t).set_placement((0, -SEP_COTA - 0.72), align=TextEntityAlignment.LEFT)

    salida = os.path.join(comun.DXF, nom + '.dxf')
    os.makedirs(comun.DXF, exist_ok=True)
    rect = os.path.join(comun.RAIZ, est['rectificada'])
    idef = doc.add_image_def(filename=os.path.relpath(rect, comun.DXF).replace(os.sep, '/'), size_in_pixel=(W, H))
    ox, oy = m(0, H)
    msp.add_image(idef, insert=(ox, oy), size_in_units=(W / sx, H / sy), dxfattribs={'layer': 'FACH-FOTO'})

    doc.saveas(salida)
    aviso = '  (%d elemento(s) fuera del contorno, no dibujados)' % fuera if fuera else ''
    print('%s: DXF %.2f x %.2f m, %d elementos, %d aberturas acotadas -> %s%s'
          % (nom, ancho_m, alto_m, len(ej.get('elementos', [])) - fuera, len(aberturas),
             os.path.relpath(salida, comun.RAIZ), aviso))
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('foto')
    ap.add_argument('--rotulo', help='texto del rótulo (sin números de casa ni propietarios)')
    a = ap.parse_args()
    dibujar(a.foto, a.rotulo)


if __name__ == '__main__':
    main()
