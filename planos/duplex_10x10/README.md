# Edificio de dos departamentos — terreno 10,00 × 10,00 m

Planta acotada de un edificio de dos plantas con **dos departamentos por
planta** (4 en total), sobre un terreno de 10,00 × 10,00 m ocupado en su
totalidad. Cada departamento mide **5,00 × 10,00 m**, tiene **3
dormitorios** y es espejo del otro respecto del muro divisorio.

**No hay pasillo**: el estar-comedor hace de distribuidor y todas las
puertas abren sobre él.

## Entregables

| Archivo | Uso |
|---|---|
| `plano_duplex_10x10.pdf` | Lámina A2 apaisada, escala 1:50, lista para imprimir |
| `plano_duplex_10x10.png` | Vista rápida de la misma lámina |
| `plano_duplex_10x10.dxf` | AutoCAD, unidades en metros, escala 1:1 en modelo |

## Programa por departamento

| Ambiente | Medidas | Superficie |
|---|---|---|
| Dorm. 1 | 2,15 x 3,00 | 6,45 m² |
| Dorm. 2 | 2,50 x 3,00 | 7,50 m² |
| Estar - Comedor | 3,30 x 2,35 | 7,76 m² |
| Baño | 1,35 x 2,35 | 3,17 m² |
| Dorm. 3 | 2,15 x 2,90 | 6,24 m² |
| Cocina | 1,35 x 2,90 | 3,91 m² |
| Balcón | 3,60 x 1,10 | 3,96 m² |
| **Superficie cubierta** | | **35,03 m²** |
| **Total con balcón** | | **38,99 m²** |

## Criterios adoptados

- **Dorm. 1 y Dorm. 2 al frente**, sobre la línea municipal, con ventana
  a la calle.
- **Estar-comedor en la franja central**, sin muros de pasillo: reparte a
  los tres dormitorios y al baño, y se abre a la cocina por un vano libre
  de 1,00 m.
- **Dorm. 3 y cocina al fondo**, con ventana y puerta al balcón. El
  acceso al departamento entra por la cocina.
- **Escalera común al fondo**, de dos tramos con descanso, caja de
  2,20 × 4,15 m. El ojo de escalera coincide con el eje del muro
  divisorio. 16 alzadas de 0,175 m (2,80 m piso a piso) y pedadas de
  0,275 m.
- **Balcón corredor de 1,20 m** en el fondo: es el acceso a los
  departamentos y conecta con la escalera.

## Limitaciones conocidas

- Los muros laterales son **medianeras sin aberturas**, así que sólo hay
  fachada al frente y al fondo. Los tres dormitorios ventilan a fachada,
  pero **el estar-comedor queda interior**: recibe luz a través de la
  cocina y el balcón.
- El baño ventila a la caja de escalera, que funciona como patio de aire
  y luz abierto.
- Meter tres dormitorios en 5,00 × 10,00 deja ambientes de mínima:
  Dorm. 1 y Dorm. 3 rondan los 6,3 m² y la cocina es tipo galera de
  1,35 m de ancho.

## Espesores

| Elemento | Espesor |
|---|---|
| Muros exteriores y medianeras | 0,15 m |
| Muro divisorio entre unidades | 0,20 m |
| Tabiques interiores | 0,10 m |
| Muros de la caja de escalera | 0,15 m |

## Regenerar los archivos

```bash
pip install matplotlib ezdxf
cd planos/duplex_10x10
python3 dibujar_pdf.py    # PDF + PNG
python3 dibujar_dxf.py    # DXF
```

`geometria.py` concentra toda la geometría (muros, ambientes, aberturas,
escalera y cadenas de cotas). Las superficies de la planilla se calculan
del polígono de cada ambiente, así que no pueden quedar desfasadas del
dibujo: para mover un muro alcanza con editar ese archivo y volver a
correr los dos scripts.

## Pendiente de verificar

- Retiros, altura máxima y factor de ocupación según la ordenanza
  municipal que corresponda.
- Medidas reales del terreno con relevamiento en obra.
