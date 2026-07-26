"""
Geometria del edificio de dos departamentos sobre terreno de 10,00 x 10,00 m.

Version de 3 dormitorios por departamento, sin pasillo: el estar-comedor
hace de distribuidor y todas las puertas abren sobre el.

Sistema de coordenadas en METROS:
    x = 0.00  -> medianera izquierda (linea de propiedad)
    x = 10.00 -> medianera derecha
    y = 0.00  -> frente / linea municipal (calle)
    y = 10.00 -> fondo del terreno

El Departamento 1 ocupa x [0.00, 5.00] y el Departamento 2 es su espejo
respecto del eje x = 5.00.

Espesores:
    muros exteriores y medianeras ... 0.15 m
    muro divisorio entre unidades ... 0.20 m
    tabiques interiores ............. 0.10 m
    muros de la caja de escalera .... 0.15 m
"""

EJE = 5.00          # eje de simetria
LOTE = 10.00        # frente y fondo del terreno
BALCON_PROF = 1.20  # profundidad del balcon / corredor de acceso al fondo
ALTURA_PISO = 2.80  # piso a piso (16 alzadas de 0.175)


def esp(x):
    """Espeja una coordenada x respecto del eje del edificio."""
    return LOTE - x


def espejar_rect(r):
    x0, y0, x1, y1 = r
    return (esp(x1), y0, esp(x0), y1)


# --------------------------------------------------------------------------
# MUROS  (x0, y0, x1, y1)  -- rectangulos macizos
# --------------------------------------------------------------------------

MUROS_COMUNES = [
    (0.00, 0.00, 10.00, 0.15),    # fachada frente (calle)
    (0.00, 0.00, 0.15, 8.80),     # medianera izquierda
    (9.85, 0.00, 10.00, 8.80),    # medianera derecha
    (4.90, 0.00, 5.10, 5.60),     # muro divisorio entre departamentos
    (3.75, 5.60, 6.25, 5.75),     # muro frontal de la caja de escalera
    (3.75, 5.75, 3.90, 8.80),     # muro izq. caja de escalera
    (6.10, 5.75, 6.25, 8.80),     # muro der. caja de escalera
    (0.00, 9.90, 10.00, 10.00),   # antepecho del fondo (linea de propiedad)
    (0.00, 8.80, 0.15, 9.90),     # antepecho lateral balcon 1
    (9.85, 8.80, 10.00, 9.90),    # antepecho lateral balcon 2
]

# Muros propios del Departamento 1 (se espejan para el Departamento 2)
MUROS_UNIDAD = [
    (0.00, 8.65, 3.75, 8.80),     # muro de fondo del departamento
    (2.30, 0.15, 2.40, 3.15),     # tabique entre dorm. 1 y dorm. 2
    (0.15, 3.15, 4.90, 3.25),     # tabique dormitorios / estar + bano
    (3.45, 3.25, 3.55, 5.60),     # tabique estar / bano
    (0.15, 5.60, 3.75, 5.75),     # tabique estar / dorm. 3 + cocina
    (2.30, 5.75, 2.40, 8.65),     # tabique dorm. 3 / cocina
]

MUROS = MUROS_COMUNES + MUROS_UNIDAD + [espejar_rect(m) for m in MUROS_UNIDAD]


# --------------------------------------------------------------------------
# AMBIENTES
# --------------------------------------------------------------------------
# (nombre, medida, area_m2, poligono, (x_rotulo, y_rotulo), compacto)
# El area se recalcula del poligono mas abajo.

