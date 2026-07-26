# Edificio de dos departamentos — terreno 10,00 × 10,00 m

Planta acotada de un edificio de dos plantas con **dos departamentos por
planta** (4 en total), sobre un terreno de 10,00 × 10,00 m ocupado en su
totalidad. Cada departamento mide **5,00 × 10,00 m**, tiene **3
dormitorios** y es espejo del otro respecto del muro divisorio.

- **Sin pasillo**: el estar-comedor hace de distribuidor y todas las
  puertas abren sobre él.
- **Escalera común de un solo tramo recto** de 1,20 m de ancho, **sin
  descanso intermedio**.

## Entregables

| Archivo | Uso |
|---|---|
| `plano_duplex_10x10.pdf` | Lámina A2 apaisada, escala 1:50, lista para imprimir |
| `plano_duplex_10x10.png` | Vista rápida de la misma lámina |
| `plano_duplex_10x10.dxf` | AutoCAD, unidades en metros, escala 1:1 en modelo |

## Programa por departamento

| Ambiente | Medidas | Superficie |
|---|---|---|
| Dorm. 1 | 2,40 x 2,90 | 6,96 m² |
| Dorm. 2 | 2,25 x 2,90 | 6,53 m² |
| Baño | 1,40 x 2,45 | 3,43 m² |
| Estar - Comedor | 3,25 x 2,45 | 7,18 m² |
| Dorm. 3 | 2,60 x 2,90 | 7,54 m² |
| Cocina | 1,40 x 2,90 | 4,06 m² |
| Balcón | 4,10 x 1,10 | 4,51 m² |
| **Superficie cubierta** | | **35,70 m²** |
| **Total con balcón** | | **40,21 m²** |

## Escalera

Un solo tramo recto, sin descanso intermedio:

| | |
|---|---|
| Ancho útil | 1,20 m |
| Desarrollo | 4,125 m (15 pedadas de 0,275) |
| Alzadas | 16 de 0,175 m (2,80 m piso a piso) |
| Descanso de llegada | 1,20 × 1,23 m, en planta alta |

La caja está centrada sobre el eje del muro divisorio y arranca al nivel
del balcón del fondo (y = 9,90), subiendo hacia el frente.

## Accesos

Con un tramo recto la escalera llega a media profundidad del edificio, no
al fondo, así que **cada unidad tiene dos puertas de acceso** según la
planta:

- **Planta baja**: desde el balcón del fondo, a la cocina.
- **Planta alta**: desde el descanso de la escalera, al estar-comedor.

## Criterios adoptados

- **Dorm. 1 y Dorm. 2 al frente**, sobre la línea municipal, con ventana
  a la calle.
- **Estar-comedor en la franja central**, sin muros de pasillo: reparte a
  los tres dormitorios y al baño, y se abre a la cocina por un vano libre
  de 1,10 m.
- **Dorm. 3 y cocina al fondo**, con ventana y puerta al balcón.
- **Balcón corredor de 1,20 m** en el fondo, que conecta con el pie de la
  escalera.

## Limitaciones conocidas

- Los muros laterales son **medianeras sin aberturas**, así que sólo hay
  fachada al frente y al fondo. Los tres dormitorios ventilan a fachada,
  pero **el estar-comedor queda interior**: recibe luz a través de la
  cocina y el balcón.
- **El baño queda interior** y ventila por conducto de 0,40 × 0,40 con
  extractor mecánico. Con la escalera en U, el baño podía ventilar al
  hueco de escalera; con el tramo recto ese frente lo ocupa la puerta de
  acceso de planta alta.
- En planta baja, el espacio bajo el tramo queda como depósito, sin uso
  de paso.

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
