# FUGA: contexto para Claude

Este archivo se lee al arrancar cada sesión. Es la memoria del proyecto: si algo
cambia (una decisión, un cliente, una regla), se actualiza acá.

Dueño: Alexander Romero (Alex), Asunción, Paraguay. Se habla en español rioplatense/paraguayo, de vos.

> Lo marcado **[FALTA]** todavía no está confirmado. Completar con Alex.

---

## 1. Qué es FUGA

Estudio creativo + archivo urbano + plataforma editorial. Une cultura, espacio,
diseño y tecnología desde una misma mirada: curiosa, técnica y con criterio propio.
Instagram: **@fuga.py**. Lema de pie: "PENSAMOS CIUDAD. HACEMOS COSAS."

"FUGA ve algo que todavía no viste y sabe cómo mostrártelo."

### Cuatro ramas (no son marcas independientes)
Comparten logo, grilla, tipografía y voz; el nombre y el color indican el territorio.

| Rama | Color | Territorio |
|---|---|---|
| FUGA / CULTURAL | Rojo `#FF0402` | ciudad, archivo, revista, fotografía, cultura visual |
| FUGA / ESPACIO | Verde `#70C83B` | arquitectura, refacción, proyecto, documentación, obra |
| FUGA / TECH | Azul `#004ED8` | CAD, código, automatización, infraestructura, procesos |
| FUGA / DISEÑO | Amarillo `#FFD500` | branding, gráfico, editorial, packaging, comunicación |

Amarillo = firma de la marca madre. Ink `#0A0A0A`, Paper `#F4F2ED`.
(En el kit del Tender 001 se usó papel `#FBF5EC`, texto `#1D1B18`, verde `#73C83E`.)

### Reglas de marca (del mini manual, sep 2026)
- Una pieza = un color dominante. Cuatro colores solo en piezas de conjunto (en chico: códigos, barras, etiquetas).
- Negro y papel sostienen la grilla. Sin degradados ni pasteles. Validar contraste.
- Logo: principal por defecto; Apoyo A (sobrio/monocromo), Apoyo B (digital/tech/alto contraste). No inventar combinaciones, no alternar versiones en una pieza.
- Mínimo 120 px digital / 28 mm impreso. Resguardo: 1/4 de la altura del símbolo.
- Dos cubos = marca de agua (5–12 % de opacidad, o blanco sobre negro en portada). Nunca reemplazan al logo.
- Tipografía: títulos **Archivo ExtraBold** mayúsculas interletrado apretado; cuerpo **Manrope**; etiquetas Archivo Bold 12–13 px mayúsculas interletrado amplio.
- Feed: una rama, una idea, una grilla, una firma. Formatos: feed 1080×1350, historia 1080×1920.

### Voz
Juvenil, urbana, editorial, inteligente, directa, cool. Curiosa, segura, magnética.
Frases cortas y con ritmo; conocimiento real sin tono académico; humor seco.
Ej.: "Mirá esto." · "Esto parece un detalle. No lo es." · "La ciudad también se lee."
Evitar: infantilizar, exagerar, vender humo, sonar solemne o corporativo.

### Contenido publicado / en curso
- CULTURAL 001: "Sajonia. La gracia de no combinar." (historia + carrusel)
- ESPACIO · TENDER 001: "Una casa posible de Asunción." Axonometría con la puerta azul
  (fotos IMG_1556 e IMG_1574, ilustraciones con Magnific). Versiones v2 y v3; kit para Canva.
- Implantación 1574 (antes/después, fotorrealista); "reversión" (axonometría + render).

---

## 2. FUGA / TECH

**[FALTA]** Modelo de negocio: ¿servicio, producto, herramienta interna? Precios, oferta, a quién se vende.

### Lo que existe hoy: digitalización de tramos de fibra óptica
Del KML de relevamiento (Google Earth) al plano en AutoCAD 2026 ES, sin dibujar a mano.

