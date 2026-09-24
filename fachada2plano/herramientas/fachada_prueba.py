# -*- coding: utf-8 -*-
"""Genera una fachada de prueba con medidas conocidas, para validar el pipeline.

8,40 x 5,60 m, puerta 1,00 x 2,10, dos ventanas 1,20 x 1,40, cornisa, zócalo
y baranda. Se dibuja frontal y se deforma con una perspectiva, como una foto
sacada de costado. Escribe input/00_prueba.jpg, su fila en refs.csv y el
json de elementos (lo que en la fase 1 se carga a mano).

  python herramientas/fachada_prueba.py
  python run.py input/00_prueba.jpg --esquinas "300,180;1650,330;1620,1150;330,1280"

El DXF tiene que medir 8,40 x 5,60 m (±10 %).
"""
import csv
import os
import sys

import cv2
import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'src'))
import comun  # noqa: E402

ANCHO, ALTO, P = 8.4, 5.6, 100
ESQUINAS = [[300, 180], [1650, 330], [1620, 1150], [330, 1280]]
ELEMENTOS = [('zocalo', 0, 0, 8.4, 0.5), ('cornisa', 0, 5.2, 8.4, 5.6),
             ('puerta', 3.7, 0, 4.7, 2.1), ('ventana', 1.0, 1.0, 2.2, 2.4),
             ('ventana', 6.2, 1.0, 7.4, 2.4), ('baranda', 2.9, 3.2, 5.5, 4.2)]
COLOR = {'zocalo': (90, 100, 110), 'cornisa': (240, 245, 250), 'puerta': (160, 80, 20),
         'ventana': (70, 60, 50), 'baranda': None}


def main():
    W, H = int(ANCHO * P), int(ALTO * P)
    f = np.full((H, W, 3), (205, 225, 240), np.uint8)
    for tipo, x0, y0, x1, y1 in ELEMENTOS:
        p0, p1 = (int(x0 * P), H - int(y1 * P)), (int(x1 * P), H - int(y0 * P))
        if COLOR[tipo]:
            cv2.rectangle(f, p0, p1, COLOR[tipo], -1)
        cv2.rectangle(f, p0, p1, (40, 40, 40), 3)
    foto = np.full((1400, 1900, 3), (180, 200, 215), np.uint8)
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [W, 0], [W, H], [0, H]]), np.float32(ESQUINAS))
    cv2.warpPerspective(f, M, (1900, 1400), foto, borderMode=cv2.BORDER_TRANSPARENT)
    os.makedirs(comun.INPUT, exist_ok=True)
    cv2.imwrite(os.path.join(comun.INPUT, '00_prueba.jpg'), foto)

    # Elementos en píxeles de la rectificada: se calcula el mismo tamaño que
    # va a sacar 01_rectificar (promedio de lados opuestos).
    d = lambda a, b: np.hypot(b[0] - a[0], b[1] - a[1])
    tl, tr, br, bl = ESQUINAS
    rw, rh = round((d(tl, tr) + d(bl, br)) / 2), round((d(tl, bl) + d(tr, br)) / 2)
    kx, ky = rw / ANCHO, rh / ALTO
    els = [{'tipo': t, 'bbox': [round(x0 * kx), round((ALTO - y1) * ky), round(x1 * kx), round((ALTO - y0) * ky)]}
           for t, x0, y0, x1, y1 in ELEMENTOS]
    comun.escribir_json(comun.ruta_elementos('00_prueba'), {'contorno': [0, 0, rw, rh], 'elementos': els})

    filas = []
    if os.path.exists(comun.REFS):
        with open(comun.REFS, encoding='utf-8-sig') as fh:
            filas = [r for r in csv.DictReader(fh) if comun.nombre(r['foto']) != '00_prueba']
    filas += [{'foto': '00_prueba.jpg', 'medida_ref_m': '1.00', 'tipo_ref': 'ancho_puerta'},
              {'foto': '00_prueba.jpg', 'medida_ref_m': '2.10', 'tipo_ref': 'alto_puerta'}]
    with open(comun.REFS, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['foto', 'medida_ref_m', 'tipo_ref'])
        w.writeheader()
        w.writerows(filas)
    print('listo: input/00_prueba.jpg + refs.csv + output/json/00_prueba_elementos.json')


if __name__ == '__main__':
    main()
