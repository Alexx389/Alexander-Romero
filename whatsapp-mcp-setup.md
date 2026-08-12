# WhatsApp MCP en Windows — guía de instalación

Guía para conectar tu WhatsApp personal a Claude Desktop / Claude Code en modo
lectura, usando un servidor MCP no oficial.

**Ambiente:** Windows 10/11
**Uso previsto:** leer y consultar chats personales. Sin envío masivo ni automatización comercial.

---

## 1. Leé esto antes de instalar nada

Esto no es una integración oficial de WhatsApp. Vale la pena que entiendas exactamente
qué estás aceptando.

### Riesgo de baneo del número

El bridge se vincula como un **dispositivo enlazado** (igual que WhatsApp Web), usando
la librería `whatsmeow`, que es una reimplementación de ingeniería inversa del protocolo.
No usa la API oficial de WhatsApp Business.

- WhatsApp **puede** detectar clientes no oficiales y suspender el número. No es lo más
  común en uso personal de solo lectura, pero el riesgo nunca es cero y **no hay
  apelación garantizada**.
- El riesgo sube muchísimo con envío automatizado, mensajes masivos o respuestas
  automáticas. Tu caso de uso (leer) es el perfil de menor riesgo, y por eso conviene
  mantenerlo así.
- Si tu número es crítico para tu trabajo, evaluá probarlo primero con un número
  secundario.

### Términos de servicio

Los Términos de WhatsApp prohíben acceder al servicio por "medios automatizados" o
clientes no autorizados. Usar esto es, en los hechos, una violación de los ToS. La
consecuencia realista es la pérdida de la cuenta, no una acción legal — pero es una
decisión consciente que estás tomando.

### Privacidad

- Todo el historial que sincronices queda en **SQLite sin cifrar** en tu disco
  (`whatsapp-bridge/store/messages.db`). Cualquiera con acceso a tu PC lo puede leer.
- Incluye mensajes de otras personas que **no consintieron** que sus mensajes se guarden
  así ni que pasen por un modelo de IA. Tenelo presente si manejás información sensible
  de clientes.
- Los mensajes se envían a Anthropic **solo** cuando vos hacés una consulta que los usa.
  El almacenamiento local en sí no manda nada a ningún lado.
- El repo genera un token en `.bridge-token` que autoriza a mandar mensajes por la API
  local. No lo compartas.

### Mantenimiento

Cuando WhatsApp cambia el protocolo, estos clientes se rompen hasta que alguien los
actualiza. Contá con romper y actualizar cada tanto. Por eso la elección del repo
(abajo) es la decisión más importante de toda la guía.

---

## 2. Qué repo usar, y por qué NO el más popular

Pediste evaluar `lharries/whatsapp-mcp`. Lo revisé a fondo y **te recomiendo un fork**.

| Repo | Estrellas | Último commit de código | whatsmeow | Veredicto |
|---|---|---|---|---|
| `lharries/whatsapp-mcp` | ~6.100 | **abril 2025** | marzo 2025 | ❌ Abandonado |
| **`verygoodplugins/whatsapp-mcp`** | ~140 | **agosto 2026 (ayer)** | julio 2026 | ✅ **Recomendado** |
| `felipeadeildo/whatsapp-mcp` | ~84 | junio 2026 | junio 2026 | 🟡 Alternativa |
| `jlucaso1/whatsapp-mcp-ts` | ~70 | agosto 2026 | Baileys (TS) | 🟡 Si preferís Node |

El detalle clave: GitHub muestra `lharries` como actualizado hoy, pero eso es solo
movimiento de estrellas. **El código no se toca desde abril de 2025**, tiene 222 issues
abiertas y su `whatsmeow` está clavado en marzo de 2025. Con más de un año de atraso, es
muy probable que falle el pairing con un error `Client outdated` o `HTTP 405`, porque
WhatsApp sube periódicamente la versión mínima de cliente enlazado que acepta.

