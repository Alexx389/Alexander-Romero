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


def nuevo_doc():
    """DXF R2018 en metros con las capas, estilos y bloques de FUGA."""
    doc = ezdxf.new('R2018', setup=True)
    doc.units = ezdxf.units.M
    doc.header['$MEASUREMENT'] = 1
    doc.header['$LWDISPLAY'] = 1
    for nombre_capa, (color, lw) in CAPAS.items():
        doc.layers.add(nombre_capa, color=color, lineweight=lw)
    doc.layers.get('FACH-FOTO').off()
    _estilos(doc)
    _bloques(doc)
    return doc


def dibujar_fachada(msp, geo, dx=0.0, cotas=True):
    """Dibuja una fachada con su esquina abajo-izquierda en (dx, 0). Devuelve las aberturas."""
    ancho, alto = geo['ancho'], geo['alto']
    msp.add_lwpolyline([(dx, 0), (dx + ancho, 0), (dx + ancho, alto), (dx, alto)], close=True,
                       dxfattribs={'layer': 'FACH-CONTORNO'})
    aberturas = []
    for tipo, a, b, c, d, _ in geo['elementos']:
        a, c = a + dx, c + dx
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
    if cotas:
        cota = {'dimstyle': 'FUGA', 'dxfattribs': {'layer': 'FACH-COTAS'}}
        msp.add_linear_dim(base=(dx, -SEP_COTA), p1=(dx, 0), p2=(dx + ancho, 0), **cota).render()
        msp.add_linear_dim(base=(dx - SEP_COTA, 0), p1=(dx, 0), p2=(dx, alto), angle=90, **cota).render()
        for a, b, c, d in aberturas:
            msp.add_linear_dim(base=(c + 0.15, b), p1=(c, b), p2=(c, d), angle=90, **cota).render()
    return aberturas


def rotulo(msp, titulo, detalle, y):
    t = {'layer': 'FACH-TEXTO', 'style': 'FUGA'}
    msp.add_text(titulo, height=H_TEXTO, dxfattribs=t).set_placement((0, y), align=TextEntityAlignment.LEFT)
    msp.add_text(detalle, height=H_TEXTO * 0.6, dxfattribs=t).set_placement(
        (0, y - 0.27), align=TextEntityAlignment.LEFT)


def foto_de_fondo(doc, msp, geo, dx=0.0):
    """La rectificada en FACH-FOTO (apagada), calzada sobre el dibujo, para calcar."""
    est = geo['estado']
    W, H = est['ancho_px'], est['alto_px']
    rect = os.path.join(comun.RAIZ, est['rectificada'])
    idef = doc.add_image_def(filename=os.path.relpath(rect, comun.DXF).replace(os.sep, '/'), size_in_pixel=(W, H))
    ox, oy = geo['px_a_m'](0, H)
    msp.add_image(idef, insert=(ox + dx, oy), size_in_units=(W / est['px_por_m_x'], H / est['px_por_m_y']),
                  dxfattribs={'layer': 'FACH-FOTO'})


def dibujar(foto, rot=None):
    nom = comun.nombre(foto)
    geo = comun.geometria(nom)
    doc = nuevo_doc()
    msp = doc.modelspace()
    msp.add_line((-0.5, 0), (geo['ancho'] + 0.5, 0), dxfattribs={'layer': 'FACH-CONTORNO'})  # vereda
    aberturas = dibujar_fachada(msp, geo)
    rotulo(msp, '%s · ELEVACIÓN · RELEVAMIENTO FOTOGRÁFICO · FUGA TECH 001' % (rot or _rotulo_defecto(nom)).upper(),
           'Medidas en metros · precisión esperada ±5-10 cm · escala desde %s'
           % ', '.join(geo['estado'].get('escala_origen', [])), -SEP_COTA - 0.45)
    foto_de_fondo(doc, msp, geo)

    salida = os.path.join(comun.DXF, nom + '.dxf')
    os.makedirs(comun.DXF, exist_ok=True)
    doc.saveas(salida)
    aviso = '  (%d elemento(s) fuera del contorno, no dibujados)' % geo['fuera'] if geo['fuera'] else ''
    print('%s: DXF %.2f x %.2f m, %d elementos, %d aberturas acotadas -> %s%s'
          % (nom, geo['ancho'], geo['alto'], len(geo['elementos']), len(aberturas),
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
