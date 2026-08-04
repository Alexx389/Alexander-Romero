# Plugins de SketchUp para Arquitectura — Guía de referencia

Última actualización: agosto 2026. Compatible con SketchUp 2023–2026.

Leyenda: 🆓 gratis · 💲 pago · 🔓 código abierto (GitHub)

---

## 0. Dónde se descargan

| Fuente | Qué tiene | Link |
|---|---|---|
| Extension Warehouse | Tienda oficial, se instala desde dentro de SketchUp (`Extensiones > Extension Warehouse`) | https://extensions.sketchup.com/ |
| SketchUcation PluginStore | La biblioteca más grande de la comunidad, incluye todo Fredo6 | https://sketchucation.com/pluginstore |
| GitHub | Plugins open source, se bajan como `.rbz` desde *Releases* | https://github.com/topics/sketchup |

**Instalación manual de un `.rbz`:** `Ventana > Preferencias > Extensiones > Instalar extensión…` y elegir el archivo.

---

## 1. Base imprescindible (instalar primero, todo gratis)

| Plugin | Para qué sirve |
|---|---|
| 🆓🔓 **CleanUp³** (ThomThom) | Borra geometría basura, aristas duplicadas, materiales sin usar. Baja el peso del archivo a la mitad. Obligatorio si importás DWG o bajás modelos de 3D Warehouse. |
| 🆓🔓 **Solid Inspector²** (ThomThom) | Detecta y repara por qué un grupo no es sólido. Indispensable antes de usar herramientas sólidas o exportar. |
| 🆓 **Selection Toys / Selection Filter** (ThomThom) | Seleccionar por tipo, tamaño, capa. Ahorra muchísimo en modelos grandes. |
| 🆓 **LibFredo6** | No es un plugin en sí: es la librería que necesitan todos los plugins de Fredo6. Se instala una sola vez. |
| 🆓 **Extension Warehouse + Extension Manager** | Ya viene: activá/desactivá plugins por proyecto para que SketchUp no arranque lento. |

---

## 2. Modelado arquitectónico (muros, escaleras, techos, aberturas)

| Plugin | Qué hace | Costo |
|---|---|---|
| **1001bit Tools** | ~40 herramientas específicas de arquitectura: escaleras, muros con espesor, aberturas de puertas/ventanas, techos, barandas, cerchas, columnas. La versión Freeware ya resuelve el 80 %. | 🆓 Freeware / 💲 Pro |
| **Profile Builder 4** | Extrusión paramétrica de perfiles: zócalos, molduras, marcos, muros multicapa, vigas. Editable después de creado. Trae *Quantifier Pro* para cantidades. | 💲 |
| **Medeek Wall / Truss / Foundation / Electrical** | Framing real: muros con estructura, cerchas, fundaciones, instalación eléctrica. Nivel documentación constructiva. Truss ~USD 180 perpetuo o USD 99/año. | 💲 |
| **PlusSpec / ArchTools** | Set de herramientas BIM-lite para muros, losas, aberturas. | 💲 |
| **Instant Roof / Instant Stair / Instant Fence** (Vali Arch) | Generadores rápidos de techos con aleros, escaleras y cercos. | 💲 |
| **FlexTools** | Puertas y ventanas paramétricas de alta calidad, con apertura animada para render. | 💲 |

---

## 3. Modelado avanzado y formas complejas — suite Fredo6

Todos requieren **LibFredo6**. Desde 2024 estos 8 pasaron a pago: **USD 12 c/u o USD 40 el bundle completo**, licencia perpetua, con 30 días de prueba gratis.

| Plugin | Para qué |
|---|---|
| **JointPushPull** | Extruir superficies curvas o no planas (lo que el Push/Pull nativo no puede). Espesor de cáscaras, losas curvas. |
| **RoundCorner** | Redondear/biselar aristas en 3D. |
| **Curviloft** | Superficies entre contornos: cubiertas orgánicas, rampas, terrenos. |
| **FredoScale** | Escalar, estirar, torcer y doblar con precisión. |
| **ToolsOnSurface** | Dibujar directamente sobre superficies curvas. |
| **TopoShaper** | Terrenos limpios desde curvas de nivel (ver sección 4). |
| **Curvizard** | Limpieza y suavizado de curvas importadas de CAD. |
| **VisuHole** | Perforaciones automáticas en muros/superficies. |
| 🆓 **FredoTools** | Colección grande de utilidades sueltas, sigue gratis. |
| 🆓 **Animator / FredoSketch** | Animación y dibujo estilizado. |

