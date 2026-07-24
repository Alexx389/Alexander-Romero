# POC — Color adaptativo (AR Studio)

Prototipo del sistema de diseño de Alexander Romero.

## Qué es
Una tarjeta de proyecto (Casa Umbral · 028) que demuestra el **sistema de color adaptativo**:
la interfaz no tiene una paleta fija — el color se **extrae del render** que se muestra y tiñe
toda la UI. Es la idea central de la marca: *estructura fija, color que se transforma con el
contenido*.

## Cómo probarlo
Abrí `color-adaptativo.html` en el navegador:
- **Chips de mood** (Hormigón, Atardecer, Vegetación, Noche, Brasa) → cambian el protagonista
  y recolorean todo.
- **Subí tu render ↑** → carga una imagen tuya; el sistema extrae su color dominante y tiñe la
  interfaz. Todo pasa local en tu navegador (la imagen no se sube a ningún lado).
- **Modo claro / oscuro** → los dos mundos del sistema:
  - Oscuro = tarjeta editorial estilo ICONYC (nº grande, ficha mono, texto vertical, grano).
  - Claro = trend card estilo Pantone/WGSN (banda de imagen + franja de color + título + texto).

## Estado
v1 de validación de rumbo. **No es el diseño final.**
- Fuentes = del sistema (placeholder). Las definitivas se eligen después (Fontshare, etc.).
- Imagen protagonista y grano = generados por código (sin archivos externos).

## Próximos pasos
- Modo plano/técnico (presentar planos y fachadas de CAD, con el trazo teñido del color del
  proyecto). Ver `inspo/PERFIL-DE-GUSTOS.md` → "Planos y fachadas (CAD)".
- Elegir fuentes definitivas y armar la biblioteca de assets.
