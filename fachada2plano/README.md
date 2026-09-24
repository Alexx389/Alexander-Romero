# fachada2plano: FUGA TECH 001

Fotos de fachadas de una calle → elevaciones en DXF a escala (AutoCAD 2026), alzado de calle,
paleta de colores y piezas para Instagram. Es un relevamiento fotográfico (±5–10 cm), no una mensura.

## Estado
| Paso | Qué hace | Estado |
|---|---|---|
| 01 rectificar | homografía con 4 esquinas (`--esquinas` o `--clic`) | ✅ |
| 02 escalar | px/m desde `refs.csv`; con ancho + alto corrige la proporción | ✅ |
| 03 detectar | elementos con Claude (visión) → JSON | fase 2 |
| 04 dibujar DXF | capas FACH-*, bloques puerta/ventana, cotas, foto de fondo apagada | ✅ |
| 05 alzado de calle | fachadas en fila | fase 3 |
| 06 paleta | k-means, 5 colores | fase 3 |
| 07 export IG | 1080×1350 foto \| dibujo + paleta | fase 3 |

## Uso (fase 1)
```bash
pip install -r requirements.txt

# 1. Foto en input/ con número de orden: input/01_casa.jpg
# 2. Medida de referencia en refs.csv (puede haber una de ancho y una de alto por foto):
#      foto,medida_ref_m,tipo_ref
#      01_casa.jpg,0.90,ancho_puerta
#      01_casa.jpg,2.10,alto_puerta
# 3. Esquinas de la fachada (arriba-izq, arriba-der, abajo-der, abajo-izq):
python run.py input/01_casa.jpg --clic                 # con el mouse
python run.py input/01_casa.jpg --esquinas "x,y;x,y;x,y;x,y"
# 4. Cargar a mano output/json/01_casa_elementos.json (bbox en px de la rectificada):
#      {"contorno": [x0,y0,x1,y1],
#       "elementos": [{"tipo": "puerta", "bbox": [x0,y0,x1,y1]}, ...]}
#    tipos: puerta ventana porton baranda cornisa zocalo pilar reja alero otro
# 5. Volver a correr: ya no pide nada, todo quedó en output/json/01_casa.json
python run.py
```
Si la referencia es de puerta y no marcás los puntos, toma el bbox de la primera puerta del json.
Sin `refs.csv` asume puerta de 2,10 m de alto.

El DXF lleva la foto rectificada en la capa **FACH-FOTO** (apagada) para calcar detalle a mano. La imagen
va con ruta relativa: mover la carpeta `output/` entera.

## Prueba
```bash
python herramientas/fachada_prueba.py
python run.py input/00_prueba.jpg --esquinas "300,180;1650,330;1620,1150;330,1280"
```
Fachada sintética de 8,40 × 5,60 m fotografiada en perspectiva. Resultado actual: DXF de 8,45 × 5,60 m (error 0,6 %).

## Reglas
- No inventar elementos que no se ven en la foto.
- Sin números de casa ni propietarios en los rótulos: por defecto dice `FACHADA 01` (sale del número de orden).
