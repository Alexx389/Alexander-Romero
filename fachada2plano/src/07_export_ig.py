# -*- coding: utf-8 -*-
"""07 Export IG: piezas 1080x1350 para el carrusel de FUGA TECH.

Por fachada: arriba la foto rectificada, abajo el dibujo en línea negra, a la
MISMA escala (se leen como un par), la franja con la paleta real y el pie de
marca. Portada: el alzado de calle completo.

Sistema FUGA: fondo papel, tinta, azul TECH como único color de marca.
Tipografía de fuentes/ (Archivo + Manrope) si está; si no, una del sistema.
Si existe marca/logo.png se usa en la cabecera; si no, va "FUGA" en texto.

Uso:
  python src/07_export_ig.py input/01_casa.jpg
  python src/07_export_ig.py --portada --calle "SAJONIA"
"""
import argparse
import os
import sys

import cv2
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
import comun  # noqa: E402

W, H = 1080, 1350
M = 48                      # margen lateral
PAPEL, TINTA, AZUL = '#F4F2ED', '#0A0A0A', '#004ED8'
GRIS = '#8A8781'
SERIE = 'TECH 001'
LEMA = 'PENSAMOS CIUDAD. HACEMOS COSAS. @FUGA.PY'
LOGO = os.path.join(comun.RAIZ, 'marca', 'logo.png')


def _cabecera(img, d, etiqueta):
    if os.path.exists(LOGO):
        logo = Image.open(LOGO).convert('RGBA')
        k = 56.0 / logo.height
        logo = logo.resize((round(logo.width * k), 56))
        img.paste(logo, (M, 40), logo)
    else:
        d.text((M, 38), 'FUGA', fill=TINTA, font=comun.fuente('titulo', 46))
    f = comun.fuente('etiqueta', 18)
    txt = etiqueta.upper()
    ancho = d.textlength(txt, font=f)
    d.text((W - M - ancho, 58), txt, fill=TINTA, font=f)
    d.rectangle([W - M - ancho - 26, 60, W - M - ancho - 12, 74], fill=AZUL)


def _pie(d, izq):
    d.line([(M, H - 78), (W - M, H - 78)], fill=TINTA, width=1)
    f = comun.fuente('etiqueta', 14)
    d.text((M, H - 60), izq.upper(), fill=TINTA, font=f)
    d.text((W - M - d.textlength(LEMA, font=f), H - 60), LEMA, fill=TINTA, font=f)


def _dibujo(d, geo, x0, y_base, s, grosor=3):
    """La fachada en línea: (x0, y_base) es la esquina abajo-izquierda, s = px por metro."""
    def P(x, y):
        return (x0 + x * s, y_base - y * s)

    for tipo, a, b, c, e, _ in geo['elementos']:
        p0, p1 = P(a, e), P(c, b)
        d.rectangle([p0, p1], outline=TINTA, width=max(1, grosor - 1))
        if tipo in ('puerta', 'porton'):   # marco, abierto al piso
            w, h = p1[0] - p0[0], p1[1] - p0[1]
            d.line([(p0[0] + .07 * w, p1[1]), (p0[0] + .07 * w, p0[1] + .05 * h),
                    (p1[0] - .07 * w, p0[1] + .05 * h), (p1[0] - .07 * w, p1[1])], fill=TINTA, width=1)
        elif tipo == 'ventana':
            w, h = p1[0] - p0[0], p1[1] - p0[1]
            d.rectangle([p0[0] + .07 * w, p0[1] + .07 * h, p1[0] - .07 * w, p1[1] - .07 * h], outline=TINTA, width=1)
        elif tipo in ('baranda', 'reja'):
            n = max(1, int((c - a) / 0.12))
            for i in range(1, n):
                x = p0[0] + (p1[0] - p0[0]) * i / n
                d.line([(x, p0[1]), (x, p1[1])], fill=TINTA, width=1)
    d.rectangle([P(0, geo['alto']), P(geo['ancho'], 0)], outline=TINTA, width=grosor)


def _m(v):
    return ('%.2f' % v).replace('.', ',')


def _foto(geo):
    est = geo['estado']
    img = cv2.cvtColor(cv2.imread(os.path.join(comun.RAIZ, est['rectificada'])), cv2.COLOR_BGR2RGB)
    x0, y0, x1, y1 = geo['contorno_px']
    return Image.fromarray(img[y0:y1, x0:x1])


def _paleta(nom):
    return comun.leer_json(os.path.join(comun.PALETAS, nom + '.json')).get('colores', [])


