# HANDOFF

## 2026-09-30 — Setup de Codex (sesión cloud de Claude Code)

1. `node -v` → v22.22.2 (cumple ≥ 18.18). ✅
2. `npm install -g @openai/codex` → `codex --version` = `codex-cli 0.159.2`. ✅
3. Git: la carpeta ya era un repo (commit previo `82ba1b1`), así que no se hizo
   `git init` ni el commit "base: motor 01-05 + kit Claude/Codex".
   Ojo: este repo solo tiene `generar_reporte_pc.ps1`; no están el `.gitignore`,
   el motor 01-05 ni el kit Claude/Codex (probablemente viven en la PC local).
4. `codex login` → **pendiente**. La política de red del entorno cloud bloquea
   `auth.openai.com` (403 del proxy), tanto el login por navegador como
   `codex login --device-auth`. Para destrabarlo hay que agregar
   `auth.openai.com` y `api.openai.com` a los dominios permitidos del entorno
   (o subir el nivel de acceso a red) y volver a correr
   `codex login --device-auth`.
