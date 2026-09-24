# -*- coding: utf-8 -*-
"""02 Escalar: calcula cuántos píxeles de la rectificada son un metro.

La medida sale de refs.csv (foto, medida_ref_m, tipo_ref). Los 2 puntos de la
medida se marcan sobre la foto RECTIFICADA, con --puntos o --clic. Si el tipo
es de puerta y no se marcan puntos, se usa el bbox de la primera puerta
cargada en <nombre>_elementos.json.

  ancho_puerta, ancho_lote -> escala horizontal (distancia en x)
  alto_puerta              -> escala vertical   (distancia en y)

Con una sola referencia se usa la misma escala en los dos ejes. Con una
horizontal y una vertical cada eje tiene la suya, y eso corrige la proporción
aproximada que dejó 01_rectificar.

Sin referencia: se asume que la primera puerta mide 2,10 m de alto.

Uso:
  python src/02_escalar.py input/01_casa.jpg --puntos "880,1020;1180,1020"
  python src/02_escalar.py input/01_casa.jpg --clic
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import comun  # noqa: E402

HORIZ = ('ancho_puerta', 'ancho_lote')
VERT = ('alto_puerta',)


def _puerta(nom):
    """La puerta peatonal que sirve de referencia. Un portón no: no mide 2,10.

    Si hay más de una, se toma la de la izquierda y se avisa: conviene marcar
    los puntos de la puerta que realmente se midió.
    """
    els = comun.leer_json(comun.ruta_elementos(nom)).get('elementos', [])
    puertas = sorted((e['bbox'] for e in els if e.get('tipo') == 'puerta'), key=lambda b: b[0])
    if len(puertas) > 1:
        print('%s: OJO, hay %d puertas; la escala sale de la de la izquierda. '
              'Si mediste otra, marcá sus puntos con --puntos o --clic.' % (nom, len(puertas)))
    return puertas[0] if puertas else None


def escalar(foto, puntos_cli=None, usar_clic=False):
    nom = comun.nombre(foto)
    est = comun.estado(nom)
    if 'rectificada' not in est:
        raise SystemExit('%s: primero correr 01_rectificar' % nom)

    filas = comun.refs(nom)
    guardados = est.get('ref_puntos', {})
    origenes = est.get('ref_origen', {})
    medidas = {}  # 'x' / 'y' -> (px, m, origen)

    for i, r in enumerate(filas):
        tipo = (r.get('tipo_ref') or '').strip()
        m = float(r['medida_ref_m'])
        if tipo not in HORIZ + VERT:
            raise SystemExit('%s: tipo_ref desconocido %r' % (nom, tipo))
        eje = 'x' if tipo in HORIZ else 'y'
        pts = (puntos_cli[i] if puntos_cli and i < len(puntos_cli) else None) or guardados.get(tipo)
        origen = origenes.get(tipo, 'puntos') if pts is not None and not (puntos_cli and i < len(puntos_cli)) else 'puntos'
        if pts is None and usar_clic:
            import cv2
            img = cv2.imread(os.path.join(comun.RAIZ, est['rectificada']))
            pts = comun.clic(img, 2, '%s = %.2f m: marcá los 2 extremos (Enter)' % (tipo, m))
        if pts is None and tipo in ('ancho_puerta', 'alto_puerta'):
            b = _puerta(nom)
            if b:
                pts = [[b[0], b[3]], [b[2], b[3]]] if eje == 'x' else [[b[0], b[1]], [b[0], b[3]]]
                origen = 'bbox de la puerta'
        if pts is None:
            raise SystemExit('%s: la referencia %s no tiene puntos. Usá --puntos o --clic' % (nom, tipo))
        guardados[tipo], origenes[tipo] = pts, origen
        px = abs(pts[1][0] - pts[0][0]) if eje == 'x' else abs(pts[1][1] - pts[0][1])
        if px < 5:
            raise SystemExit('%s: los puntos de %s están casi encima uno del otro' % (nom, tipo))
        medidas[eje] = (px, m, '%s (%s)' % (tipo, origen))

    if not medidas:
        b = _puerta(nom)
        if not b:
            raise SystemExit('%s: sin refs.csv ni puerta cargada, no hay de dónde sacar la escala' % nom)
        medidas['y'] = (abs(b[3] - b[1]), comun.ALTO_PUERTA_STD, 'puerta estándar %.2f m' % comun.ALTO_PUERTA_STD)

    ppm = {e: px / m for e, (px, m, _) in medidas.items()}
    ppm_x = ppm.get('x', ppm.get('y'))
    ppm_y = ppm.get('y', ppm.get('x'))
    comun.guardar_estado(nom, ref_puntos=guardados, ref_origen=origenes, px_por_m_x=ppm_x, px_por_m_y=ppm_y,
                         escala_origen=[o for _, _, o in medidas.values()])
    print('%s: %.1f px/m horizontal, %.1f px/m vertical -> fachada de %.2f x %.2f m  [%s]'
          % (nom, ppm_x, ppm_y, est['ancho_px'] / ppm_x, est['alto_px'] / ppm_y,
             '; '.join(o for _, _, o in medidas.values())))
    return ppm_x, ppm_y


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('foto')
    ap.add_argument('--puntos', action='append',
                    help='"x,y;x,y" sobre la rectificada, uno por fila de refs.csv (en orden)')
    ap.add_argument('--clic', action='store_true')
    a = ap.parse_args()
    escalar(a.foto, [comun.puntos(p, 2) for p in a.puntos] if a.puntos else None, a.clic)


if __name__ == '__main__':
    main()
