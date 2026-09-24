# -*- coding: utf-8 -*-
"""03 Detectar: Claude (visión) marca los elementos de la fachada rectificada.

Escribe output/json/<nombre>_elementos.json con el mismo formato que en la
fase 1 se cargaba a mano:
  {"contorno": [x0,y0,x1,y1],
   "elementos": [{"tipo": "puerta", "bbox": [x0,y0,x1,y1], "nota": "..."}]}
en píxeles de la imagen rectificada.

La imagen se achica antes de mandarla (lado mayor MAX_LADO) y las cajas se
vuelven a escalar al tamaño real. Con salida estructurada el JSON siempre es
válido; igual se revisa que las cajas tengan sentido y, si no, se reintenta
una vez. Si ya existe un _elementos.json (por ejemplo corregido a mano), no
se pisa salvo con --forzar.

Necesita ANTHROPIC_API_KEY (o un perfil de `ant auth login`).

Uso:
  python src/03_detectar.py input/01_casa.jpg
  python src/03_detectar.py input/01_casa.jpg --forzar
"""
import argparse
import base64
import json
import os
import sys

import anthropic
import cv2

sys.path.insert(0, os.path.dirname(__file__))
import comun  # noqa: E402

MODELO = 'claude-opus-5'
MAX_LADO = 1568  # px: más grande el modelo lo achica igual y las coordenadas dejan de coincidir

CAJA = {'type': 'array', 'items': {'type': 'integer'}}
ESQUEMA = {
    'type': 'object',
    'properties': {
        'contorno': CAJA,
        'elementos': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'tipo': {'type': 'string', 'enum': list(comun.TIPOS)},
                    'bbox': CAJA,
                    'nota': {'type': 'string'},
                },
                'required': ['tipo', 'bbox', 'nota'],
                'additionalProperties': False,
            },
        },
    },
    'required': ['contorno', 'elementos'],
    'additionalProperties': False,
}

PROMPT = """This is a rectified, front-on photo of one building facade in Asunción, Paraguay. \
The image is {w} x {h} pixels; (0,0) is the top-left corner.

Mark the facade's architectural elements so they can be redrawn as a line elevation in CAD.

- "contorno": bounding box of the facade itself (wall, cornice and base), excluding sky, \
neighbouring buildings and the sidewalk.
- "elementos": one entry per element you can actually see. Types: {tipos}.
  puerta = pedestrian door, porton = garage/vehicle gate, zocalo = base band at ground level, \
cornisa = top moulding or parapet band, pilar = column or pilaster, alero = eave or canopy.
- Every box is [x0, y0, x1, y1] in pixels of this image, x0 < x1 and y0 < y1, tight to the element.
- "nota": a few words in Spanish only when useful (material, colour, "persiana", "reja de hierro"); \
otherwise "".

Only include what is visible. If something is hidden by a tree, a car or a pole, leave it out \
rather than guessing its extent. Do not report house numbers, signs with names, or people."""


def _b64(img):
    ok, buf = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return base64.standard_b64encode(buf.tobytes()).decode('ascii')


def _problemas(data, w, h):
    """Qué está mal en la respuesta, en coordenadas de la imagen enviada."""
    malos = []
    cajas = [('contorno', data.get('contorno'))] + [
        ('%s %d' % (e.get('tipo'), i), e.get('bbox')) for i, e in enumerate(data.get('elementos', []))]
    for nombre, b in cajas:
        if not isinstance(b, list) or len(b) != 4:
            malos.append('%s: la caja no tiene 4 números' % nombre)
        elif not (0 <= b[0] < b[2] <= w + 2 and 0 <= b[1] < b[3] <= h + 2):
            malos.append('%s: caja %s fuera de la imagen o invertida' % (nombre, b))
    return malos