Descarga: https://sketchucation.com/pluginstore?pauthor=fredo6

---

## 4. Terreno y sitio

| Plugin | Qué hace | Costo |
|---|---|---|
| **TopoShaper** (Fredo6) | Terreno con malla limpia y adaptativa desde curvas de nivel o nubes de puntos. Muy superior al Sandbox nativo. | 💲 (bundle Fredo6) |
| **Instant Road Nui** | Calles, veredas y cortes de terreno sobre topografía. | 💲 |
| **PlaceMaker** | Importa terreno, imágenes satelitales, edificios y calles de una ubicación real. Ideal para implantación y estudios de contexto. | 💲 |
| 🆓 **Sandbox Tools** | Nativo, ya viene. Suficiente para terrenos simples. | 🆓 |
| 🆓 **Eneroth Terrain Volume Calculator** | Calcula volúmenes de corte y relleno. | 🆓 |

---

## 5. Documentación: cortes, planos y LayOut

| Plugin | Qué hace | Costo |
|---|---|---|
| **Skalp** | Cortes en vivo con hatch/tramas CAD, espesores y colores de línea. Convierte SketchUp + LayOut en una herramienta real de documentación técnica. | 💲 |
| **Curic Section** | Alternativa más liviana y económica: múltiples planos de corte, animaciones de sección para presentar. | 💲 |
| 🆓 **Eneroth Flatten to Plane** | Aplana geometría a un plano — útil para armar plantas 2D. | 🆓 |
| 🆓 **Open Newer Version** (Eneroth) 🔓 | Abrir archivos guardados en versiones más nuevas de SketchUp. Salva vidas cuando un cliente manda un `.skp` de otra versión. | 🆓 |
| **LayOut** (nativo de Pro) | Escalas, cotas, rótulos, láminas. Aprovechalo antes de comprar otra cosa. | incluido |

---

## 6. Cómputo métrico y cantidades

| Plugin | Qué hace | Costo |
|---|---|---|
| **Quantifier Pro** (Mind.Sight.Studios) | Cómputo automático de áreas, volúmenes, longitudes y conteo por material/componente. Exporta a Excel. Se integra con Profile Builder. | 💲 |
| 🆓🔓 **OpenCutList** | Listas de corte y despiece con costos. Pensado para carpintería/muebles, pero sirve muy bien para encofrados, tabiquería y estructuras de madera. Open source, muy activo. | 🆓 |
| 🆓 **Eneroth Material Area Counter** | Área total por material — rápido para pisos, revoques, pintura. | 🆓 |
| 🆓 **Generate Report** (nativo) | Reporte de entidades a CSV. Básico pero gratis. | 🆓 |

---

## 7. Render y presentación

| Opción | Nota |
|---|---|
| **D5 Render** | Community Edition gratuita, sin marca de agua, tiempo real, hasta 16K. La mejor relación costo/resultado hoy. |
| **Enscape** (Chaos) | Tiempo real + VR, sincronización instantánea con el modelo. Desde ~USD 85/mes. |
| **V-Ray** (Chaos) | Máxima calidad fotorrealista, curva de aprendizaje y tiempos de render más altos. |
| **Twinmotion** | Buena alternativa, licencia más accesible. |
| **SU Podium / Brighter3D** | Livianos y baratos, para equipos con poca placa de video. |
| 🆓 **Ambient Occlusion / Styles nativos** | Para láminas conceptuales sin render. |

---

## 8. Optimización, importación y limpieza

