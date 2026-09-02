<#
.SYNOPSIS
    Diagnostica por que no cargan los plugins ni la biblioteca de texturas en SketchUp.
.DESCRIPTION
    Revisa las causas conocidas, en orden de probabilidad:
      1. Politica de carga de extensiones bloqueando plugins sin firmar
      2. Web cache corrupto (dialogos en blanco: texturas, warehouses)
      3. WebView2 / navegador embebido ausente o roto
      4. Plugins instalados en la carpeta equivocada
      5. Instalacion de SketchUp alterada (ejecutable sin firma de Trimble)
      6. Sin conectividad a los servidores de Trimble

    Solo lee y reporta. No modifica nada salvo que uses -RepararCache.
.USAGE
    Cerrar SketchUp. Abrir PowerShell y ejecutar:
        powershell -ExecutionPolicy Bypass -File .\diagnostico_sketchup.ps1

    Para borrar el web cache (soluciona los dialogos en blanco):
        powershell -ExecutionPolicy Bypass -File .\diagnostico_sketchup.ps1 -RepararCache

    Genera diagnostico_sketchup.md con todo el detalle.
#>

param(
    [switch]$RepararCache
)

$ErrorActionPreference = 'SilentlyContinue'
$out = Join-Path (Get-Location) 'diagnostico_sketchup.md'
$sb  = New-Object System.Text.StringBuilder

function L    { param([string]$t = '') [void]$sb.AppendLine($t) }
function Head { param($t) Write-Host "`n== $t" -ForegroundColor Cyan; L ''; L "## $t"; L '' }
function Ok   { param($t) Write-Host "   [OK]    $t" -ForegroundColor Green;  L "- **OK** — $t" }
function Warn { param($t) Write-Host "   [AVISO] $t" -ForegroundColor Yellow; L "- **AVISO** — $t" }
function Bad  { param($t) Write-Host "   [FALLA] $t" -ForegroundColor Red;    L "- **FALLA** — $t" }
function Info { param($t) Write-Host "           $t" -ForegroundColor Gray;   L "  - $t" }

$problemas = New-Object System.Collections.ArrayList

L "# Diagnostico de SketchUp"
L ''
L "Generado: $(Get-Date -Format 'yyyy-MM-dd HH:mm')  "
L "Equipo: $env:COMPUTERNAME — Usuario: $env:USERNAME"

# --- Detectar instalaciones ---------------------------------------------------

Head 'Instalaciones de SketchUp detectadas'

$appdata = Join-Path $env:APPDATA 'SketchUp'
$versiones = @()

if (Test-Path $appdata) {
    Get-ChildItem $appdata -Directory | Where-Object { $_.Name -match '^SketchUp (\d{4})$' } | ForEach-Object {
        $versiones += [pscustomobject]@{
            Anio    = $Matches[1]
            Perfil  = $_.FullName
            Plugins = Join-Path $_.FullName 'SketchUp\Plugins'
            Exe     = "C:\Program Files\SketchUp\SketchUp $($Matches[1])\SketchUp.exe"
        }
    }
}

if ($versiones.Count -eq 0) {
    Bad "No hay perfiles de SketchUp en $appdata. SketchUp no esta instalado o nunca se abrio."
    [void]$problemas.Add('No se detecto ninguna instalacion de SketchUp')
} else {
    foreach ($v in $versiones) { Ok "SketchUp $($v.Anio)" ; Info $v.Perfil }
}

if (Get-Process -Name 'SketchUp' -ErrorAction SilentlyContinue) {
    Warn 'SketchUp esta abierto ahora. Cerralo antes de reparar nada.'
}

# --- 1. Politica de carga de extensiones -------------------------------------

Head '1. Politica de carga de extensiones'

L 'SketchUp tiene tres modos. Si esta en *Identified Extensions Only*, NINGUN plugin'
L 'instalado por fuera del Extension Warehouse carga, porque quedan sin firma digital.'
L 'Es la causa numero uno de "no me anda ningun plugin".'
L ''

$policyEncontrada = $false
foreach ($v in $versiones) {
    $key = "HKCU:\Software\SketchUp\SketchUp $($v.Anio)"
    if (-not (Test-Path $key)) { continue }

    # El nombre exacto del valor cambia entre versiones: buscamos cualquiera que hable de policy/extension
    Get-ChildItem $key -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
        $props = Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
        foreach ($p in $props.PSObject.Properties) {
            if ($p.Name -match 'Policy|Signature|Signed|Extension') {
                Info "SketchUp $($v.Anio): $($_.PSChildName) > $($p.Name) = $($p.Value)"
                $script:policyEncontrada = $true
            }
        }
    }
}

