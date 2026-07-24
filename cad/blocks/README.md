# Biblioteca de bloques — `default`

Bloques de mobiliario/sanitarios en **SVG**, en milímetros reales (el `viewBox` de cada
archivo = ancho × profundidad reales, ej. `bed.svg` = 1400×2000 mm).

## Origen y licencia
Tomados de **Plancraft** (https://github.com/pedroodb/plancraft) — **licencia MIT**
(ver `../PLANCRAFT-LICENSE.txt`). Uso comercial permitido conservando el aviso de licencia.

## Contenido (29 bloques)
Dormitorio: `bed`, `wardrobe` · Living: `sofa`, `l_sofa`, `sectional_sofa`, `coffee_table`,
`tv_console`, `bookshelf`, `floor_lamp` · Comedor: `table`, `round_table`, `chair`,
`conference_table` · Cocina: `counter`, `fridge`, `stove`, `oven` · Baño: `toilet`, `sink`,
`shower`, `bathtub` · Oficina: `desk`, `executive_desk`, `office_chair`, `filing_cabinet`,
`whiteboard` · Estructura: `staircase`, `spiral_staircase`, `car`.

## Cómo se usan
Cada bloque tiene trazo negro + relleno gris claro. Para las **láminas branded** se
recolorean a `currentColor` (trazo teñido del color del proyecto) y se insertan como
`<symbol>`/`<use>` en el SVG de la planta. Ver `../demo-olmedo.html` (demo generada).