`verygoodplugins/whatsapp-mcp` es un fork directo de ese repo, con la **misma
arquitectura** que pediste (bridge en Go + servidor MCP en Python, SQLite local), pero
mantenido de verdad: releases regulares, CI, y `whatsmeow` al día. Además suma
autenticación por token en la API local y confinamiento de rutas de media, que el
original no tiene.

**Arquitectura (dos procesos):**

```
WhatsApp (tu teléfono)
        │  QR / dispositivo enlazado
        ▼
whatsapp-bridge (Go)  ──►  store/messages.db  (SQLite local)
        │                  store/whatsapp.db  (sesión)
        │  REST en localhost:8080
        ▼
whatsapp-mcp-server (Python)  ◄── stdio ──  Claude Desktop / Claude Code
```

El **bridge lo arrancás vos en una terminal y lo dejás corriendo**. El servidor MCP lo
levanta Claude solo, no lo ejecutás a mano.

---

## 3. Requisitos previos

Abrí PowerShell y instalá lo que falte:

```powershell
winget install GoLang.Go            # Go 1.25 o superior
winget install Python.Python.3.12   # Python 3.11 o superior
winget install astral-sh.uv         # gestor de paquetes uv
winget install MSYS2.MSYS2          # necesario para el compilador C (ver abajo)
```

Cerrá y reabrí PowerShell para que tome el PATH, y verificá:

```powershell
go version ; python --version ; uv --version
```

### El paso que rompe a todo el mundo en Windows: CGO

El bridge usa `go-sqlite3`, que es una librería C. En Windows necesita un compilador
de C, que no viene con Go. Sin esto la compilación falla con un error tipo
`cgo: C compiler "gcc" not found`.

1. Abrí **MSYS2 UCRT64** (desde el menú Inicio) e instalá gcc:

   ```bash
   pacman -S mingw-w64-ucrt-x86_64-gcc
   ```

2. Agregá `C:\msys64\ucrt64\bin` al PATH de tu usuario:

   ```powershell
   [Environment]::SetEnvironmentVariable(
     "Path",
     [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\msys64\ucrt64\bin",
     "User"
   )
   ```

3. Reabrí PowerShell, activá CGO y confirmá que gcc responde:

   ```powershell
   go env -w CGO_ENABLED=1
   gcc --version
   ```

Si `gcc --version` imprime una versión, ya está lo difícil.

---

## 4. Clonar y compilar

```powershell
cd $HOME
git clone https://github.com/verygoodplugins/whatsapp-mcp.git
cd whatsapp-mcp\whatsapp-bridge
go build -o whatsapp-bridge.exe .
```

La primera compilación baja dependencias y tarda unos minutos. Si falla con un error de
`gcc` o `cgo`, volvé al paso 3.

---

## 5. Vincular tu WhatsApp (el QR)

Este paso es **inherentemente manual y presencial** — nadie lo puede hacer por vos, ni
yo desde acá: el QR se dibuja en tu terminal y se escanea con tu teléfono.

```powershell
cd $HOME\whatsapp-mcp\whatsapp-bridge
.\whatsapp-bridge.exe
```

Vas a ver:

1. Un **banner con el token** de la API local (se guarda solo en `store\.bridge-token`;
   no tenés que copiarlo a ningún lado si todo corre desde el mismo directorio).
2. Un **código QR ASCII**.

En el teléfono: **WhatsApp → Configuración → Dispositivos vinculados → Vincular un
dispositivo** → escaneá el QR.

> **Si el QR se ve deformado:** usá Windows Terminal, no la consola vieja `cmd.exe`.
> Bajá el tamaño de fuente (Ctrl + `-`) hasta que el QR entre completo en pantalla.

Después de vincular, empieza la sincronización. **Puede tardar varios minutos** con
historiales grandes. Por defecto WhatsApp manda aproximadamente los **últimos 3 meses**
— la ventana exacta la decide tu teléfono.

**Dejá esta terminal abierta.** Si cerrás el bridge, Claude deja de ver mensajes nuevos
(los ya guardados en SQLite siguen consultables).