- Entrada: KML/KMZ con el recorrido de la FO y los postes de ANDE.
- Proceso (Python, sin dependencias externas):
  - WGS84 → UTM 21S, proyecta cada poste sobre el recorrido.
  - Interpreta el tipo de poste, herraje, alumbrado, transformador, ganancia y notas.
  - Coloca las etiquetas sin que se pisen.
- Salida: archivos `.lsp` (capas, recorrido, postes, textos, cotas) + `.scr` para correrlos en AutoCAD.
  - Los LISP de más de 150 KB se parten porque AutoCAD los ejecuta a medias.
  - Después `TEC_LAMINAS.lsp` arma las láminas A0 a partir de la plantilla `01CMO_CERRO_MORADO.dwg`.
- Entregable: DWG + láminas A0 + PDF, con cronómetro por tramo.

Código en `work/fuga-tech/` (copiado de la carpeta `fuga` de Google Drive).

### Clientes / perfiles
| Perfil | Cliente | Particularidad |
|---|---|---|
| HTE | HTE / NUBICOM | el dato del poste viene en atributos del KML; vanos como cotas |
| TECMONT | Tecmont (norma ANDE) | el dato viene en el `<name>` del punto, ej. `12/300 rhr transformador` |

Contactos Tecmont: **Angel** y **Diego Peña** (relevamientos). **[FALTA]** Roles y contactos de HTE.

### Reglas confirmadas por el cliente (no cambiar sin preguntar)
- `*` en el nombre = el poste tiene alumbrado → se rotula `AP` junto al herraje (Angel, 24/09/2026).
- 12/309, 12/390, 12/30/ → 12/300; 12/20 → 12/200. **Solo esos casos.** El resto queda `REVISAR`.
- Alturas válidas: 7, 7.5, 9, 10.5, 11, 12, 15. Resistencias: 150, 200, 300, 500, 800.
- Etiquetas siempre a la izquierda del sentido de avance; paralelas de MANZANAS (3 m y 15 m) a la derecha.
- Las MANZANAS y los nombres de calle no salen del relevamiento: se trazan aparte.

### Tramos trabajados
Cerro Morado (plantilla de láminas), Santa María (312 postes), Justicia Electoral (lámina de referencia),
Itapúa/Misiones (23/09/2026). **[FALTA]** lista completa y estado.

---

## 3. Otras líneas de trabajo de Alex
- Arquitectura / refacción para clientes (intake por WhatsApp, cómputo métrico y presupuesto en Gs/m²).
  Hay skills para esto: `client-intake-arquitectura`, `computo-metrico-planos`, `presentacion-computo-metrico`.
- Skills de FO: `hte-fo-tramo`, `tecmont-fo-tramo`.

## 4. Dónde está cada cosa
- **Este repo**: código, contexto, notas. `work/` es la mesa de trabajo (ver `work/README.md`).
- **Google Drive** (ale.romero389@gmail.com): lo pesado.
  - `FUGA_ESTUDIO/`: logo/branding, POST FEED FUGA, TENDER AXONOMETRICO (kit Canva)
  - `fuga/`: código Python y LISP de FUGA Tech
  - `fuga-cad/1.0.0`
  - `FUGA-mini-manual-identidad-visual.pdf`
  - `brief_tender_fuga_inspiracion_axonometrica.pdf`
- No subir al repo: DWG, KMZ de clientes, renders, zips, fotos. Se quedan en Drive; acá solo se anota dónde están.

## 5. Pendientes de contexto [FALTA]
- [ ] FUGA Tech: oferta, precios, clientes objetivo, próximos productos
- [ ] Equipo / socios y quién hace qué
- [ ] Estado de cada tramo y de cada cliente
- [ ] Planes para CULTURAL / ESPACIO / DISEÑO que no están en el manual
- [ ] Material que no está en Drive (ver `work/_entrada/`)
