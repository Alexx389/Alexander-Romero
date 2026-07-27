# HANDOFF — Edificio Olmedo (láminas + deck branded)

> Si sos una sesión nueva de Claude: leé este archivo primero. Resume el estado, las
> decisiones de marca y el flujo de trabajo. El usuario (Alexander Romero, arquitecto,
> español) va a editar los planos a mano en **Adobe Illustrator** y necesita ayuda
> rápida y concreta con la curva de aprendizaje.

## Estado actual
- Rama de trabajo: `claude/inspo-continuacion-5bgt8m`
- Fuente CAD original (DXF, unidades en metros):
  `/root/.claude/uploads/0f0a35b5-99e2-5d68-bef2-cda187185a16/3dc7b7c6-SALON_DPTO.OLMEDO_NUEVO.dxf`
- Pipeline DXF→SVG branded: `cad/build_deck.py` (self-contained, corre con `python3 cad/build_deck.py`; requiere `ezdxf` y `pillow`).
- Deck presentable (HTML, 8 slides, teñible por color, modo claro/oscuro): `cad/deck-olmedo.html`
  - Artifact publicado: https://claude.ai/code/artifact/4e669a26-33c9-47ee-bc82-4161aad3cc5c
- **SVG EDITABLES (lo que el usuario va a editar en Illustrator):**
  - `cad/planta-alta.svg`  (4 deptos espejados + escalera central)
  - `cad/planta-baja.svg`  (salón comercial + estacionamiento)
  - Generados con `cad/export_svg.py` (en scratchpad); color explícito `#1a1a1a`, muros weight 900.

## Decisiones de marca (cerradas)
- Concepto: **arquitectura + tecnología**. Estudio: "AR STUDIO / アイコン (ICONYC)".
- Color: **ADAPTATIVO** — se extrae del render/contenido mostrado, NO hay paleta fija.
  En el deck hay chips de ejemplo (#4f7fb0 Hormigón, #e0863a Atardecer, #8caf3f Vegetación,
  #a45cc9 Noche, #d8433a Brasa) pero es solo demo.
- Estética: **line-art** fino (NO poché grueso), teñible, modo claro y oscuro.
- Estilo de referencia: Contemporary Type / editorial minimal (moodboard en `inspo/PERFIL-DE-GUSTOS.md`).

## Geometría útil del DXF (metros)
- Envolvente edificio: 24.00 × 12.90 m.
- Planta Alta ocupa x[19,47] y[65,85]; Planta Baja x[48,81] y[53,86].
- Unidad tipo A (la de las secciones): x[20.6,26.95] y[66.9,80.6].
- Organización de la unidad: frente = cocina+comedor; medio = sala+baño; fondo = 2 dormitorios.
  Área húmeda (cocina·lavadero·baño) alineada sobre un mismo eje.
- Aberturas: frente 1.20×1.00 y 0.60×0.40; contrafrente (dormitorios) blindex 1.50×2.10.
  Los textos "AxB" frente a puertas/ventanas son las medidas de cada vano.
- La pileta de cocina del DXF es un dibujo limpio → se conserva, NO se reemplaza.
- Baño (inodoro/ducha/bacha): los bloques del DXF están vacíos → se dibujan con símbolos propios.

## Quejas del usuario aún abiertas (por qué pasó a editar a mano)
- Al seccionar no se ve pulcro: muros gruesos, líneas fuera de lugar, bloques superpuestos.
- Decisión: el usuario dibuja/limpia a mano en Illustrator; Claude se encarga del
  "envoltorio" branded (color, tipografía, secciones, layout del deck).

## Flujo de trabajo acordado
1. Usuario edita `planta-alta.svg` / `planta-baja.svg` en Illustrator hasta que quede limpio.
2. Para que la versión editada se **tiña sola** en el deck: reemplazar el color `#1a1a1a`
   por `currentColor` (buscar-y-reemplazar), o pasársela a Claude y él la re-integra.
3. Con la planta limpia como base, Claude arma **secciones** por ambiente (con medidas reales
   y breve explicación) y luego la **fachada/alzado**.

## Guía rápida Illustrator (para el usuario) — lo mínimo para ir rápido
- **Abrir**: File → Open → el .svg. Si pregunta, importar como SVG editable (no imagen).
- **Muros muy gruesos → cambiar todos de una**: clic en una línea de muro → botón derecho →
  *Select → Same → Stroke Weight* (o Stroke Color) → cambiá el grosor en el panel Stroke.
- **Separar bloques superpuestos**: clic en el bloque; si es grupo, doble-clic entra al grupo.
  Arrastrá para separar. `Ctrl+Shift+G` desagrupa si necesitás.
- **Borrar líneas sueltas**: clic + Delete. Para varias: Selection tool (V) y arrastrá un
  marco, o *Select → Same*.
- **Alinear**: panel Align (Window → Align) para dejar bloques prolijos.
- **Capas**: Window → Layers; conviene separar Muros / Mobiliario / Cotas / Textos en capas.
- **Reemplazar un bloque**: borrá el feo, pegá uno nuevo (hay bloques MIT en `cad/blocks/default/*.svg`).
- **Exportar de vuelta**: File → Save As → SVG (o File → Export → SVG). Mantené el viewBox.
- **Tip color**: si vas a devolverlo al deck branded, dejá todo en un solo color y avisá para
  cambiarlo a `currentColor`.

## Archivos de referencia en el repo
- `cad/build_deck.py` — pipeline completo (muros, símbolos, ventanas, cotas, etiquetas).
- `cad/blocks/default/*.svg` — biblioteca de bloques (Plancraft, MIT) en mm reales.
- `cad/blocks/README.md`, `cad/PLANCRAFT-LICENSE.txt` — licencia.
- `inspo/PERFIL-DE-GUSTOS.md` — perfil de gustos / moodboard.
- `poc/color-adaptativo.html` — POC de color adaptativo desde imagen.
