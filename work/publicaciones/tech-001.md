# TECH 001: Del mapa al plano. (PROPUESTA)

- Rama: TECH (azul `#004ED8`) · carrusel de 7 · 1080×1350
- Estado: propuesta, falta que Alex la apruebe
- Material: capturas de Google Earth (KML), del código y del plano terminado en AutoCAD

## Idea
Mostrar el proceso real de FUGA TECH: un relevamiento de postes en Google Earth se
convierte en un plano de AutoCAD sin dibujar a mano. Es el equivalente técnico de
"De la calle al dibujo".

**Ojo, confidencialidad:** no nombrar clientes ni mostrar coordenadas o datos de un tramo real sin permiso. Usar un tramo borroneado o de ejemplo.

## Slides
**01 · PORTADA** (TECH 001)
DEL MAPA AL PLANO.
312 postes. Cero dibujados a mano.

**02 · EL PROBLEMA** (PROCESO 02)
UN PUNTO EN EL MAPA NO ES UN PLANO.
Alguien camina la línea y marca cada poste en Google Earth. Después, alguien más tiene que dibujarlos uno por uno en AutoCAD. Con sus etiquetas, sus vanos y sus cotas.

**03 · EL DATO** (DATO 03)
TODO ESTÁ EN EL NOMBRE.
"12/300 rhr transformador *". Altura, resistencia, herraje, transformador. Y el asterisco quiere decir que tiene alumbrado. Lo aprendimos preguntando.

**04 · EL CÓDIGO** (CÓDIGO 04)
LEER, ORDENAR, DIBUJAR.
El programa lee el mapa, pasa las coordenadas a metros, ordena los postes sobre el recorrido y escribe las instrucciones para que AutoCAD los dibuje solo.

**05 · EL DETALLE** (DETALLE 05)
QUE NADA SE PISE.
Con 300 etiquetas, lo difícil no es dibujar: es que se lean. Cada texto busca su lugar y, si choca con el de al lado, se corre y deja una guía hasta su poste.

**06 · EL RESULTADO** (PLANO 06)
Antes/después: puntos en Google Earth | lámina A0 terminada.
DE PUNTOS A LÁMINAS.

**07 · CIERRE**
Lo que no suma, se automatiza.
FUGA TECH: CAD, automatización, infraestructura y procesos.
CTA: "Mandáselo al que todavía dibuja postes a mano."

## Caption (borrador, ~650 caracteres)
Del mapa al plano.

Un relevamiento de fibra óptica llega como cientos de puntos en Google Earth. Cada uno tiene su altura, su resistencia, su herraje. Dibujarlos a mano en AutoCAD lleva días.

Armamos un programa que lo hace solo: lee el mapa, ordena los postes sobre el recorrido, los etiqueta sin que se pisen y arma las láminas.

312 postes. Cero dibujados a mano.

FUGA TECH: CAD, automatización y procesos. Si tu trabajo tiene una parte que se repite, probablemente se pueda automatizar.

¿Conocés a alguien que todavía dibuja postes uno por uno? Mandáselo.

— FUGA TECH

## [FALTA]
- ¿Se puede mostrar un tramo real, borroneado? ¿Qué cliente autoriza?
- Dato de tiempo real: ¿cuánto llevaba antes a mano y cuánto ahora? Ese es el mejor gancho.