AMBIENTES_UNIDAD = [
    ("DORM. 1", "2,15 x 3,00", 0,
     [(0.15, 0.15), (2.30, 0.15), (2.30, 3.15), (0.15, 3.15)],
     (1.225, 1.65), False),

    ("DORM. 2", "2,50 x 3,00", 0,
     [(2.40, 0.15), (4.90, 0.15), (4.90, 3.15), (2.40, 3.15)],
     (3.65, 1.65), False),

    ("ESTAR - COMEDOR", "3,30 x 2,35", 0,
     [(0.15, 3.25), (3.45, 3.25), (3.45, 5.60), (0.15, 5.60)],
     (1.80, 4.42), False),

    ("BAÑO", "1,35 x 2,35", 0,
     [(3.55, 3.25), (4.90, 3.25), (4.90, 5.60), (3.55, 5.60)],
     (4.225, 4.42), False),

    ("DORM. 3", "2,15 x 2,90", 0,
     [(0.15, 5.75), (2.30, 5.75), (2.30, 8.65), (0.15, 8.65)],
     (1.225, 7.20), False),

    ("COCINA", "1,35 x 2,90", 0,
     [(2.40, 5.75), (3.75, 5.75), (3.75, 8.65), (2.40, 8.65)],
     (3.075, 7.20), True),

    ("BALCÓN", "3,60 x 1,10", 0,
     [(0.15, 8.80), (3.75, 8.80), (3.75, 9.90), (0.15, 9.90)],
     (2.70, 9.35), True),
]


def area_poligono(poly):
    """Superficie de un poligono cerrado por la formula del agrimensor."""
    s = 0.0
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        s += x0 * y1 - x1 * y0
    return abs(s) / 2.0


# La superficie declarada se recalcula del poligono para que planilla y
# dibujo no puedan quedar desfasados.
AMBIENTES_UNIDAD = [
    (n, m, round(area_poligono(p), 2), p, r, c)
    for (n, m, _, p, r, c) in AMBIENTES_UNIDAD
]


def espejar_ambiente(a):
    nombre, medida, area, poly, rot, compacto = a
    return (nombre, medida, area,
            [(esp(x), y) for (x, y) in reversed(poly)],
            (esp(rot[0]), rot[1]), compacto)


AMBIENTES_1 = AMBIENTES_UNIDAD
AMBIENTES_2 = [espejar_ambiente(a) for a in AMBIENTES_UNIDAD]

SUP_INTERIOR = round(
    sum(a[2] for a in AMBIENTES_UNIDAD if a[0] != "BALCÓN"), 2)
SUP_BALCON = next(a[2] for a in AMBIENTES_UNIDAD if a[0] == "BALCÓN")


# --------------------------------------------------------------------------
# ESCALERA  (comun a los dos departamentos)
# --------------------------------------------------------------------------
# Caja util: x [3.90, 6.10] = 2.20 m ; y [5.75, 9.90] = 4.15 m
# 16 alzadas de 0.175 m (piso a piso 2.80 m), pedadas de 0.275 m
# Descanso de llegada 1.10 + tramo 1.925 + descanso intermedio 1.125 = 4.15
# El ojo de escalera coincide con el eje del muro divisorio.

ESC = dict(
    x0=3.90, x1=6.10, y0=5.75, y1=9.90,
    ancho_tramo=1.00,        # ancho util de cada tramo
    ojo=0.20,                # ojo de escalera, sobre el eje del divisorio
    pedada=0.275,
    alzada=0.175,
    n_pedadas=7,             # pedadas visibles por tramo (8 alzadas)
    y_descanso_sup=8.80,     # borde del descanso de llegada (lado fondo)
    y_descanso_int=6.875,    # borde del descanso intermedio
)


def escalones():
    """Lineas de pedada de los dos tramos: (x0, y, x1, y)."""
    lineas = []
    for k in range(1, ESC["n_pedadas"] + 1):          # tramo 1 (ala izq.)
        y = ESC["y_descanso_sup"] - k * ESC["pedada"]
        lineas.append((ESC["x0"], y, ESC["x0"] + ESC["ancho_tramo"], y))
    for k in range(1, ESC["n_pedadas"] + 1):          # tramo 2 (ala der.)
        y = ESC["y_descanso_int"] + k * ESC["pedada"]
        lineas.append((ESC["x1"] - ESC["ancho_tramo"], y, ESC["x1"], y))
    return lineas


# --------------------------------------------------------------------------
# ABERTURAS
# --------------------------------------------------------------------------
# Puertas: hueco = rectangulo vaciado en el muro
#          bisagra + ang0 + barrido definen la hoja y el arco de giro
#          (ang0 = direccion de la hoja cerrada, apoyada sobre el muro)

