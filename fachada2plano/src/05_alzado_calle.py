# -*- coding: utf-8 -*-
"""05 Alzado de calle: todas las fachadas en fila, en un solo DXF.

Toma las fotos de input/ que ya tienen escala y elementos, en el orden del
nombre de archivo (01_, 02_...), una pegada a la otra y apoyadas en la línea
de vereda. Cota por fachada, cota total y el rótulo con el nombre de la calle
o del barrio (sin números de casa).

Uso:
  python src/05_alzado_calle.py --calle "SAJONIA"
"""
import argparse
import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import comun  # noqa: E402

_spec = importlib.util.spec_from_file_location('dxf04', os.path.join(os.path.dirname(__file__), '04_dibujar_dxf.py'))
dxf04 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dxf04)


def listas():
    """Fachadas con escala y elementos, en orden."""
    out = []
    for foto in comun.fotos():
        nom = comun.nombre(foto)
        if 'px_por_m_x' in comun.estado(nom) and os.path.exists(comun.ruta_elementos(nom)):
            out.append(nom)
    return out


def alzado(calle='CALLE'):
    noms = listas()
    if not noms:
        raise SystemExit('no hay fachadas con escala y elementos para armar el alzado')
    doc = dxf04.nuevo_doc()
    msp = doc.modelspace()
    cota = {'dimstyle': 'FUGA', 'dxfattribs': {'layer': 'FACH-COTAS'}}

    x, alto_max, geos = 0.0, 0.0, []
    for nom in noms:
        geo = comun.geometria(nom)
        dxf04.dibujar_fachada(msp, geo, dx=x, cotas=False)
        dxf04.foto_de_fondo(doc, msp, geo, dx=x)
        msp.add_linear_dim(base=(x, -dxf04.SEP_COTA), p1=(x, 0), p2=(x + geo['ancho'], 0), **cota).render()
        geos.append((nom, x, geo))
        x += geo['ancho']
        alto_max = max(alto_max, geo['alto'])

    msp.add_line((-1.0, 0), (x + 1.0, 0), dxfattribs={'layer': 'FACH-CONTORNO'})  # vereda
    msp.add_linear_dim(base=(0, -2 * dxf04.SEP_COTA), p1=(0, 0), p2=(x, 0), **cota).render()
    dxf04.rotulo(msp, '%s · RELEVAMIENTO FOTOGRÁFICO · FUGA TECH 001' % calle.upper(),
                 '%d fachadas · %.2f m de frente · medidas en metros · ±5-10 cm'
                 % (len(noms), x), -2 * dxf04.SEP_COTA - 0.5)

    os.makedirs(comun.DXF, exist_ok=True)
    salida = os.path.join(comun.DXF, 'alzado_calle.dxf')
    doc.saveas(salida)
    comun.escribir_json(os.path.join(comun.JSON, 'alzado_calle.json'),
                        {'calle': calle, 'frente_m': x, 'alto_max_m': alto_max,
                         'fachadas': [{'nombre': n, 'x_m': dx, 'ancho_m': g['ancho'], 'alto_m': g['alto']}
                                      for n, dx, g in geos]})
    print('alzado de calle: %d fachadas, %.2f m de frente -> %s'
          % (len(noms), x, os.path.relpath(salida, comun.RAIZ)))
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--calle', default='CALLE', help='nombre de la calle o barrio para el rótulo')
    alzado(ap.parse_args().calle)


if __name__ == '__main__':
    main()
