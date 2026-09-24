# -*- coding: utf-8 -*-
"""Corre el pipeline fachada -> plano en orden, para una foto o para todo input/.

  01 rectificar -> 03 detectar (Claude) -> 02 escalar -> 04 DXF -> 06 paleta -> 07 pieza IG
  y al final, con 2 o más fachadas: 05 alzado de calle + portada IG.

Cada paso guarda lo que necesita en output/json/<nombre>.json: la segunda
corrida no vuelve a pedir esquinas ni puntos. Si ya hay un
<nombre>_elementos.json (cargado o corregido a mano) no se vuelve a detectar.

  python run.py --calle "SAJONIA"                  # todas las fotos de input/
  python run.py input/01_casa.jpg --clic
  python run.py input/01_casa.jpg --esquinas "x,y;x,y;x,y;x,y"
  python run.py --sin-ia                           # no llamar a Claude
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
    spec = importlib.util.spec_from_file_location(archivo[:-3], os.path.join(SRC, archivo))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def procesar(foto, a):
    nom = comun.nombre(foto)
    paso('01_rectificar.py').rectificar(foto, comun.puntos(a.esquinas, 4) if a.esquinas else None, a.clic)
    if not os.path.exists(comun.ruta_elementos(nom)):
        if a.sin_ia:
            print('%s: falta %s (sin IA: se carga a mano). Sigo con la próxima.'
                  % (nom, os.path.relpath(comun.ruta_elementos(nom), RAIZ)))
            return False
        paso('03_detectar.py').detectar(foto)
    paso('02_escalar.py').escalar(foto, [comun.puntos(p, 2) for p in a.puntos] if a.puntos else None, a.clic)
    paso('04_dibujar_dxf.py').dibujar(foto, a.rotulo)
    paso('06_paleta.py').paleta(foto)
    paso('07_export_ig.py').exportar(foto)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('foto', nargs='?', help='una foto; sin esto procesa todo input/')
    ap.add_argument('--esquinas')
    ap.add_argument('--puntos', action='append')
    ap.add_argument('--clic', action='store_true')
    ap.add_argument('--rotulo', help='rótulo de una fachada (sin números de casa)')
    ap.add_argument('--calle', default='CALLE', help='calle o barrio para el alzado y la portada')
    ap.add_argument('--sin-ia', action='store_true', help='no llamar a Claude para detectar elementos')
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
    if not a.foto and ok > 1:
        paso('05_alzado_calle.py').alzado(a.calle)
        paso('07_export_ig.py').portada(a.calle)
    print('\n%d de %d fachada(s) procesadas.' % (ok, len(lista)))


if __name__ == '__main__':
    main()