PUERTAS_UNIDAD = [
    # acceso al departamento desde el balcon -> abre hacia la cocina
    dict(hueco=(2.55, 8.65, 3.45, 8.80), eje="h",
         bisagra=(3.45, 8.725), ang0=180, barrido=90, etiqueta="0,90"),
    # dorm. 1 -> abre hacia el dormitorio
    dict(hueco=(0.80, 3.15, 1.60, 3.25), eje="h",
         bisagra=(1.60, 3.20), ang0=180, barrido=90, etiqueta="0,80"),
    # dorm. 2 -> abre hacia el dormitorio
    dict(hueco=(2.45, 3.15, 3.25, 3.25), eje="h",
         bisagra=(2.45, 3.20), ang0=0, barrido=-90, etiqueta="0,80"),
    # dorm. 3 -> abre hacia el dormitorio
    dict(hueco=(0.55, 5.60, 1.35, 5.75), eje="h",
         bisagra=(1.35, 5.675), ang0=180, barrido=-90, etiqueta="0,80"),
    # bano -> abre hacia el bano
    dict(hueco=(3.45, 3.60, 3.55, 4.30), eje="v",
         bisagra=(3.50, 3.60), ang0=90, barrido=-90, etiqueta="0,70"),
]

# Vanos libres sin hoja: el estar-comedor se abre a la cocina
VANOS_UNIDAD = [
    (2.45, 5.60, 3.45, 5.75),
]

# Ventanas: rectangulo del hueco + orientacion del muro
VENTANAS_UNIDAD = [
    (0.60, 0.00, 1.80, 0.15, "h"),   # dorm. 1 -> frente
    (2.90, 0.00, 4.40, 0.15, "h"),   # dorm. 2 -> frente
    (0.55, 8.65, 1.75, 8.80, "h"),   # dorm. 3 -> balcon
    (4.10, 5.60, 4.70, 5.75, "h"),   # bano -> caja de escalera (ventilacion)
]


def espejar_puerta(p):
    x0, y0, x1, y1 = p["hueco"]
    bx, by = p["bisagra"]
    return dict(
        hueco=(esp(x1), y0, esp(x0), y1),
        eje=p["eje"],
        bisagra=(esp(bx), by),
        ang0=180 - p["ang0"],
        barrido=-p["barrido"],
        etiqueta=p["etiqueta"],
    )


PUERTAS = PUERTAS_UNIDAD + [espejar_puerta(p) for p in PUERTAS_UNIDAD]
VANOS = VANOS_UNIDAD + [espejar_rect(v) for v in VANOS_UNIDAD]
VENTANAS = ([v for v in VENTANAS_UNIDAD] +
            [espejar_rect(v[:4]) + (v[4],) for v in VENTANAS_UNIDAD])


# --------------------------------------------------------------------------
# CADENAS DE COTAS
# --------------------------------------------------------------------------

COTAS_H = [
    # detalle de ambientes (abajo)
    dict(pos=[0.00, 0.15, 2.30, 2.40, 4.90, 5.10, 7.60, 7.70, 9.85, 10.00],
         off=-0.95, lado="abajo"),
    # por departamento
    dict(pos=[0.00, 5.00, 10.00], off=-1.80, lado="abajo"),
    # total del terreno
    dict(pos=[0.00, 10.00], off=-2.65, lado="abajo"),
    # arriba: balcones y caja de escalera
    dict(pos=[0.00, 0.15, 3.75, 3.90, 6.10, 6.25, 9.85, 10.00],
         off=0.95, lado="arriba", base=10.00),
    dict(pos=[0.00, 10.00], off=1.80, lado="arriba", base=10.00),
]

COTAS_V = [
    # detalle izquierdo: dormitorios / estar / dorm. 3 / balcon
    dict(pos=[0.00, 0.15, 3.15, 3.25, 5.60, 5.75, 8.65, 8.80, 10.00],
         off=-0.95, lado="izq"),
    dict(pos=[0.00, 8.80, 10.00], off=-1.80, lado="izq"),
    dict(pos=[0.00, 10.00], off=-2.65, lado="izq"),
    # detalle derecho: bano y caja de escalera
    dict(pos=[0.00, 0.15, 3.15, 3.25, 5.60, 5.75, 9.90, 10.00],
         off=0.95, lado="der", base=10.00),
    dict(pos=[0.00, 10.00], off=1.80, lado="der", base=10.00),
]
