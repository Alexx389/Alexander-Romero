"""
Genera el plano acotado en PDF (A2 apaisado, escala 1:50) y PNG.

    python3 dibujar_pdf.py
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Arc, FancyArrow

import geometria as G

AQUI = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- estilo ---
C_MURO = "#232323"
C_MURO_BORDE = "#000000"
C_PISO = "#f5f2ea"
C_BALCON = "#e4e8ea"
C_ESCALERA = "#eceff1"
C_COTA = "#0b4f9e"
C_TEXTO = "#111111"
C_ABERTURA = "#ffffff"
C_TERRENO = "#b03a2e"

ESCALA = 50.0                       # 1:50
MM_POR_M = 1000.0 / ESCALA          # 20 mm de papel por metro
HOJA_MM = (594.0, 420.0)            # A2 apaisado

# encuadre del dibujo, en metros
X_MIN, X_MAX = -3.70, 12.50
Y_MIN, Y_MAX = -3.40, 12.90


def fmt(v):
    """Formatea una cota en metros, con coma decimal."""
    return f"{round(v, 4):.2f}".replace(".", ",")


# --------------------------------------------------------------- dibujo ----
def dibujar_muros(ax):
    for (x0, y0, x1, y1) in G.MUROS:
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0,
                               facecolor=C_MURO, edgecolor=C_MURO_BORDE,
                               linewidth=0.4, zorder=5))


def dibujar_ambientes(ax, ambientes):
    for nombre, medida, area, poly, (tx, ty), compacto in ambientes:
        color = C_BALCON if nombre == "BALCÓN" else C_PISO
        ax.add_patch(Polygon(poly, closed=True, facecolor=color,
                             edgecolor="none", zorder=1))
        if compacto:
            ax.text(tx, ty + 0.12, nombre, ha="center", va="center",
                    fontsize=6.8, fontweight="bold", color=C_TEXTO, zorder=10)
            ax.text(tx, ty - 0.14, f"{medida}  ·  {fmt(area)} m²",
                    ha="center", va="center", fontsize=5.6,
                    color="#4a4a4a", zorder=10)
        else:
            ax.text(tx, ty + 0.24, nombre, ha="center", va="center",
                    fontsize=7.2, fontweight="bold", color=C_TEXTO, zorder=10)
            ax.text(tx, ty - 0.02, medida, ha="center", va="center",
                    fontsize=6.2, color="#333333", zorder=10)
            ax.text(tx, ty - 0.26, f"{fmt(area)} m²", ha="center", va="center",
                    fontsize=5.8, style="italic", color="#555555", zorder=10)


def tapar_hueco(ax, x0, y0, x1, y1):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0,
                           facecolor=C_ABERTURA, edgecolor="none", zorder=6))


def _jambas(ax, x0, y0, x1, y1, eje):
    if eje == "h":
        ax.plot([x0, x0], [y0, y1], color=C_MURO_BORDE, lw=0.5, zorder=7)
        ax.plot([x1, x1], [y0, y1], color=C_MURO_BORDE, lw=0.5, zorder=7)
    else:
        ax.plot([x0, x1], [y0, y0], color=C_MURO_BORDE, lw=0.5, zorder=7)
        ax.plot([x0, x1], [y1, y1], color=C_MURO_BORDE, lw=0.5, zorder=7)


def dibujar_puertas(ax):
    for p in G.PUERTAS:
        x0, y0, x1, y1 = p["hueco"]
        tapar_hueco(ax, x0, y0, x1, y1)
        _jambas(ax, x0, y0, x1, y1, p["eje"])

        bx, by = p["bisagra"]
        ancho = (x1 - x0) if p["eje"] == "h" else (y1 - y0)
        a1 = math.radians(p["ang0"] + p["barrido"])
        ax.plot([bx, bx + ancho * math.cos(a1)],
                [by, by + ancho * math.sin(a1)],
                color="#3a3a3a", lw=0.8, zorder=8)
        th0, th1 = sorted([p["ang0"], p["ang0"] + p["barrido"]])
        ax.add_patch(Arc((bx, by), 2 * ancho, 2 * ancho, angle=0,
                         theta1=th0, theta2=th1,
                         color="#8a8a8a", lw=0.5, linestyle=(0, (3, 2)),
                         zorder=8))


def dibujar_vanos(ax):
    for (x0, y0, x1, y1) in G.VANOS:
        tapar_hueco(ax, x0, y0, x1, y1)
        _jambas(ax, x0, y0, x1, y1, "h")


def dibujar_ventanas(ax):
    for (x0, y0, x1, y1, eje) in G.VENTANAS:
        tapar_hueco(ax, x0, y0, x1, y1)
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0,
                               facecolor="white", edgecolor=C_MURO_BORDE,
                               lw=0.5, zorder=7))
        if eje == "h":
            ym = (y0 + y1) / 2
            ax.plot([x0, x1], [ym, ym], color=C_MURO_BORDE, lw=0.5, zorder=8)
        else:
            xm = (x0 + x1) / 2
            ax.plot([xm, xm], [y0, y1], color=C_MURO_BORDE, lw=0.5, zorder=8)


def dibujar_escalera(ax):
    e = G.ESC
    ax.add_patch(Rectangle((e["x0"], e["y0"]), e["x1"] - e["x0"],
                           e["y1"] - e["y0"],
                           facecolor=C_ESCALERA, edgecolor="none", zorder=1))
    for (x0, y, x1, _) in G.escalones():
        ax.plot([x0, x1], [y, y], color="#666666", lw=0.6, zorder=8)
    ax.add_patch(Rectangle((e["x0"] + e["ancho_tramo"], e["y_descanso_int"]),
                           e["ojo"], e["y_descanso_sup"] - e["y_descanso_int"],
                           facecolor="white", edgecolor="#666666",
                           lw=0.5, zorder=8))
    ax.add_patch(FancyArrow(4.40, 8.60, 0.0, -1.60, width=0.012,
                            head_width=0.13, head_length=0.18,
                            length_includes_head=True,
                            color="#333333", zorder=9))
    ax.text(4.40, 8.72, "SUBE", ha="center", va="bottom",
            fontsize=5.2, color="#333333", zorder=9)
    ax.text(5.00, 9.55, "ESCALERA COMÚN", ha="center", va="center",
            fontsize=6.8, fontweight="bold", color=C_TEXTO, zorder=10)
    ax.text(5.00, 9.30, "2,20 x 4,15  ·  tramos de 1,00",
            ha="center", va="center", fontsize=5.6, color="#444444", zorder=10)
    ax.text(5.00, 6.45, "16 alzadas de 0,175", ha="center", va="center",
            fontsize=5.4, color="#444444", zorder=10)
    ax.text(5.00, 6.22, "pedada 0,275", ha="center", va="center",
            fontsize=5.4, color="#444444", zorder=10)


# ----------------------------------------------------------------- cotas ---
def _tick(ax, x, y, largo=0.12):
    d = largo / math.sqrt(2)
    ax.plot([x - d, x + d], [y - d, y + d], color=C_COTA, lw=0.7, zorder=12)


def cadena_h(ax, pos, y_linea, texto_arriba=True):
    ax.plot([pos[0], pos[-1]], [y_linea, y_linea],
            color=C_COTA, lw=0.6, zorder=12)
    for x in pos:
        _tick(ax, x, y_linea)
    for a, b in zip(pos, pos[1:]):
        d = b - a
        if d <= 0.001:
            continue
        chico = d < 0.45
        dy = 0.10 if texto_arriba else -0.10
        va = "bottom" if texto_arriba else "top"
        ax.text((a + b) / 2, y_linea + dy, fmt(d), ha="center", va=va,
                fontsize=5.0 if chico else 6.4, color=C_COTA,
                rotation=90 if chico else 0, zorder=12)


def cadena_v(ax, pos, x_linea, texto_izq=True):
    ax.plot([x_linea, x_linea], [pos[0], pos[-1]],
            color=C_COTA, lw=0.6, zorder=12)
    for y in pos:
        _tick(ax, x_linea, y)
    for a, b in zip(pos, pos[1:]):
        d = b - a
        if d <= 0.001:
            continue
        chico = d < 0.45
        dx = -0.10 if texto_izq else 0.10
        ha = "right" if texto_izq else "left"
        ax.text(x_linea + dx, (a + b) / 2, fmt(d), ha=ha, va="center",
                fontsize=5.0 if chico else 6.4, color=C_COTA,
                rotation=0 if chico else 90, zorder=12)


def auxiliares(ax, pos, desde, hasta, eje):
    for p in pos:
        if eje == "h":
            ax.plot([p, p], [desde, hasta], color=C_COTA, lw=0.25,
                    linestyle=(0, (4, 3)), zorder=11)
        else:
            ax.plot([desde, hasta], [p, p], color=C_COTA, lw=0.25,
                    linestyle=(0, (4, 3)), zorder=11)


def dibujar_cotas(ax):
    for c in G.COTAS_H:
        y = c.get("base", 0.00) + c["off"]
        cadena_h(ax, c["pos"], y, texto_arriba=(c["lado"] == "arriba"))
        auxiliares(ax, c["pos"], 0.00 if c["lado"] == "abajo" else 10.00,
                   y, "h")
    for c in G.COTAS_V:
        x = c.get("base", 0.00) + c["off"]
        cadena_v(ax, c["pos"], x, texto_izq=(c["lado"] == "izq"))
        auxiliares(ax, c["pos"], 0.00 if c["lado"] == "izq" else 10.00,
                   x, "v")


# ------------------------------------------------------------ anotaciones --
def anotaciones(ax):
    for x, n in ((2.50, "DEPARTAMENTO 1"), (7.50, "DEPARTAMENTO 2")):
        ax.text(x, 12.35, n, ha="center", va="center",
                fontsize=9, fontweight="bold", color=C_TEXTO)
        ax.text(x, 12.05, "5,00 x 10,00 m", ha="center", va="center",
                fontsize=6.4, color="#555555")

    ax.plot([0, 10], [-3.05, -3.05], color="#aaaaaa", lw=1.2)
    ax.text(5.00, -3.28, "CALLE  ·  LÍNEA MUNICIPAL", ha="center", va="top",
            fontsize=7, color="#666666", fontweight="bold")
    ax.text(-3.35, 5.00, "MEDIANERA", ha="center", va="center",
            fontsize=6.4, color="#888888", rotation=90)
    ax.text(11.30, 11.10, "LÍNEA DE FONDO", ha="center", va="center",
            fontsize=6.4, color="#888888")


def norte(ax, x, y, r=0.45):
    ax.add_patch(Polygon([(x, y + r), (x - r * 0.42, y - r * 0.55),
                          (x, y - r * 0.28), (x + r * 0.42, y - r * 0.55)],
                         closed=True, facecolor=C_MURO, edgecolor=C_MURO,
                         lw=0.5))
    ax.text(x, y + r + 0.18, "N", ha="center", va="bottom",
            fontsize=8, fontweight="bold")


def escala_grafica(ax, x, y, largo=5.0):
    """Escala grafica de 5 m, en tramos de 1 m."""
    alto = 0.16
    for i in range(int(largo)):
        ax.add_patch(Rectangle((x + i, y), 1.0, alto,
                               facecolor=(C_MURO if i % 2 == 0 else "white"),
                               edgecolor=C_MURO, lw=0.5))
    for i in range(int(largo) + 1):
        ax.text(x + i, y - 0.10, str(i), ha="center", va="top",
                fontsize=5.4, color="#333333")
    ax.text(x + largo / 2, y + alto + 0.10, "ESCALA GRÁFICA  ·  metros",
            ha="center", va="bottom", fontsize=5.6, color="#333333")


# ------------------------------------------------------------------ hoja ---
NOTAS = [
    "1.  Medidas en metros, tomadas a cara de muro",
    "     terminado.",
    "2.  Sin pasillo: el estar-comedor es el",
    "     distribuidor y todas las puertas abren",
    "     sobre él. Se abre a la cocina por un vano",
    "     libre de 1,00 m.",
    "3.  Los dos departamentos son espejo respecto",
    "     del muro divisorio.",
    "4.  Acceso a la planta alta por escalera común",
    "     al fondo, de dos tramos con descanso, y",
    "     balcón corredor de 1,20 m.",
    "5.  Muros laterales sobre medianera: sin",
    "     aberturas. Los tres dormitorios ventilan a",
    "     fachada (dos al frente, uno al balcón).",
    "6.  El estar-comedor queda interior: recibe luz",
    "     a través de la cocina y el balcón.",
    "7.  El baño ventila a la caja de escalera, que",
    "     funciona como patio de aire y luz.",
    "8.  Verificar retiros, altura y factor de",
    "     ocupación con la ordenanza municipal.",
    "9.  Cotas a confirmar con relevamiento en obra.",
]


def _contenido_rotulo():
    """Bloques del rotulo: (tipo, payload, alto_relativo)."""
    b = [
        ("titulo", ("EDIFICIO DE DOS DEPARTAMENTOS", 9.5, "bold"), 1.35),
        ("sub", ("Terreno de 10,00 x 10,00 m", 7, "#444444"), 1.00),
        ("regla", None, 0.35),
        ("titulo", ("PLANTA ACOTADA", 8.5, "bold"), 1.30),
        ("sub", ("3 dormitorios por unidad  ·  planta baja y alta idénticas",
                 6, "#444444"), 0.95),
        ("regla", None, 0.35),
    ]
    for k, v in (("Escala", "1 : 50"),
                 ("Acotación", "metros"),
                 ("Muros exteriores / medianeras", "0,15 m"),
                 ("Muro divisorio", "0,20 m"),
                 ("Tabiques interiores", "0,10 m"),
                 ("Altura piso a piso", "2,80 m"),
                 ("Balcón corredor (fondo)", "1,20 m"),
                 ("Escalera común", "2,20 x 4,15 m")):
        b.append(("par", (k, v, 6.0), 1.00))
    b += [
        ("regla", None, 0.55),
        ("titulo", ("PLANILLA DE SUPERFICIES", 7, "bold"), 1.25),
        ("sub_izq", ("Por departamento (5,00 x 10,00)", 6), 1.00),
    ]
    for nombre, medida, area, _, _, _ in G.AMBIENTES_UNIDAD:
        b.append(("fila3", (nombre.title(), medida, f"{fmt(area)} m²"), 1.00))
    b += [
        ("regla", None, 0.55),
        ("par_bold", ("Superficie cubierta",
                      f"{fmt(G.SUP_INTERIOR)} m²"), 1.05),
        ("par_bold", ("Total con balcón",
                      f"{fmt(G.SUP_INTERIOR + G.SUP_BALCON)} m²"), 1.05),
        ("sub_izq", ("Edificio completo: 4 departamentos", 5.8), 0.90),
        ("sub_izq", ("(2 por planta, planta baja y alta)", 5.8), 0.90),
        ("regla", None, 0.55),
        ("titulo", ("NOTAS", 7, "bold"), 1.20),
    ]
    for n in NOTAS:
        b.append(("nota", n, 0.85))
    return b


def rotulo(fig):
    ax = fig.add_axes([0.745, 0.050, 0.225, 0.900])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_linewidth(1.0)
        s.set_color("#222222")

    bloques = _contenido_rotulo()
    margen = 0.020
    # paso unitario que hace entrar exactamente todo el contenido
    paso = (1.0 - 2 * margen) / sum(h for _, _, h in bloques)

    y = 1.0 - margen
    for tipo, dato, alto in bloques:
        h = alto * paso
        yc = y - h / 2
        if tipo == "regla":
            ax.plot([0, 1], [y, y], color="#222222", lw=0.7)
        elif tipo == "titulo":
            txt, fs, peso = dato
            ax.text(0.5, yc, txt, ha="center", va="center",
                    fontsize=fs, fontweight=peso)
        elif tipo == "sub":
            txt, fs, col = dato
            ax.text(0.5, yc, txt, ha="center", va="center",
                    fontsize=fs, color=col)
        elif tipo == "sub_izq":
            txt, fs = dato
            ax.text(0.04, yc, txt, ha="left", va="center", fontsize=fs,
                    style="italic", color="#666666")
        elif tipo == "par":
            k, v, fs = dato
            ax.text(0.04, yc, k, ha="left", va="center", fontsize=fs,
                    color="#444444")
            ax.text(0.96, yc, v, ha="right", va="center", fontsize=fs,
                    fontweight="bold")
        elif tipo == "par_bold":
            k, v = dato
            ax.text(0.04, yc, k, ha="left", va="center", fontsize=6.2,
                    fontweight="bold")
            ax.text(0.96, yc, v, ha="right", va="center", fontsize=6.2,
                    fontweight="bold")
        elif tipo == "fila3":
            a, bb, c = dato
            ax.text(0.04, yc, a, ha="left", va="center", fontsize=6)
            ax.text(0.66, yc, bb, ha="right", va="center", fontsize=5.6,
                    color="#666666")
            ax.text(0.96, yc, c, ha="right", va="center", fontsize=6)
        elif tipo == "nota":
            ax.text(0.04, yc, dato, ha="left", va="center", fontsize=5.4,
                    color="#333333")
        y -= h


def construir():
    fig = plt.figure(figsize=(HOJA_MM[0] / 25.4, HOJA_MM[1] / 25.4))
    fig.patch.set_facecolor("white")

    ancho_mm = (X_MAX - X_MIN) * MM_POR_M
    alto_mm = (Y_MAX - Y_MIN) * MM_POR_M
    ax = fig.add_axes([0.030, 0.050,
                       ancho_mm / HOJA_MM[0], alto_mm / HOJA_MM[1]])
    ax.set_xlim(X_MIN, X_MAX)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.set_aspect("equal")
    ax.axis("off")

    # limite del terreno
    ax.add_patch(Rectangle((0, 0), 10, 10, facecolor="none",
                           edgecolor=C_TERRENO, lw=1.0,
                           linestyle=(0, (7, 3, 1, 3)), zorder=3))

    dibujar_ambientes(ax, G.AMBIENTES_1)
    dibujar_ambientes(ax, G.AMBIENTES_2)
    dibujar_escalera(ax)
    dibujar_muros(ax)
    dibujar_ventanas(ax)
    dibujar_puertas(ax)
    dibujar_vanos(ax)
    dibujar_cotas(ax)
    anotaciones(ax)
    norte(ax, 11.60, 8.60)
    escala_grafica(ax, -3.45, 11.45)

    rotulo(fig)
    return fig


if __name__ == "__main__":
    fig = construir()
    pdf = os.path.join(AQUI, "plano_duplex_10x10.pdf")
    png = os.path.join(AQUI, "plano_duplex_10x10.png")
    fig.savefig(pdf, format="pdf")
    fig.savefig(png, format="png", dpi=200)
    print("OK ->", pdf)
    print("OK ->", png)
