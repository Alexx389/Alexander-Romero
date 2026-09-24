# -*- coding: utf-8 -*-
"""Genera fachadas de prueba con medidas conocidas, para validar el pipeline.

Tres casas (8,40 x 5,60 / 6,00 x 4,20 / 10,00 x 6,50 m) dibujadas de frente
y deformadas con una perspectiva, como fotos sacadas de costado. Escribe
input/9N_prueba.jpg, sus filas en refs.csv, las esquinas en el estado y el
json de elementos (lo que se carga a mano o saca 03_detectar).

  python herramientas/fachada_prueba.py
  python run.py --calle "PRUEBA"

Cada DXF tiene que dar sus medidas reales (±10 %).
"""
import csv
import os
import sys

import cv2
import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'src'))
import comun  # noqa: E402

P = 100
# Tres casas distintas para probar también el alzado de calle.
# (nombre, ancho, alto, pared BGR, esquinas en la foto, elementos en metros)
CASAS = [
    ('91_prueba', 8.4, 5.6, (205, 225, 240), [[300, 180], [1650, 330], [1620, 1150], [330, 1280]],
     [('zocalo', 0, 0, 8.4, 0.5), ('cornisa', 0, 5.2, 8.4, 5.6), ('puerta', 3.7, 0, 4.7, 2.1),
      ('ventana', 1.0, 1.0, 2.2, 2.4), ('ventana', 6.2, 1.0, 7.4, 2.4), ('baranda', 2.9, 3.2, 5.5, 4.2)]),
    ('92_prueba', 6.0, 4.2, (150, 190, 120), [[250, 260], [1500, 200], [1540, 1180], [220, 1100]],
     [('zocalo', 0, 0, 6.0, 0.4), ('porton', 0.6, 0, 3.4, 2.4), ('puerta', 4.2, 0, 5.1, 2.1),
      ('cornisa', 0, 3.8, 6.0, 4.2), ('reja', 0.6, 2.7, 3.4, 3.4)]),
    ('93_prueba', 10.0, 6.5, (220, 220, 225), [[200, 120], [1720, 240], [1700, 1250], [230, 1320]],
     [('zocalo', 0, 0, 10.0, 0.6), ('pilar', 0, 0, 0.5, 6.5), ('pilar', 9.5, 0, 10.0, 6.5),
      ('puerta', 4.4, 0, 5.6, 2.4), ('ventana', 1.2, 1.0, 3.2, 2.6), ('ventana', 6.8, 1.0, 8.8, 2.6),
      ('ventana', 1.2, 3.8, 3.2, 5.4), ('ventana', 6.8, 3.8, 8.8, 5.4), ('alero', 0, 6.1, 10.0, 6.5)]),
]
COLOR = {'zocalo': (90, 100, 110), 'cornisa': (240, 245, 250), 'puerta': (160, 80, 20), 'porton': (60, 60, 60),
         'ventana': (70, 60, 50), 'pilar': (200, 200, 200), 'alero': (80, 90, 150)}


def casa(nombre, ancho, alto, pared, esquinas, elementos):
    W, H = int(ancho * P), int(alto * P)
    f = np.full((H, W, 3), pared, np.uint8)
    for tipo, x0, y0, x1, y1 in elementos:
        p0, p1 = (int(x0 * P), H - int(y1 * P)), (int(x1 * P), H - int(y0 * P))
        if tipo in COLOR:
            cv2.rectangle(f, p0, p1, COLOR[tipo], -1)
        cv2.rectangle(f, p0, p1, (40, 40, 40), 3)
    foto = np.full((1400, 1900, 3), (180, 200, 215), np.uint8)
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [W, 0], [W, H], [0, H]]), np.float32(esquinas))
    cv2.warpPerspective(f, M, (1900, 1400), foto, borderMode=cv2.BORDER_TRANSPARENT)
    cv2.imwrite(os.path.join(comun.INPUT, nombre + '.jpg'), foto)

    # Elementos en píxeles de la rectificada: se calcula el mismo tamaño que
    # va a sacar 01_rectificar (promedio de lados opuestos).
    d = lambda a, b: np.hypot(b[0] - a[0], b[1] - a[1])
    tl, tr, br, bl = esquinas
    rw, rh = round((d(tl, tr) + d(bl, br)) / 2), round((d(tl, bl) + d(tr, br)) / 2)
    kx, ky = rw / ancho, rh / alto
    els = [{'tipo': t, 'bbox': [round(x0 * kx), round((alto - y1) * ky), round(x1 * kx), round((alto - y0) * ky)],
            'nota': ''} for t, x0, y0, x1, y1 in elementos]
    comun.escribir_json(comun.ruta_elementos(nombre), {'contorno': [0, 0, rw, rh], 'elementos': els})
    comun.guardar_estado(nombre, esquinas=esquinas)
    puerta = next(e for e in elementos if e[0] == 'puerta')
    return [{'foto': nombre + '.jpg', 'medida_ref_m': '%.2f' % (puerta[3] - puerta[1]), 'tipo_ref': 'ancho_puerta'},
            {'foto': nombre + '.jpg', 'medida_ref_m': '%.2f' % (puerta[4] - puerta[2]), 'tipo_ref': 'alto_puerta'}]


def main():
    os.makedirs(comun.INPUT, exist_ok=True)
    nuevas = []
    for c in CASAS:
        nuevas += casa(*c)
    filas = []
    if os.path.exists(comun.REFS):
        with open(comun.REFS, encoding='utf-8-sig') as fh:
            filas = [r for r in csv.DictReader(fh) if not comun.nombre(r['foto']).endswith('_prueba')]
    with open(comun.REFS, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['foto', 'medida_ref_m', 'tipo_ref'])
        w.writeheader()
        w.writerows(filas + nuevas)
    print('listo: %s en input/, sus filas en refs.csv y sus elementos en output/json/'
          % ', '.join(c[0] + '.jpg' for c in CASAS))
    print('medidas reales: ' + ', '.join('%s %.2f x %.2f m' % (c[0], c[1], c[2]) for c in CASAS))


if __name__ == '__main__':
    main()
