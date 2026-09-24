# -*- coding: utf-8 -*-
"""Rutas y estado compartido del pipeline fachada -> plano.

Cada foto tiene un json de estado en output/json/<nombre>.json que va
completando cada paso (esquinas, tamaño rectificado, escala). Los elementos
de la fachada van aparte, en output/json/<nombre>_elementos.json, que en la
fase 1 se carga a mano y en la fase 2 lo escribe 03_detectar.py.
"""
import csv
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT = os.path.join(RAIZ, 'input')
REFS = os.path.join(RAIZ, 'refs.csv')
OUT = os.path.join(RAIZ, 'output')
RECT = os.path.join(OUT, 'rectificadas')
JSON = os.path.join(OUT, 'json')
DXF = os.path.join(OUT, 'dxf')
IG = os.path.join(OUT, 'ig')
PALETAS = os.path.join(OUT, 'paletas')

EXT_FOTO = ('.jpg', '.jpeg', '.png')

TIPOS = ('puerta', 'ventana', 'porton', 'baranda', 'cornisa', 'zocalo',
         'pilar', 'reja', 'alero', 'otro')

# Puerta estandar: se usa como escala si la foto no tiene referencia medida.
ALTO_PUERTA_STD = 2.10


def nombre(foto):
    """'input/01_casa.jpg' -> '01_casa'."""
    return os.path.splitext(os.path.basename(foto))[0]


def fotos():
    """Fotos de input/ en orden de nombre (01_, 02_...)."""
    return sorted(os.path.join(INPUT, f) for f in os.listdir(INPUT)
                  if f.lower().endswith(EXT_FOTO))


def ruta_estado(nom):
    return os.path.join(JSON, nom + '.json')


def ruta_elementos(nom):
    return os.path.join(JSON, nom + '_elementos.json')


def leer_json(ruta, defecto=None):
    if not os.path.exists(ruta):
        return {} if defecto is None else defecto
    with open(ruta, encoding='utf-8') as f:
        return json.load(f)


def escribir_json(ruta, data):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def estado(nom):
    return leer_json(ruta_estado(nom))


def guardar_estado(nom, **campos):
    e = estado(nom)
    e.update(campos)
    escribir_json(ruta_estado(nom), e)
    return e


def refs(nom):
    """Filas de refs.csv para esta foto. Puede haber dos (un ancho y un alto)."""
    if not os.path.exists(REFS):
        return []
    with open(REFS, encoding='utf-8-sig') as f:
        filas = list(csv.DictReader(f))
    return [r for r in filas if nombre(r.get('foto', '')) == nom]


def puntos(txt, n):
    """'10,20;30,40' -> [[10.0, 20.0], [30.0, 40.0]], validando cantidad."""
    pts = [[float(v) for v in p.split(',')] for p in txt.replace(' ', '').split(';') if p]
    if len(pts) != n or any(len(p) != 2 for p in pts):
        raise ValueError('se esperaban %d puntos "x,y;x,y..." y llegó: %r' % (n, txt))
    return pts


def clic(img, n, titulo):
    """Ventana de OpenCV para marcar n puntos. Enter confirma, Backspace borra."""
    import cv2
    pts, vista = [], img.copy()
    esc = min(1.0, 1400.0 / max(img.shape[:2]))
    chica = cv2.resize(vista, None, fx=esc, fy=esc) if esc < 1 else vista.copy()

    def dibujar():
        v = chica.copy()
        for i, (x, y) in enumerate(pts):
            p = (int(x * esc), int(y * esc))
            cv2.circle(v, p, 6, (0, 0, 255), -1)
            cv2.putText(v, str(i + 1), (p[0] + 8, p[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.imshow(titulo, v)

    def mouse(ev, x, y, *_):
        if ev == cv2.EVENT_LBUTTONDOWN and len(pts) < n:
            pts.append([x / esc, y / esc])
            dibujar()

    cv2.namedWindow(titulo)
    cv2.setMouseCallback(titulo, mouse)
    dibujar()
    while True:
        k = cv2.waitKey(50) & 0xFF
        if k in (13, 10) and len(pts) == n:
            break
        if k == 8 and pts:
            pts.pop()
            dibujar()
        if k == 27:
            cv2.destroyAllWindows()
            raise SystemExit('cancelado')
    cv2.destroyAllWindows()
    return pts


def geometria(nom):
    """La fachada en metros, lista para dibujar en CAD o en imagen.

    Origen abajo-izquierda del contorno, Y hacia arriba. Devuelve
    {'ancho', 'alto', 'elementos': [(tipo, x0, y0, x1, y1, nota)], 'fuera',
     'estado', 'px_a_m'} donde px_a_m convierte un píxel de la rectificada.
    """
    est = estado(nom)
    if 'px_por_m_x' not in est:
        raise SystemExit('%s: primero correr 01_rectificar y 02_escalar' % nom)
    ej = leer_json(ruta_elementos(nom))
    if not ej:
        raise SystemExit('%s: falta %s' % (nom, os.path.relpath(ruta_elementos(nom), RAIZ)))
    W, H = est['ancho_px'], est['alto_px']
    sx, sy = est['px_por_m_x'], est['px_por_m_y']
    cx0, cy0, cx1, cy1 = ej.get('contorno') or [0, 0, W, H]

    def px_a_m(x, y):
        return ((x - cx0) / sx, (cy1 - y) / sy)

    els, fuera = [], 0
    for e in ej.get('elementos', []):
        x0, y0, x1, y1 = e['bbox']
        if x1 < cx0 or x0 > cx1 or y1 < cy0 or y0 > cy1:
            fuera += 1
            continue
        (a, b), (c, d) = px_a_m(min(x0, x1), max(y0, y1)), px_a_m(max(x0, x1), min(y0, y1))
        els.append((e.get('tipo', 'otro'), a, b, c, d, e.get('nota', '')))
    ancho, alto = px_a_m(cx1, cy0)
    return {'ancho': ancho, 'alto': alto, 'elementos': els, 'fuera': fuera,
            'estado': est, 'px_a_m': px_a_m, 'contorno_px': (cx0, cy0, cx1, cy1)}


FUENTES = os.path.join(RAIZ, 'fuentes')
# Las de marca van en fuentes/ (no vienen en el repo). Si no están, se usa
# una del sistema para que el export no se frene.
_FUENTE = {
    'titulo': (['Archivo-ExtraBold.ttf', 'Archivo-Bold.ttf'],
               ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold.ttf', 'arialbd.ttf']),
    'etiqueta': (['Archivo-Bold.ttf', 'Archivo-ExtraBold.ttf'],
                 ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold.ttf', 'arialbd.ttf']),
    'cuerpo': (['Manrope-Regular.ttf', 'Manrope-Medium.ttf'],
               ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'DejaVuSans.ttf', 'arial.ttf']),
}


def fuente(tipo, tam):
    from PIL import ImageFont
    marca, sistema = _FUENTE[tipo]
    for f in [os.path.join(FUENTES, n) for n in marca] + sistema:
        try:
            return ImageFont.truetype(f, tam)
        except OSError:
            continue
    return ImageFont.load_default()