### Si querés más historial

Solo funciona en un pairing nuevo, antes de vincular:

```powershell
.\whatsapp-bridge.exe --full-history-pair
```

Si ya vinculaste, tenés que desvincular y repetir el QR.

---

## 6. Configuración (puertos y variables)

**No necesitás tocar nada para el caso estándar.** Las rutas por defecto se resuelven
contra la ubicación del propio script, no contra el directorio actual, así que mientras
bridge y servidor MCP vivan en el mismo clon, se encuentran solos.

Configurá algo solo si tenés un conflicto real:

| Variable | Default | Cuándo tocarla |
|---|---|---|
| `WHATSAPP_BRIDGE_PORT` | `8080` | Si ya tenés algo en el 8080 |
| `WHATSAPP_API_URL` | `http://localhost:8080/api` | Debe coincidir con el puerto de arriba |
| `WHATSAPP_DB_PATH` | `whatsapp-bridge/store/messages.db` | Si movés la DB |
| `WHATSMEOW_DB_PATH` | `whatsapp-bridge/store/whatsapp.db` | Si movés la sesión |
| `WHATSAPP_DEVICE_NAME` | `whatsmeow` | Para que se vea con nombre lindo en Dispositivos vinculados |
| `WEBHOOK_ENABLED` | `true` | **Poné `false`** — no lo necesitás para leer |

Para cambiar el puerto, copiá `.env.example` a `.env` en la raíz del repo y editá.

> **Nota de seguridad:** el bridge solo acepta conexiones de loopback y exige el token
> bearer en cada request. No lo expongas a la red (`0.0.0.0`) sin poner autenticación
> delante: quien llega a esa API puede leer **y enviar** mensajes por tu cuenta.

---

## 7. Bloque de configuración para Claude

### Claude Desktop

Archivo: `%APPDATA%\Claude\claude_desktop_config.json`

Abrilo rápido con:

```powershell
notepad $env:APPDATA\Claude\claude_desktop_config.json
```

```json
{
  "mcpServers": {
    "whatsapp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/TU_USUARIO/whatsapp-mcp/whatsapp-mcp-server",
        "run",
        "main.py"
      ]
    }
  }
}
```

Reemplazá `TU_USUARIO` por tu usuario real de Windows.

> **Dos detalles de Windows que causan la mayoría de los fallos:**
>
> 1. **Usá barras normales `/`** en el JSON. Con backslashes tenés que escaparlas
>    (`C:\\Users\\...`) y es el error más común.
> 2. Claude Desktop **no siempre hereda el PATH**. Si el server no levanta, poné la ruta
>    absoluta a `uv.exe` en `command`. Averiguala con `(Get-Command uv).Source`, y
>    escribila con `/`, por ejemplo
>    `"C:/Users/TU_USUARIO/.local/bin/uv.exe"`.

Después de guardar, **cerrá Claude Desktop del todo** — incluido el ícono de la bandeja
del sistema, no solo la ventana — y volvé a abrirlo.

### Claude Code

Desde la raíz del proyecto:

```powershell
claude mcp add whatsapp -- uv --directory C:/Users/TU_USUARIO/whatsapp-mcp/whatsapp-mcp-server run main.py
```

Verificá con `claude mcp list`.

---

## 8. Restringir a solo lectura

El servidor **no tiene un modo solo-lectura nativo**: junto con las tools de consulta
expone `send_message`, `send_file`, `send_audio_message`, `send_reaction` y
`mark_messages_read`.

Como dijiste que es solo para consultar, conviene bloquear las de escritura desde los
permisos de Claude, sin tocar el código (así no hay que re-parchear en cada `git pull`).
En tu `settings.json` de Claude Code:

```json
{
  "permissions": {
    "deny": [
      "mcp__whatsapp__send_message",
      "mcp__whatsapp__send_file",
      "mcp__whatsapp__send_audio_message",
      "mcp__whatsapp__send_reaction",
      "mcp__whatsapp__mark_messages_read"
    ]
  }
}
```

