# Perfil de gustos — dirección de diseño

**Para:** Alexander Romero
**Última actualización:** 2026-07-24
**Estado:** patrón consolidado tras varias tandas de inspo. Listo para bajar a un sistema único.

> Este es un documento vivo. Cada vez que Alexander manda inspo nueva, se actualiza acá el
> patrón. Sirve de base para el moodboard y para las plantillas finales.

---

## Concepto de marca
**Arquitectura + tecnología.** El concepto es el trabajo (renders, proyectos, obra); el
estilo es el vestido. La marca NO es un color: es el sistema.

## Resumen en una línea
Tipografía protagonista sobre alto contraste (negro inmersivo / blanco editorial), **color
adaptativo que se transforma según el render/contenido mostrado** (sin paleta fija), atmósfera
aurora holográfica en momentos hero, motion suave con un "wow" por pantalla, y estructura
editorial numerada.

## Lo que SÍ le gusta (patrón)
1. **Tipografía como protagonista.** Grotesca bold, grande, segura. Versales para impacto,
   itálica de acento. Le gusta cuando la tipo *se mueve* (variable, reveal, desenfoque, rotación).
2. **Alto contraste puro.** Negro o blanco de base; nada de grises tibios como fondo.
3. **Color adaptativo (NO paleta fija).** El color se extrae del render/imagen que está en
   pantalla y tiñe la UI (acento, gradiente, detalles). Cada proyecto trae su propio color;
   la estructura no cambia. Ese "cambio de color" ES el concepto (transformation).
4. **Aurora / holográfico.** Gradientes fluor que brillan detrás de la tipo, alimentados por
   el color del contenido mostrado. Con criterio, en momentos hero — no en todo.
5. **Motion suave, un "wow" por pantalla.** Blur→foco, parallax, sliders de peso, repetición.
6. **Estructura editorial.** Slides numeradas, subtítulo fino con guiones, texto vertical,
   full-bleed para imagen, mockups de dispositivos para presentar.
7. **Breaks de energía.** Collage pop de color plano con grano, puntual.
8. **Branding minimalista.** Logo grotesca pesado, papel/soporte crudo, cero adorno.

## Color — sistema adaptativo (sin paleta fija)
Base neutra fija + acento que se transforma según el contenido:
| Rol | Valor | Nota |
|-----|-------|------|
| Negro base | `#0A0A0B` | mundo hero / renders / posters de tipo |
| Blanco base | `#F5F4F1` | boards de concepto / material |
| Tinta | `#141514` | texto sobre blanco |
| **Acento** | *dinámico* | extraído del render mostrado (Vibrant.js / Color Thief) |
| **Aurora** | *dinámico* | gradiente alimentado por el color del contenido |

**Receta del color adaptativo:** mostrar render → extraer color dominante (Vibrant.js /
Color Thief) → setear variables CSS (`--acento`, colores del gradiente) → la UI y el aurora
se tiñen solos con el color del proyecto.

## Tipografía
- **Display / hero:** grotesca bold (referencia: Art Grotesk / Helvetica), versales.
- **Acento:** itálica de la misma familia.
- **Datos / specs / etiquetas:** monoespaciada.

## Motion
Reveal blur→foco · parallax al scroll · sliders de fuente variable · repetición rotando ·
transiciones aurora entre secciones. Regla: **un momento fuerte por vista**, el resto quieto.

## Estructura / layout
Título grande arriba-izquierda + subtítulo fino con guiones · numeración de sección ·
texto vertical como recurso · full-bleed para render/imagen · mockups para mostrar trabajo.

## Cómo se aplica
- **Presentación web de renders:** negro full-bleed, título grotesca gigante por ambiente,
  contador de escena, nav con hover naranja, transición aurora entre ambientes. (Retoma la
  referencia @nplusj_studio con este lenguaje.)
- **Marca / IG:** alternar posters de tipo (negro) con boards numerados de concepto/material
  (blanco); naranja como hilo conductor y aurora en piezas destacadas.

## Referencias vistas
- Contemporary Type (@contemporarytype) — behance.net/gallery/221204131
- Trend boards: CONNECTION / MERGER / MATERIALS / TRANSFORMATION / ТРАНСФОРМАЦИЯ
- @nplusj_studio — presentación web de renders (ver reporte 2026-07-21)
- Branding *ésse* (Stefani Both, arquitecta)

## Decidido
- [x] **Concepto de marca:** arquitectura + tecnología.
- [x] **Color:** adaptativo, se transforma según el contenido (sin paleta fija).

## Pendiente de confirmar
- [ ] Fuente hero definitiva: grotesca tipo Art Grotesk/Helvetica vs. variable propia.
- [ ] Camino de producción: Framer (rápido) vs HTML a medida (color adaptativo sin límites).
- [ ] Uso #1 a atacar: presentación web de renders vs marca/IG.
- [ ] ¿Rebautizar la Vía 04 del moodboard con este sistema consolidado?