if (-not $policyEncontrada) {
    Warn 'No se pudo leer la politica desde el registro (varia segun version).'
}
Warn 'REVISAR A MANO: Ventana > Extension Manager > engranaje (abajo a la derecha) > Loading Policy.'
Info 'Debe estar en "Unrestricted". Si dice "Identified Extensions Only", ese es el problema.'
Info 'Cambiarlo NO carga los plugins al instante: hay que cerrar y reabrir SketchUp.'
[void]$problemas.Add('Verificar Loading Policy en Extension Manager (ver arriba)')

# --- 2. Que hay realmente en la carpeta Plugins ------------------------------

Head '2. Contenido de la carpeta Plugins'

foreach ($v in $versiones) {
    L ''
    L "### SketchUp $($v.Anio)"
    L ''
    L '```'
    L $v.Plugins
    L '```'

    if (-not (Test-Path $v.Plugins)) {
        Bad "SketchUp $($v.Anio): la carpeta Plugins no existe."
        [void]$problemas.Add("Falta la carpeta Plugins de SketchUp $($v.Anio)")
        continue
    }

    $rb   = @(Get-ChildItem $v.Plugins -Filter '*.rb' -File)
    $dirs = @(Get-ChildItem $v.Plugins -Directory)

    if ($rb.Count -eq 0 -and $dirs.Count -eq 0) {
        Bad "SketchUp $($v.Anio): la carpeta Plugins esta VACIA. No hay nada instalado ahi."
        [void]$problemas.Add("Plugins vacia en SketchUp $($v.Anio)")
    } else {
        Ok "SketchUp $($v.Anio): $($rb.Count) archivos .rb y $($dirs.Count) carpetas"
        L ''
        L '| Archivo / carpeta | Tipo |'
        L '|---|---|'
        $rb   | ForEach-Object { L "| $($_.Name) | .rb (cargador) |" }
        $dirs | ForEach-Object { L "| $($_.Name) | carpeta |" }
        L ''
        L 'Un plugin bien instalado necesita AMBAS cosas: un `.rb` suelto y su carpeta'
        L 'del mismo nombre. Si ves carpetas sin su `.rb`, la instalacion quedo incompleta.'

        $huerfanas = $dirs | Where-Object { $n = $_.Name; -not ($rb | Where-Object { $_.BaseName -eq $n }) }
        if ($huerfanas) {
            Warn "SketchUp $($v.Anio): carpetas sin su .rb correspondiente (instalacion incompleta):"
            $huerfanas | ForEach-Object { Info $_.Name }
            [void]$problemas.Add("Instalaciones incompletas en SketchUp $($v.Anio)")
        }
    }
}

# --- 3. Web cache (dialogos en blanco / texturas) ----------------------------

Head '3. Web cache — causa de los dialogos en blanco'

L 'La biblioteca de texturas, el 3D Warehouse y el Extension Warehouse se dibujan con'
L 'un navegador embebido. Si su cache se corrompe, esas ventanas salen en blanco'
L 'aunque SketchUp funcione normal. La solucion es borrar la carpeta de cache:'
L 'se regenera sola al reabrir.'
L ''

$caches = @()
foreach ($v in $versiones) {
    Get-ChildItem $v.Perfil -Directory -Recurse -Depth 2 -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match 'cache' } | ForEach-Object { $caches += $_ }
}

if ($caches.Count -eq 0) {
    Info 'No se encontraron carpetas de cache (puede ser normal si nunca se abrieron esas ventanas).'
} else {
    foreach ($c in $caches) {
        $mb = [math]::Round((Get-ChildItem $c.FullName -Recurse -File -ErrorAction SilentlyContinue |
                             Measure-Object Length -Sum).Sum / 1MB, 1)
        Info "$($c.FullName)  ($mb MB)"
    }

    if ($RepararCache) {
        if (Get-Process -Name 'SketchUp' -ErrorAction SilentlyContinue) {
            Bad 'No se borra el cache: SketchUp esta abierto. Cerralo y volve a ejecutar.'
        } else {
            foreach ($c in $caches) {
                $bak = "$($c.FullName).bak-$(Get-Date -Format 'yyyyMMddHHmmss')"
                Rename-Item $c.FullName $bak -ErrorAction SilentlyContinue
                if ($?) { Ok "Cache renombrado a $bak (podes borrarlo si todo anda bien)" }
                else    { Bad "No se pudo renombrar $($c.FullName)" }
            }
        }
    } else {
        Warn 'Para borrar el cache volve a correr el script con  -RepararCache'
        [void]$problemas.Add('Probar borrar el web cache con -RepararCache')
    }
}

# --- 4. WebView2 / navegador embebido ----------------------------------------

Head '4. Microsoft Edge WebView2 Runtime'

L 'SketchUp usa WebView2 para varios paneles. Si falta o esta roto, esos paneles'
L 'quedan en blanco.'
L ''