Incluí `mark_messages_read` a propósito: manda acuses de lectura reales a tus contactos.
Leer o buscar mensajes **no** los marca como leídos, así que si no bloqueás esa tool,
podrías marcar chats como leídos sin querer y delatar que algo los está leyendo.

En Claude Desktop no hay un `deny` equivalente por tool; ahí el control es que cada
llamada te pide aprobación, así que simplemente rechazá las de envío. Si preferís algo
más contundente, comentá los decoradores `@mcp.tool()` de esas funciones en
`whatsapp-mcp-server/main.py` — pero recordá reaplicarlo después de cada actualización.

---

## 9. Probarlo

Con el bridge corriendo y Claude reiniciado:

1. **Verificá que las tools aparezcan.** En Claude Desktop, el ícono de herramientas
   debería listar el server `whatsapp`. En Claude Code: `/mcp`.

2. **Probá de menor a mayor.** Empezá por algo que no dependa del historial:

   > "Listá mis chats de WhatsApp más recientes"

   Después algo con búsqueda:

   > "Buscá en mis contactos de WhatsApp a alguien que se llame Juan"

   Y por último una consulta real:

   > "Mostrame los últimos 20 mensajes de mi chat con [nombre]"
   > "¿De qué hablamos con [nombre] la semana pasada?"
   > "Buscá en mis chats dónde se mencionó el presupuesto"

3. **Chequeo directo de la base**, si algo no cierra. Esto te dice si el problema es la
   sincronización o la conexión con Claude:

   ```powershell
   cd $HOME\whatsapp-mcp\whatsapp-bridge\store
   python -c "import sqlite3;print(sqlite3.connect('messages.db').execute('select count(*) from messages').fetchone())"
   ```

   Si da 0, el problema es la sincronización (esperá o revisá el bridge). Si da un número
   alto pero Claude no ve nada, el problema es la configuración del MCP.

### Problemas frecuentes

| Síntoma | Causa y solución |
|---|---|
| `cgo: C compiler "gcc" not found` | Falta el paso 3 (MSYS2 + PATH + `CGO_ENABLED=1`) |
| El server no aparece en Claude | JSON mal formado, o `uv` no está en el PATH → usá ruta absoluta a `uv.exe` |
| `Client outdated` / HTTP 405 al vincular | `whatsmeow` viejo. Es exactamente lo que pasa con el repo de `lharries`. `git pull` y recompilá |
| `401 Unauthorized` | Reiniciá el bridge (regenera `.bridge-token`) y después reiniciá Claude |
| `403 Forbidden for Host` | Usá `127.0.0.1` o `localhost` **con puerto** en `WHATSAPP_API_URL` |
| "Device Limit Reached" | WhatsApp permite 4 dispositivos enlazados. Sacá uno desde el teléfono |
| No cargan mensajes | La sincronización inicial tarda varios minutos con historial grande |
| Desincronizado / errores LTHash | Respaldá `store\`, mové **solo** `whatsapp.db` y re-escaneá el QR. **No borres `messages.db`** o perdés el archivo local |

### Mantenimiento

```powershell
cd $HOME\whatsapp-mcp
git pull
cd whatsapp-bridge
go build -o whatsapp-bridge.exe .
```

Actualizar **no** requiere re-escanear el QR: la sesión y el historial se conservan.
Reiniciá el bridge y Claude Desktop después de actualizar.

---

## 10. Para desconectar todo

1. Cerrá el bridge (Ctrl+C).
2. En el teléfono: **WhatsApp → Dispositivos vinculados** → cerrá la sesión del
   dispositivo.
3. Sacá el bloque `whatsapp` del `claude_desktop_config.json`.
4. Borrá la carpeta del repo — ahí adentro está toda la copia local de tus mensajes.

El paso 2 es el que realmente corta el acceso. Borrar los archivos sin desvincular deja
la sesión viva del lado de WhatsApp.
