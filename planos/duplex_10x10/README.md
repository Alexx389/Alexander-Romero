# Edificio de dos departamentos — terreno 10,00 × 10,00 m

Planta acotada de un edificio de dos plantas con **dos departamentos por
planta** (4 en total), sobre un terreno de 10,00 × 10,00 m ocupado en su
totalidad. Cada departamento mide **5,00 × 10,00 m** y es espejo del otro
respecto del muro divisorio.

## Entregables

| Archivo | Uso |
|---|---|
| `plano_duplex_10x10.pdf` | Lámina A2 apaisada, escala 1:50, lista para imprimir |
| `plano_duplex_10x10.png` | Vista rápida de la misma lámina |
| `plano_duplex_10x10.dxf` | AutoCAD, unidades en metros, escala 1:1 en modelo |

## Programa por departamento

| Ambiente | Medidas | Superficie |
|---|---|---|
| Dorm. 1 | 2,25 × 3,15 | 7,09 m² |
| Dorm. 2 | 2,40 × 3,15 | 7,56 m² |
| Pasillo | 3,25 × 1,00 | 3,25 m² |
| Baño | 1,40 × 2,10 | 2,94 m² |
| Cocina – comedor – estar | 3,40 × 3,00 | 13,94 m² |
| Balcón | 3,40 × 1,10 | 3,74 m² |
| **Superficie cubierta** | | **34,78 m²** |
| **Total con balcón** | | **38,52 m²** |

## Criterios adoptados

- **Dormitorios al frente**, sobre la línea municipal, que es donde hay
  fachada disponible para ventanas.
- **Cocina–comedor al fondo**, con puerta y ventana al balcón.
- **Escalera común al fondo**, de dos tramos con descanso, caja de
  2,60 × 4,25 m alineada con el muro divisorio. 16 alzadas de 0,175 m
  (2,80 m piso a piso) y pedadas de 0,275 m.
- **Balcón corredor de 1,20 m** en el fondo: es el acceso a los
  departamentos y conecta con la escalera.
- Los muros laterales son **medianeras sin aberturas**: la iluminación y
  ventilación entran por frente y fondo. El baño ventila a la caja de
  escalera, que funciona como patio de aire y luz abierto.

## Espesores

| Elemento | Espesor |
|---|---|
| Muros exteriores y medianeras | 0,15 m |
| Muro divisorio entre unidades | 0,20 m |
| Tabiques interiores | 0,10 m |

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
