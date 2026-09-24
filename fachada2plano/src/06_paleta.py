# -*- coding: utf-8 -*-
"""06 Paleta: los 5 colores reales de la fachada (k-means).

Se toman los píxeles de adentro del contorno (sin cielo ni vereda) y se
agrupan en 5 colores, ordenados por cuánto ocupan. Se descartan los muy
oscuros (sombras, vidrio): no son el color de la casa. Sale un PNG con las
muestras y el hex, y un json.

Uso:
  python src/06_paleta.py input/01_casa.jpg
"""
import argparse
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw
from sklearn.cluster import KMeans

sys.path.insert(0, os.path.dirname(__file__))
import comun  # noqa: E402

N_COLORES = 5
MUESTRA = 40000       # píxeles que entran al k-means: de sobra para 5 colores
LUMA_MIN = 28         # más oscuro que esto es sombra o vidrio


def hexa(rgb):
    return '#%02X%02X%02X' % tuple(int(v) for v in rgb)


def paleta(foto):
    nom = comun.nombre(foto)
    est = comun.estado(nom)
    if 'rectificada' not in est:
        raise SystemExit('%s: primero correr 01_rectificar' % nom)
    img = cv2.cvtColor(cv2.imread(os.path.join(comun.RAIZ, est['rectificada'])), cv2.COLOR_BGR2RGB)
    ej = comun.leer_json(comun.ruta_elementos(nom))
    x0, y0, x1, y1 = ej.get('contorno') or [0, 0, img.shape[1], img.shape[0]]
    px = img[y0:y1, x0:x1].reshape(-1, 3).astype(np.float32)
    luma = px @ np.float32([0.299, 0.587, 0.114])
    px = px[luma >= LUMA_MIN]
    if len(px) < N_COLORES:
        raise SystemExit('%s: no hay píxeles suficientes para la paleta' % nom)
    rng = np.random.default_rng(0)
    if len(px) > MUESTRA:
        px = px[rng.choice(len(px), MUESTRA, replace=False)]

    km = KMeans(n_clusters=N_COLORES, n_init=4, random_state=0).fit(px)
    peso = np.bincount(km.labels_, minlength=N_COLORES) / float(len(px))
    orden = np.argsort(-peso)
    colores = [{'hex': hexa(km.cluster_centers_[i]), 'rgb': [int(v) for v in km.cluster_centers_[i]],
                'proporcion': round(float(peso[i]), 3)} for i in orden]

    os.makedirs(comun.PALETAS, exist_ok=True)
    comun.escribir_json(os.path.join(comun.PALETAS, nom + '.json'), {'fachada': nom, 'colores': colores})
    lienzo = Image.new('RGB', (1000, 260), '#F4F2ED')
    d = ImageDraw.Draw(lienzo)
    fuente = comun.fuente('cuerpo', 22)
    x = 20
    for c in colores:
        w = 180
        d.rectangle([x, 20, x + w, 180], fill=tuple(c['rgb']))
        d.text((x, 195), c['hex'], fill='#0A0A0A', font=fuente)
        d.text((x, 222), '%d %%' % round(c['proporcion'] * 100), fill='#0A0A0A', font=fuente)
        x += w + 12
    salida = os.path.join(comun.PALETAS, nom + '.png')
    lienzo.save(salida)
    print('%s: paleta %s -> %s' % (nom, ' '.join(c['hex'] for c in colores), os.path.relpath(salida, comun.RAIZ)))
    return colores


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('foto')
    paleta(ap.parse_args().foto)


if __name__ == '__main__':
    main()