def _pedir(client, img, w, h, correccion=None):
    contenido = [
        {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': _b64(img)}},
        {'type': 'text', 'text': PROMPT.format(w=w, h=h, tipos=', '.join(comun.TIPOS))},
    ]
    if correccion:
        contenido.append({'type': 'text', 'text': 'A previous answer had these problems, fix them: '
                          + '; '.join(correccion)})
    r = client.beta.messages.create(
        model=MODELO,
        max_tokens=16000,
        betas=['server-side-fallback-2026-07-01'],
        fallbacks='default',
        thinking={'type': 'adaptive'},
        output_config={'format': {'type': 'json_schema', 'schema': ESQUEMA}},
        messages=[{'role': 'user', 'content': contenido}],
    )
    if r.stop_reason == 'refusal':
        raise RuntimeError('el modelo rechazó la imagen')
    if r.stop_reason == 'max_tokens':
        raise RuntimeError('la respuesta se cortó (max_tokens)')
    return json.loads(next(b.text for b in r.content if b.type == 'text'))


def detectar(foto, forzar=False):
    nom = comun.nombre(foto)
    destino = comun.ruta_elementos(nom)
    if os.path.exists(destino) and not forzar:
        print('%s: ya hay elementos (%s), no se pisan. Usá --forzar para volver a detectar.'
              % (nom, os.path.relpath(destino, comun.RAIZ)))
        return destino
    est = comun.estado(nom)
    if 'rectificada' not in est:
        raise SystemExit('%s: primero correr 01_rectificar' % nom)

    img = cv2.imread(os.path.join(comun.RAIZ, est['rectificada']))
    H, W = img.shape[:2]
    k = min(1.0, MAX_LADO / float(max(W, H)))
    chica = cv2.resize(img, (round(W * k), round(H * k)), interpolation=cv2.INTER_AREA) if k < 1 else img
    h, w = chica.shape[:2]

    try:
        client = anthropic.Anthropic()
        data = _pedir(client, chica, w, h)
        malos = _problemas(data, w, h)
        if malos:
            data = _pedir(client, chica, w, h, malos)
            malos = _problemas(data, w, h)
    except anthropic.AuthenticationError:
        raise SystemExit('%s: sin credenciales de Claude (ANTHROPIC_API_KEY). Cargá los elementos a mano '
                         'o corré con la clave.' % nom)
    except anthropic.APIConnectionError:
        raise SystemExit('%s: no hay conexión con la API de Claude' % nom)
    except anthropic.APIStatusError as e:
        raise SystemExit('%s: la API de Claude devolvió %s: %s' % (nom, e.status_code, e.message))
    except RuntimeError as e:
        raise SystemExit('%s: %s' % (nom, e))

    def escalar(b):
        return [max(0, min(W, round(b[0] / k))), max(0, min(H, round(b[1] / k))),
                max(0, min(W, round(b[2] / k))), max(0, min(H, round(b[3] / k)))]

    ok = [e for i, e in enumerate(data['elementos'])
          if not any(m.startswith('%s %d:' % (e.get('tipo'), i)) for m in malos)]
    salida = {'contorno': escalar(data['contorno']) if not any(m.startswith('contorno') for m in malos) else [0, 0, W, H],
              'elementos': [dict(e, bbox=escalar(e['bbox'])) for e in ok],
              'origen': 'claude %s' % MODELO}
    comun.escribir_json(destino, salida)
    cuenta = {}
    for e in salida['elementos']:
        cuenta[e['tipo']] = cuenta.get(e['tipo'], 0) + 1
    print('%s: %d elementos (%s) -> %s%s' % (
        nom, len(ok), ', '.join('%d %s' % (n, t) for t, n in sorted(cuenta.items())),
        os.path.relpath(destino, comun.RAIZ),
        '  (descartados tras reintentar: %s)' % '; '.join(malos) if malos else ''))
    return destino


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('foto')
    ap.add_argument('--forzar', action='store_true', help='volver a detectar aunque ya haya elementos')
    a = ap.parse_args()
    detectar(a.foto, a.forzar)


if __name__ == '__main__':
    main()
