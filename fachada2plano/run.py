# -*- coding: utf-8 -*-
"""Corre el pipeline fachada -> plano en orden, para una foto o para todo input/.

Fase 1 (hoy): 01 rectificar -> 02 escalar -> 04 DXF, con los elementos
cargados a mano en output/json/<nombre>_elementos.json.
Los pasos 03, 05, 06 y 07 se suman cuando existan en src/.

Cada paso guarda lo que necesita en output/json/<nombre>.json: la segunda
corrida no vuelve a pedir esquinas ni puntos.

  python run.py                         # todas las fotos de input/
  python run.py input/01_casa.jpg --clic
  python run.py input/01_casa.jpg --esquinas "x,y;x,y;x,y;x,y" --puntos "x,y;x,y"
"""
import argparse
import importlib.util
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(RAIZ, 'src')
sys.path.insert(0, SRC)
import comun  # noqa: E402


def paso(archivo):
    """Los pasos empiezan con número (01_...), así que no se importan con import."""
    ruta = os.path.join(SRC, archivo)
    if not os.path.exists(ruta):
        return None
    spec = importlib.util.spec_from_file_location(archivo[:-3], ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def procesar(foto, a):
    nom = comun.nombre(foto)
    rect, esc, det, dxf = (paso('01_rectificar.py'), paso('02_escalar.py'),
                           paso('03_detectar.py'), paso('04_dibujar_dxf.py'))
    rect.rectificar(foto, comun.puntos(a.esquinas, 4) if a.esquinas else None, a.clic)
    if det and not os.path.exists(comun.ruta_elementos(nom)):
        det.detectar(foto)
    esc.escalar(foto, [comun.puntos(p, 2) for p in a.puntos] if a.puntos else None, a.clic)
    if not os.path.exists(comun.ruta_elementos(nom)):
        print('%s: falta %s (fase 1: se carga a mano). Sigo con la próxima.'
              % (nom, os.path.relpath(comun.ruta_elementos(nom), RAIZ)))
        return False
    dxf.dibujar(foto, a.rotulo)
    for archivo, fn in (('06_paleta.py', 'paleta'), ('07_export_ig.py', 'exportar')):
        mod = paso(archivo)
        if mod:
            getattr(mod, fn)(foto)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('foto', nargs='?', help='una foto; sin esto procesa todo input/')
    ap.add_argument('--esquinas')
    ap.add_argument('--puntos', action='append')
    ap.add_argument('--clic', action='store_true')
    ap.add_argument('--rotulo')
    a = ap.parse_args()

    lista = [a.foto] if a.foto else comun.fotos()
    if not lista:
        raise SystemExit('no hay fotos en input/')
    ok = 0
    for foto in lista:
        try:
            ok += bool(procesar(foto, a))
        except SystemExit as e:  # una foto sin datos no frena el lote
            if a.foto:
                raise
            print(e)
    calle = paso('05_alzado_calle.py')
    if calle and ok > 1:
        calle.alzado()
    print('\n%d de %d fachada(s) con DXF.' % (ok, len(lista)))


if __name__ == '__main__':
    main()
