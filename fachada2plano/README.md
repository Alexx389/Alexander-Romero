# fachada2plano: FUGA TECH 001

Fotos de fachadas de una calle → elevaciones en DXF a escala (AutoCAD 2026), alzado de calle,
paleta de colores y piezas para Instagram. Es un relevamiento fotográfico (±5–10 cm), no una mensura.

## Estado
| Paso | Qué hace | Estado |
|---|---|---|
| 01 rectificar | homografía con 4 esquinas (`--esquinas` o `--clic`) | ✅ |
| 02 escalar | px/m desde `refs.csv`; con ancho + alto corrige la proporción | ✅ |
| 03 detectar | Claude (visión, `claude-opus-5`) marca los elementos → JSON validado | ✅ probado con respuesta simulada, falta con API real |
| 04 dibujar DXF | capas FACH-*, bloques puerta/ventana, cotas, foto de fondo apagada | ✅ |
| 05 alzado de calle | fachadas en fila sobre la vereda, cota por casa y total | ✅ |
| 06 paleta | k-means, 5 colores por fachada (PNG + json) | ✅ |
| 07 export IG | 1080×1350: foto \| dibujo a la misma escala + paleta; portada con el alzado | ✅ |

## Uso
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # para 03_detectar; sin clave usar --sin-ia y cargar los elementos a mano

# 1. Fotos en input/ con número de orden: input/01_casa.jpg, input/02_casa.jpg...
#    (el número manda el orden en el alzado; no pongas la dirección en el nombre)
# 2. Medidas de referencia en refs.csv (una de ancho y/o una de alto por foto):
#      foto,medida_ref_m,tipo_ref
#      01_casa.jpg,0.90,ancho_puerta
#      01_casa.jpg,2.10,alto_puerta
# 3. Todo junto:
python run.py --calle "SAJONIA" --clic   # la primera vez pide las 4 esquinas de cada foto
python run.py --calle "SAJONIA"          # las siguientes ya no pide nada
```
Salidas en `output/`: `rectificadas/`, `json/`, `dxf/` (una por fachada + `alzado_calle.dxf`), `paletas/`, `ig/`.

- **Corregir la detección:** editá `output/json/<nombre>_elementos.json` (bbox en px de la rectificada) y volvé a correr: no se pisa. Para volver a detectar: `python src/03_detectar.py input/01_casa.jpg --forzar`.
- **Escala:** si la referencia es de puerta y no marcás los puntos, toma el recuadro de la puerta peatonal (nunca el portón). Si hay más de una puerta avisa, y conviene marcar con `--clic` la que mediste. Sin `refs.csv` asume puerta de 2,10 m de alto.
- **Marca:** poné las fuentes en `fuentes/` (ver `fuentes/LEEME.txt`) y el logo en `marca/logo.png`. Sin eso usa DejaVu y "FUGA" en texto.
- La foto rectificada va dentro del DXF en la capa **FACH-FOTO** (apagada), con ruta relativa: mové la carpeta `output/` entera.

## Prueba
```bash
python herramientas/fachada_prueba.py
python run.py --calle "PRUEBA"
```
Tres fachadas sintéticas fotografiadas en perspectiva. Resultado actual:

| Fachada | Real | DXF | Error |
|---|---|---|---|
| 91 | 8,40 × 5,60 | 8,45 × 5,60 | 0,6 % |
| 92 | 6,00 × 4,20 | 6,00 × 4,20 | 0 % |
| 93 | 10,00 × 6,50 | 9,99 × 6,50 | 0,1 % |

## Reglas
- No inventar elementos que no se ven en la foto.
- Sin números de casa ni propietarios en los rótulos: por defecto dice `FACHADA 01` (sale del número de orden).