| Plugin | Qué hace | Costo |
|---|---|---|
| **Skimp** | Importa modelos pesados (FBX, OBJ, 3DS, glTF) y los simplifica manteniendo texturas. Fundamental para meter mobiliario y vegetación sin colgar SketchUp. | 💲 |
| **Transmutr** | Similar a Skimp: convierte, reduce polígonos y prepara materiales para render. | 💲 |
| 🆓🔓 **Universal Importer** (SamuelTS) | Importa decenas de formatos 3D y reduce polígonos. Alternativa gratuita a Skimp. | 🆓 |
| 🆓🔓 **SketchUp STL** | Import/export STL para impresión 3D y maquetas. | 🆓 |
| 🆓 **Purge All / CleanUp³** | Limpieza periódica del archivo. | 🆓 |
| 🆓 **Architextures / Materials plugins** | Texturas arquitectónicas paramétricas con escala correcta. | 🆓/💲 |

---

## 9. Open source en GitHub (todo gratis, `.rbz` en Releases)

| Repo | Qué es |
|---|---|
| https://github.com/lairdubois/lairdubois-opencutlist-sketchup-extension | **OpenCutList** — despiece, cut list y costos |
| https://github.com/thomthom/solid-inspector | **Solid Inspector²** — reparar sólidos |
| https://github.com/thomthom/quadface-tools | **QuadFace Tools** — topología con quads |
| https://github.com/SketchUp/sketchup-stl | **SketchUp STL** — import/export STL |
| https://github.com/SamuelTS/SketchUp-Universal-Importer-Plugin | **Universal Importer** — importar + reducir polígonos |
| https://github.com/Eneroth3 | Decenas de utilidades chicas y muy prácticas (Face Creator, Flatten to Plane, Lift Entities, Open Newer Version) |
| https://github.com/NREL/OpenStudio-SketchUp-Plugin | **OpenStudio** — simulación energética del edificio |
| https://github.com/topics/sketchup?l=ruby | Índice general de plugins Ruby open source |

---

## 10. Plan de instalación recomendado

**Paso 1 — Gratis, hacelo hoy:**
LibFredo6 → CleanUp³ → Solid Inspector² → 1001bit Tools (freeware) → Selection Toys → OpenCutList → Universal Importer → Eneroth Open Newer Version.

**Paso 2 — Primera inversión (~USD 40):**
Bundle Fredo6 completo (JointPushPull, RoundCorner, Curviloft, FredoScale, ToolsOnSurface, TopoShaper, Curvizard, VisuHole). Es lo que más rinde por dólar en modelado arquitectónico.

**Paso 3 — Según el tipo de trabajo:**
- Documentación y planos ejecutivos → **Skalp** o **Curic Section**
- Presupuestos y cómputo → **Quantifier Pro** (o quedate con OpenCutList si alcanza)
- Muros y elementos repetitivos → **Profile Builder 4**
- Terreno y contexto urbano → **PlaceMaker** + **Instant Road Nui**
- Imágenes para cliente → **D5 Render Community** (gratis) antes de pagar Enscape

**Consejo de rendimiento:** no dejes todos los plugins activos siempre. Usá el Extension Manager para apagar los que no estés usando en el proyecto actual; SketchUp arranca mucho más rápido.

---

## Fuentes

- [SketchUp Extension Warehouse](https://extensions.sketchup.com/)
- [SketchUcation PluginStore](https://sketchucation.com/pluginstore)
- [Plugins de Fredo6 en SketchUcation](https://sketchucation.com/pluginstore?pauthor=fredo6)
- [Fredo6: extensiones que pasan a pago](https://forums.sketchup.com/t/more-fredo6-plugins-becoming-paid-extensions/191090)
- [1001bit Pro — herramientas arquitectónicas](https://www.1001bit.com/pro/)
- [Medeek Design — Truss / Wall / Foundation / Electrical](http://design.medeek.com/resources/resources.html)
- [Skalp for SketchUp](http://www.skalp4sketchup.com/)
- [Curic Section en Extension Warehouse](https://extensions.sketchup.com/extension/0e5686f3-b763-4b7b-a62f-01f1c5aa3fdb/curic-section)
- [thomthom — plugins](https://www.thomthom.net/thoughts/category/sketchup/plugin-sketchup/)
- [GitHub — topic sketchup (Ruby)](https://github.com/topics/sketchup?l=ruby)
- [D5 Render para SketchUp](https://www.d5render.com/posts/d5-converter-sketchup)
- [Chaos Enscape para SketchUp](https://www.chaos.com/enscape/sketchup-rendering)
