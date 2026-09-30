# Reglas compartidas — Claude Code + Codex

Este archivo lo leen los dos agentes (Codex lee `AGENTS.md`; Claude lo importa
desde `CLAUDE.md`). Las reglas valen igual para ambos.

## Quién decide
- Alex decide los permisos. Ningún agente cambia su propia configuración de
  permisos (`.claude/settings.json`, `~/.codex/config.toml`) ni la del otro.
- Si una tarea necesita más permisos, el agente frena y se lo pide a Alex.

## Cómo nos pasamos el trabajo
- `HANDOFF.md` es el tablero común. Antes de empezar: leerlo. Al terminar:
  agregar una entrada al final con fecha, agente, qué hizo, qué quedó
  pendiente y para quién.
- Un solo agente trabaja sobre un archivo a la vez. Si en HANDOFF.md figura
  "EN CURSO" de otro agente sobre ese archivo, no tocarlo.
- Commits chicos y descriptivos, con prefijo `[claude]` o `[codex]`.
- Nunca `git push --force`, nunca borrar ramas ni historial.

## Siempre preguntar a Alex antes de
- Borrar o mover archivos fuera de la carpeta del proyecto.
- Instalar programas o cambiar configuración del sistema.
- Publicar, enviar mails o mensajes, o subir algo a servicios externos.
- Tocar archivos de clientes originales (DWG/DXF/PDF entregados): trabajar
  sobre copias.
