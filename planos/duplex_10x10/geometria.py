"""
Geometria del edificio de dos departamentos sobre terreno de 10,00 x 10,00 m.

Version de 3 dormitorios por departamento, sin pasillo (el estar-comedor
hace de distribuidor) y con escalera comun de UN SOLO TRAMO RECTO de
1,20 m de ancho, sin descanso intermedio.

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
    (4.90, 0.00, 5.10, 4.40),     # muro divisorio entre departamentos
    (4.25, 4.40, 5.75, 4.55),     # muro frontal de la caja de escalera
    (4.25, 4.55, 4.40, 8.80),     # muro izq. caja de escalera
    (5.60, 4.55, 5.75, 8.80),     # muro der. caja de escalera
    (0.00, 9.90, 10.00, 10.00),   # antepecho del fondo (linea de propiedad)
    (0.00, 8.80, 0.15, 9.90),     # antepecho lateral balcon 1
    (9.85, 8.80, 10.00, 9.90),    # antepecho lateral balcon 2
]

# Muros propios del Departamento 1 (se espejan para el Departamento 2)
MUROS_UNIDAD = [
    (0.00, 8.65, 4.25, 8.80),     # muro de fondo del departamento
    (2.55, 0.15, 2.65, 3.05),     # tabique entre dorm. 1 y dorm. 2
    (0.15, 3.05, 4.90, 3.15),     # tabique dormitorios / bano + estar
    (1.55, 3.15, 1.65, 5.60),     # tabique bano / estar
    (0.15, 5.60, 4.25, 5.75),     # tabique estar / dorm. 3 + cocina
    (2.75, 5.75, 2.85, 8.65),     # tabique dorm. 3 / cocina
]

MUROS = MUROS_COMUNES + MUROS_UNIDAD + [espejar_rect(m) for m in MUROS_UNIDAD]


# --------------------------------------------------------------------------
# AMBIENTES
# --------------------------------------------------------------------------
# (nombre, medida, area_m2, poligono, (x_rotulo, y_rotulo), compacto)
# El area se recalcula del poligono mas abajo.

AMBIENTES_UNIDAD = [
    ("DORM. 1", "2,40 x 2,90", 0,
     [(0.15, 0.15), (2.55, 0.15), (2.55, 3.05), (0.15, 3.05)],
     (1.35, 1.60), False),

    ("DORM. 2", "2,25 x 2,90", 0,
     [(2.65, 0.15), (4.90, 0.15), (4.90, 3.05), (2.65, 3.05)],
     (3.775, 1.60), False),

    ("BAÑO", "1,40 x 2,45", 0,
     [(0.15, 3.15), (1.55, 3.15), (1.55, 5.60), (0.15, 5.60)],
     (0.85, 4.30), False),

    ("ESTAR - COMEDOR", "3,25 x 2,45", 0,
     [(1.65, 3.15), (4.90, 3.15), (4.90, 4.40), (4.25, 4.40),
      (4.25, 5.60), (1.65, 5.60)],
     (2.90, 4.30), False),

    ("DORM. 3", "2,60 x 2,90", 0,
     [(0.15, 5.75), (2.75, 5.75), (2.75, 8.65), (0.15, 8.65)],
     (1.45, 7.20), False),

    ("COCINA", "1,40 x 2,90", 0,
     [(2.85, 5.75), (4.25, 5.75), (4.25, 8.65), (2.85, 8.65)],
     (3.55, 7.20), False),

    ("BALCÓN", "4,10 x 1,10", 0,
     [(0.15, 8.80), (4.25, 8.80), (4.25, 9.90), (0.15, 9.90)],
     (2.20, 9.35), True),
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
# Un solo tramo recto, sin descanso intermedio.
#   ancho util 1,20 m ; caja x [4.40, 5.60], centrada en el eje divisorio
#   16 alzadas de 0.175 (piso a piso 2.80) y 15 pedadas de 0.275
#   desarrollo 15 x 0.275 = 4.125 m, del fondo (y = 9.90) hacia el frente
#   descanso de llegada de planta alta: y [4.55, 5.775] = 1.225 m

ESC = dict(
    x0=4.40, x1=5.60, y0=4.55, y1=9.90,
    ancho=1.20,
    pedada=0.275,
    alzada=0.175,
    n_pedadas=15,
    y_pie=9.90,         # arranque del tramo, al nivel del balcon
    y_llegada=5.775,    # borde superior del tramo = nivel de planta alta
)
ESC["desarrollo"] = round(ESC["n_pedadas"] * ESC["pedada"], 3)   # 4.125


def escalones():
    """Lineas de pedada del tramo unico: (x0, y, x1, y)."""
    return [(ESC["x0"], ESC["y_pie"] - k * ESC["pedada"],
             ESC["x1"], ESC["y_pie"] - k * ESC["pedada"])
            for k in range(1, ESC["n_pedadas"] + 1)]


# --------------------------------------------------------------------------
# ABERTURAS
# --------------------------------------------------------------------------
# Puertas: hueco = rectangulo vaciado en el muro
#          bisagra + ang0 + barrido definen la hoja y el arco de giro
#          (ang0 = direccion de la hoja cerrada, apoyada sobre el muro)

PUERTAS_UNIDAD = [
    # acceso de PLANTA BAJA: desde el balcon del fondo hacia la cocina
    dict(hueco=(3.15, 8.65, 4.05, 8.80), eje="h",
         bisagra=(4.05, 8.725), ang0=180, barrido=90, etiqueta="0,90"),
    # acceso de PLANTA ALTA: desde el descanso de la escalera al estar
    dict(hueco=(4.25, 4.70, 4.40, 5.55), eje="v",
         bisagra=(4.25, 4.70), ang0=90, barrido=90, etiqueta="0,85"),
    # dorm. 1 -> abre hacia el dormitorio
    dict(hueco=(1.70, 3.05, 2.50, 3.15), eje="h",
         bisagra=(2.50, 3.10), ang0=180, barrido=90, etiqueta="0,80"),
    # dorm. 2 -> abre hacia el dormitorio
    dict(hueco=(2.70, 3.05, 3.50, 3.15), eje="h",
         bisagra=(2.70, 3.10), ang0=0, barrido=-90, etiqueta="0,80"),
    # dorm. 3 -> abre hacia el dormitorio
    dict(hueco=(1.80, 5.60, 2.60, 5.75), eje="h",
         bisagra=(2.60, 5.675), ang0=180, barrido=-90, etiqueta="0,80"),
    # bano -> abre hacia el bano
    dict(hueco=(1.55, 3.60, 1.65, 4.30), eje="v",
         bisagra=(1.55, 3.60), ang0=90, barrido=90, etiqueta="0,70"),
]

# Vanos libres sin hoja: el estar-comedor se abre a la cocina
VANOS_UNIDAD = [
    (2.95, 5.60, 4.05, 5.75),
]

# Ventanas: rectangulo del hueco + orientacion del muro
VENTANAS_UNIDAD = [
    (0.65, 0.00, 2.05, 0.15, "h"),   # dorm. 1 -> frente
    (3.05, 0.00, 4.45, 0.15, "h"),   # dorm. 2 -> frente
    (0.80, 8.65, 2.20, 8.80, "h"),   # dorm. 3 -> balcon
]

# Conductos de ventilacion (el bano queda interior)
CONDUCTOS_UNIDAD = [
    (0.25, 5.05, 0.65, 5.45),
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
CONDUCTOS = CONDUCTOS_UNIDAD + [espejar_rect(c) for c in CONDUCTOS_UNIDAD]


# --------------------------------------------------------------------------
# CADENAS DE COTAS
# --------------------------------------------------------------------------

COTAS_H = [
    # detalle de ambientes (abajo)
    dict(pos=[0.00, 0.15, 2.55, 2.65, 4.90, 5.10, 7.35, 7.45, 9.85, 10.00],
         off=-0.95, lado="abajo"),
    # por departamento
    dict(pos=[0.00, 5.00, 10.00], off=-1.80, lado="abajo"),
    # total del terreno
    dict(pos=[0.00, 10.00], off=-2.65, lado="abajo"),
    # arriba: balcones y caja de escalera
    dict(pos=[0.00, 0.15, 4.25, 4.40, 5.60, 5.75, 9.85, 10.00],
         off=0.95, lado="arriba", base=10.00),
    dict(pos=[0.00, 10.00], off=1.80, lado="arriba", base=10.00),
]

COTAS_V = [
    # detalle izquierdo: dormitorios / bano-estar / dorm. 3 / balcon
    dict(pos=[0.00, 0.15, 3.05, 3.15, 5.60, 5.75, 8.65, 8.80, 10.00],
         off=-0.95, lado="izq"),
    dict(pos=[0.00, 8.80, 10.00], off=-1.80, lado="izq"),
    dict(pos=[0.00, 10.00], off=-2.65, lado="izq"),
    # detalle derecho: caja de escalera
    dict(pos=[0.00, 0.15, 3.05, 3.15, 4.40, 4.55, 9.90, 10.00],
         off=0.95, lado="der", base=10.00),
    dict(pos=[0.00, 10.00], off=1.80, lado="der", base=10.00),
]
