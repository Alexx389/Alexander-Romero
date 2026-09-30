# HANDOFF

## 2026-09-30 — Setup de Codex (sesión cloud de Claude Code)

1. `node -v` → v22.22.2 (cumple ≥ 18.18). ✅
2. `npm install -g @openai/codex` → `codex --version` = `codex-cli 0.159.2`. ✅
3. Git: la carpeta ya era un repo (commit previo `82ba1b1`), así que no se hizo
   `git init` ni el commit "base: motor 01-05 + kit Claude/Codex".
   Ojo: este repo solo tiene `generar_reporte_pc.ps1`; no están el `.gitignore`,
   el motor 01-05 ni el kit Claude/Codex (probablemente viven en la PC local).
4. `codex login` → ✅ `Logged in using ChatGPT` (cuenta personal).
   - Se usó `codex login --device-auth` (el login por navegador no sirve en el
     entorno cloud porque redirige a localhost).
   - Hizo falta habilitar `auth.openai.com` / `api.openai.com` en la red del
     entorno y activar "código de dispositivo para Codex" en ChatGPT →
     Configuración → Seguridad (versión web; la app de iPhone no lo muestra).
   - Ojo: el login vive en `~/.codex/` de este contenedor; en una sesión cloud
     nueva hay que repetir `codex login --device-auth`.
   - Para que Codex funcione además hay que permitir `chatgpt.com` en la red
     del entorno. Probado con `codex exec "Respondé solo: OK"` → OK.

## 2026-09-30 — [claude] Kit de trabajo conjunto
- Agregados `AGENTS.md` (reglas comunes), `CLAUDE.md`, `.claude/settings.json`
  (permisos de Claude) y `PERMISOS.md` (cómo ajustar permisos de ambos).
- Pendiente (Alex): copiar estos archivos a la carpeta FUGA de la PC, instalar
  Claude Code ahí y elegir el nivel de permisos de Codex.
