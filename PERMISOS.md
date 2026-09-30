# Permisos — los define Alex

Cada agente tiene su propio archivo de permisos. Los agentes no los editan;
los cambia Alex a mano.

## Claude Code → `.claude/settings.json` (en la carpeta del proyecto)
- `allow`: lo que hace sin preguntar.
- `ask`: lo que hace solo si aprobás en el momento.
- `deny`: prohibido.
Por defecto: lee, edita y commitea solo; pregunta antes de `git push` y de
llamar a Codex; nunca force-push ni toca sus propios permisos.

## Codex → `%USERPROFILE%\.codex\config.toml` (Windows)
Niveles, de más control a menos:

| Nivel | approval_policy | sandbox_mode |
|---|---|---|
| Solo lectura | `on-request` | `read-only` |
| Recomendado: edita el proyecto, pregunta lo demás | `on-request` | `workspace-write` |
| Sin preguntar dentro del proyecto | `never` | `workspace-write` |
| Total (no recomendado) | `never` | `danger-full-access` |

Ejemplo (recomendado):
```toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"
```

## Cómo trabajan juntos
1. Los dos abiertos en la misma carpeta (ej. FUGA).
2. Leen `AGENTS.md` (reglas) y `HANDOFF.md` (tablero).
3. Uno hace, anota en HANDOFF.md, el otro revisa o sigue.
4. Claude puede pedirle una revisión a Codex con `codex exec "..."`
   (te pide aprobación por la regla `ask`).
