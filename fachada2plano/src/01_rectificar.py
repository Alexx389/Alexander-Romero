# -*- coding: utf-8 -*-
"""01 Rectificar: deja la fachada frontal con una homografía.

Modo A (manual): 4 esquinas de la fachada en la foto original, en orden
arriba-izq, arriba-der, abajo-der, abajo-izq. Se pasan por --esquinas o con
--clic en una ventana. Quedan guardadas en el json de estado, así la próxima
corrida no pide nada.

El rectángulo de salida toma el promedio de los lados opuestos en píxeles:
la proporción ancho/alto sale aproximada, y 02_escalar la corrige si la foto
tiene una referencia horizontal y otra vertical.

Uso:
  python src/01_rectificar.py input/01_casa.jpg --esquinas "412,210;1630,260;1610,1180;430,1215"
  python src/01_rectificar.py input/01_casa.jpg --clic
"""
import argparse
import math
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import comun  # noqa: E402

LADO_MAX = 2400  # px del lado mayor de la rectificada: detalle de sobra sin archivos enormes


def _dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def rectificar(foto, esquinas=None, usar_clic=False):
    nom = comun.nombre(foto)
    img = cv2.imread(foto)
    if img is None:
        raise SystemExit('no se pudo leer %s' % foto)

    est = comun.estado(nom)
    if esquinas is None:
        esquinas = est.get('esquinas')
    if esquinas is None and usar_clic:
        esquinas = comun.clic(img, 4, 'Esquinas: arriba-izq, arriba-der, abajo-der, abajo-izq (Enter)')
    if esquinas is None:
        raise SystemExit('%s: faltan las esquinas. Usá --esquinas "x,y;x,y;x,y;x,y" o --clic' % nom)

    tl, tr, br, bl = esquinas
    ancho = (_dist(tl, tr) + _dist(bl, br)) / 2.0
    alto = (_dist(tl, bl) + _dist(tr, br)) / 2.0
    k = min(1.0, LADO_MAX / max(ancho, alto))
    w, h = int(round(ancho * k)), int(round(alto * k))

    src = np.float32(esquinas)
    dst = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
    H = cv2.getPerspectiveTransform(src, dst)
    rect = cv2.warpPerspective(img, H, (w, h), flags=cv2.INTER_CUBIC)

    os.makedirs(comun.RECT, exist_ok=True)
    salida = os.path.join(comun.RECT, nom + '.jpg')
    cv2.imwrite(salida, rect, [cv2.IMWRITE_JPEG_QUALITY, 92])
    comun.guardar_estado(nom, foto=os.path.relpath(foto, comun.RAIZ), esquinas=esquinas,
                         rectificada=os.path.relpath(salida, comun.RAIZ),
                         ancho_px=w, alto_px=h, homografia=H.tolist())
    print('%s: rectificada %dx%d px -> %s' % (nom, w, h, os.path.relpath(salida, comun.RAIZ)))
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('foto')
    ap.add_argument('--esquinas', help='"x,y;x,y;x,y;x,y" en la foto original')
    ap.add_argument('--clic', action='store_true', help='marcar las esquinas con el mouse')
    a = ap.parse_args()
    rectificar(a.foto, comun.puntos(a.esquinas, 4) if a.esquinas else None, a.clic)


if __name__ == '__main__':
    main()