def exportar(foto):
    nom = comun.nombre(foto)
    geo = comun.geometria(nom)
    img = Image.new('RGB', (W, H), PAPEL)
    d = ImageDraw.Draw(img)
    _cabecera(img, d, '%s · %s · ASUNCIÓN' % (SERIE, 'FACHADA ' + nom.split('_')[0]))

    # Foto y dibujo a la misma escala: cada uno entra en una caja de 984 x 470.
    caja_w, caja_h = W - 2 * M, 470
    s = min(caja_w / geo['ancho'], caja_h / geo['alto'])
    fw, fh = round(geo['ancho'] * s), round(geo['alto'] * s)
    x0 = (W - fw) // 2
    et = comun.fuente('etiqueta', 15)

    y_foto = 118 + (caja_h - fh)
    img.paste(_foto(geo).resize((fw, fh), Image.LANCZOS), (x0, y_foto))
    d.text((M, 104), 'LA FOTO', fill=GRIS, font=et)

    y_base = 118 + caja_h + 50 + caja_h
    d.text((M, 118 + caja_h + 24), 'EL DIBUJO', fill=GRIS, font=et)
    _dibujo(d, geo, x0, y_base, s)
    cf = comun.fuente('cuerpo', 18)
    cota = '%s m' % _m(geo['ancho'])
    d.text((x0 + fw / 2 - d.textlength(cota, font=cf) / 2, y_base + 8), cota, fill=AZUL, font=cf)
    alto = '%s m' % _m(geo['alto'])
    d.text((x0 + fw + 10, y_base - fh / 2 - 10), alto, fill=AZUL, font=cf)

    colores = _paleta(nom)
    if colores:
        y, x, total = 1190, M, float(sum(c['proporcion'] for c in colores))
        for c in colores:
            w = (W - 2 * M) * c['proporcion'] / total
            d.rectangle([x, y, x + w, y + 44], fill=tuple(c['rgb']))
            x += w
        d.text((M, y + 52), '   '.join(c['hex'] for c in colores), fill=TINTA, font=comun.fuente('cuerpo', 15))
    _pie(d, 'Relevamiento fotográfico · ±5-10 cm')

    os.makedirs(comun.IG, exist_ok=True)
    salida = os.path.join(comun.IG, nom + '.png')
    img.save(salida)
    print('%s: pieza IG -> %s' % (nom, os.path.relpath(salida, comun.RAIZ)))
    return salida


def portada(calle='CALLE', titulo='UNA CALLE, EN PLANO.'):
    datos = comun.leer_json(os.path.join(comun.JSON, 'alzado_calle.json'))
    if not datos:
        raise SystemExit('primero correr 05_alzado_calle')
    img = Image.new('RGB', (W, H), PAPEL)
    d = ImageDraw.Draw(img)
    _cabecera(img, d, '%s · %s' % (SERIE, calle))
    tf = comun.fuente('titulo', 92)
    y = 150
    for linea in titulo.upper().split(', '):
        linea = linea if linea.endswith('.') else linea + ','
        d.text((M, y), linea, fill=TINTA, font=tf)
        y += 100

    # El alzado va centrado entre el título y el pie (con lugar abajo para paleta y dato).
    frente, alto = datos['frente_m'], datos['alto_max_m']
    arriba, abajo = y + 40, H - 78 - 150
    s = min((W - 2 * M) / frente, (abajo - arriba) / alto)
    x0, y_base = (W - frente * s) / 2, arriba + ((abajo - arriba) + alto * s) / 2
    for f in datos['fachadas']:
        _dibujo(d, comun.geometria(f['nombre']), x0 + f['x_m'] * s, y_base, s, grosor=2)
        colores = _paleta(f['nombre'])
        xc = x0 + f['x_m'] * s
        for c in colores:   # la paleta de cada casa, debajo de su fachada
            w = f['ancho_m'] * s * c['proporcion'] / float(sum(k['proporcion'] for k in colores))
            d.rectangle([xc, y_base + 22, xc + w, y_base + 46], fill=tuple(c['rgb']))
            xc += w
    d.line([(M, y_base), (W - M, y_base)], fill=TINTA, width=2)   # vereda
    cf = comun.fuente('cuerpo', 20)
    d.text((M, y_base + 64), '%d fachadas · %s m de frente' % (len(datos['fachadas']), _m(frente)),
           fill=AZUL, font=cf)
    _pie(d, 'Relevamiento fotográfico · ±5-10 cm')

    os.makedirs(comun.IG, exist_ok=True)
    salida = os.path.join(comun.IG, '00_portada.png')
    img.save(salida)
    print('portada IG -> %s' % os.path.relpath(salida, comun.RAIZ))
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('foto', nargs='?')
    ap.add_argument('--portada', action='store_true')
    ap.add_argument('--calle', default='CALLE')
    a = ap.parse_args()
    if a.portada:
        portada(a.calle)
    elif a.foto:
        exportar(a.foto)
    else:
        ap.error('pasá una foto o --portada')


if __name__ == '__main__':
    main()
