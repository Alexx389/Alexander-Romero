# -*- coding: utf-8 -*-
"""WGS84 -> UTM 21S, sin dependencias externas.

Implementa la proyección transversa de Mercator (Krueger) sobre el elipsoide
WGS84. Se evita pyproj a propósito: así el programa se empaqueta en un .exe
chico y corre en cualquier máquina sin instalar nada.
Precisión: milimétrica dentro de la faja, más que suficiente para planta externa.
"""
import math

A = 6378137.0                 # semieje mayor WGS84
F = 1 / 298.257223563         # achatamiento
K0 = 0.9996                   # factor de escala UTM
E2 = F * (2 - F)
EP2 = E2 / (1 - E2)


def zona_utm(lon):
    return int((lon + 180) / 6) + 1


def wgs84_a_utm(lon, lat, zona=21, sur=True):
    lon0 = (zona - 1) * 6 - 180 + 3
    lat_r = math.radians(lat)
    dl = math.radians(lon - lon0)

    N = A / math.sqrt(1 - E2 * math.sin(lat_r) ** 2)
    T = math.tan(lat_r) ** 2
    C = EP2 * math.cos(lat_r) ** 2
    Ac = math.cos(lat_r) * dl

    M = A * ((1 - E2 / 4 - 3 * E2 ** 2 / 64 - 5 * E2 ** 3 / 256) * lat_r
             - (3 * E2 / 8 + 3 * E2 ** 2 / 32 + 45 * E2 ** 3 / 1024) * math.sin(2 * lat_r)
             + (15 * E2 ** 2 / 256 + 45 * E2 ** 3 / 1024) * math.sin(4 * lat_r)
             - (35 * E2 ** 3 / 3072) * math.sin(6 * lat_r))

    x = K0 * N * (Ac + (1 - T + C) * Ac ** 3 / 6
                  + (5 - 18 * T + T ** 2 + 72 * C - 58 * EP2) * Ac ** 5 / 120) + 500000.0
    y = K0 * (M + N * math.tan(lat_r) * (Ac ** 2 / 2
              + (5 - T + 9 * C + 4 * C ** 2) * Ac ** 4 / 24
              + (61 - 58 * T + T ** 2 + 600 * C - 330 * EP2) * Ac ** 6 / 720))
    if sur:
        y += 10000000.0
    return x, y


def distancia(p, q):
    return math.hypot(q[0] - p[0], q[1] - p[1])


def rumbo(p, q):
    """Ángulo del segmento p->q en radianes."""
    return math.atan2(q[1] - p[1], q[0] - p[0])