$wvGuid  = '{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}'
$wvPaths = @(
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\$wvGuid",
    "HKLM:\SOFTWARE\Microsoft\EdgeUpdate\Clients\$wvGuid",
    "HKCU:\SOFTWARE\Microsoft\EdgeUpdate\Clients\$wvGuid"
)
$wvVer = $null
foreach ($p in $wvPaths) {
    $val = (Get-ItemProperty $p -ErrorAction SilentlyContinue).pv
    if ($val) { $wvVer = $val; break }
}
if (-not $wvVer) {
    $d = Get-ChildItem 'C:\Program Files (x86)\Microsoft\EdgeWebView\Application' -Directory -ErrorAction SilentlyContinue |
         Sort-Object Name -Descending | Select-Object -First 1
    if ($d) { $wvVer = $d.Name }
}

if ($wvVer) {
    Ok "WebView2 Runtime instalado — version $wvVer"
} else {
    Bad 'WebView2 Runtime NO detectado. Descargalo (Evergreen Standalone Installer) desde:'
    Info 'https://developer.microsoft.com/microsoft-edge/webview2/'
    [void]$problemas.Add('Instalar Microsoft Edge WebView2 Runtime')
}

$edge = (Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Microsoft Edge' -ErrorAction SilentlyContinue).DisplayVersion
if ($edge) { Ok "Microsoft Edge $edge" } else { Warn 'Microsoft Edge no detectado.' }

# --- 5. Integridad de la instalacion -----------------------------------------

Head '5. Integridad de la instalacion de SketchUp'

L 'Si el ejecutable no tiene la firma digital de Trimble, la instalacion fue modificada.'
L 'Las versiones parcheadas suelen romper justo esto: warehouses, login y paneles web.'
L ''

foreach ($v in $versiones) {
    if (-not (Test-Path $v.Exe)) {
        Warn "SketchUp $($v.Anio): no se encontro SketchUp.exe en la ruta estandar."
        Info $v.Exe
        continue
    }
    $sig  = Get-AuthenticodeSignature $v.Exe
    $firm = $sig.SignerCertificate.Subject
    $info = (Get-Item $v.Exe).VersionInfo

    if ($sig.Status -eq 'Valid' -and $firm -match 'Trimble') {
        Ok "SketchUp $($v.Anio): firma valida de Trimble — build $($info.ProductVersion)"
    } else {
        Bad "SketchUp $($v.Anio): firma $($sig.Status). Instalacion posiblemente alterada."
        Info "Firmante: $firm"
        Info "Build: $($info.ProductVersion)"
        [void]$problemas.Add("SketchUp $($v.Anio) sin firma valida de Trimble")
    }
}

# --- 6. Conectividad ---------------------------------------------------------

Head '6. Conectividad con los servidores de Trimble'

foreach ($h in @('extensions.sketchup.com', '3dwarehouse.sketchup.com', 'accounts.trimble.com')) {
    $r = Test-NetConnection -ComputerName $h -Port 443 -WarningAction SilentlyContinue
    if ($r.TcpTestSucceeded) { Ok "$h alcanzable (443)" }
    else {
        Bad "$h NO responde. Puede ser firewall, antivirus o proxy."
        [void]$problemas.Add("Sin conexion a $h")
    }
}

$av = Get-CimInstance -Namespace 'root\SecurityCenter2' -ClassName AntiVirusProduct -ErrorAction SilentlyContinue
if ($av) { $av | ForEach-Object { Info "Antivirus activo: $($_.displayName)" } }
L ''
L 'Si el antivirus es de terceros, agrega una exclusion para la carpeta Plugins:'
L 'muchos bloquean archivos `.rb` por ser scripts.'

# --- Resumen -----------------------------------------------------------------

Head 'Resumen'

if ($problemas.Count -eq 0) {
    Ok 'No se detectaron problemas evidentes.'
} else {
    Write-Host ''
    L 'Puntos a revisar, en orden:'
    L ''
    $i = 1
    foreach ($p in $problemas) {
        Write-Host "   $i. $p" -ForegroundColor Yellow
        L "$i. $p"
        $i++
    }
}

L ''
L '---'
L ''
L '## Orden recomendado para resolverlo'
L ''
L '1. **Loading Policy en Unrestricted** (Extension Manager > engranaje) y reiniciar SketchUp.'
L '2. **Borrar el web cache**: correr este script con `-RepararCache`.'
L '3. **Instalar WebView2** si el punto 4 dio FALLA.'
L '4. **Ruby Console** (Ventana > Ruby Console): abrila al arrancar SketchUp y copiame'
L '   los errores en rojo que aparezcan. Ahi se ve exactamente que plugin falla y por que.'
L '5. Si el ejecutable no tiene firma de Trimble, reinstalar SketchUp desde el instalador oficial.'

Set-Content -Path $out -Value $sb.ToString() -Encoding UTF8
Write-Host "`nReporte guardado en: $out`n" -ForegroundColor Cyan
Write-Host "Pasame ese archivo y te digo exactamente que corregir.`n" -ForegroundColor Cyan
