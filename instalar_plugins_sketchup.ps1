<#
.SYNOPSIS
    Descarga e instala plugins gratuitos y open source de SketchUp para arquitectura.
.DESCRIPTION
    Busca la carpeta Plugins de cada version de SketchUp instalada en la PC,
    baja el .rbz mas reciente de cada repositorio de GitHub y lo extrae ahi.
    Un archivo .rbz es un ZIP, asi que extraerlo en Plugins es exactamente lo
    mismo que hace el instalador de SketchUp.

    Solo instala plugins de descarga libre y directa. Los que requieren cuenta
    (Extension Warehouse, SketchUcation) o son pagos NO se pueden automatizar:
    al final el script lista cuales quedan pendientes de instalar a mano.
.USAGE
    Cerrar SketchUp primero. Despues abrir PowerShell y ejecutar:
        powershell -ExecutionPolicy Bypass -File .\instalar_plugins_sketchup.ps1

    Opciones:
        -Listar          Solo muestra que haria, sin instalar nada
        -Version 2024    Instala solo en esa version de SketchUp
#>

param(
    [switch]$Listar,
    [string]$Version
)

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Plugins con descarga directa desde GitHub Releases
$repos = @(
    @{ Nombre = 'TT_Lib2 (libreria base de ThomThom)'; Repo = 'thomthom/tt-library-2' },
    @{ Nombre = 'CleanUp3 - limpieza y optimizacion';  Repo = 'thomthom/cleanup' },
    @{ Nombre = 'Solid Inspector2 - reparar solidos';  Repo = 'thomthom/solid-inspector' },
    @{ Nombre = 'QuadFace Tools - topologia quads';    Repo = 'thomthom/quadface-tools' },
    @{ Nombre = 'SketchUp STL - import/export STL';    Repo = 'SketchUp/sketchup-stl' },
    @{ Nombre = 'Universal Importer - importar 3D';    Repo = 'SamuelTS/SketchUp-Universal-Importer-Plugin' },
    @{ Nombre = 'OpenCutList - despiece y computo';    Repo = 'lairdubois/lairdubois-opencutlist-sketchup-extension' }
)

# Los que hay que instalar a mano (requieren login o son pagos)
$manuales = @(
    @{ Nombre = 'LibFredo6 (base de todo Fredo6)'; Donde = 'https://sketchucation.com/plugin/903-libfredo6'; Costo = 'Gratis' },
    @{ Nombre = '1001bit Tools (Freeware)';        Donde = 'https://extensions.sketchup.com/extension/e5b1211a-8d1a-4813-bdc3-b321e5477d7b/1001bit-tools-freeware'; Costo = 'Gratis' },
    @{ Nombre = 'FredoTools';                      Donde = 'https://sketchucation.com/pluginstore?pauthor=fredo6'; Costo = 'Gratis' },
    @{ Nombre = 'Selection Toys';                  Donde = 'https://extensions.sketchup.com/'; Costo = 'Gratis' },
    @{ Nombre = 'Eneroth (varios)';                Donde = 'https://extensions.sketchup.com/developer/43f599f6-ce20-47db-bf57-a86f98a6792f'; Costo = 'Gratis' },
    @{ Nombre = 'Bundle Fredo6 (8 plugins)';       Donde = 'https://sketchucation.com/pluginstore?pauthor=fredo6'; Costo = 'USD 40 perpetuo' },
    @{ Nombre = 'D5 Render Community';             Donde = 'https://www.d5render.com/'; Costo = 'Gratis' }
)

function Write-Paso { param($t) Write-Host "`n>> $t" -ForegroundColor Cyan }
function Write-Ok   { param($t) Write-Host "   [OK]   $t" -ForegroundColor Green }
function Write-Skip { param($t) Write-Host "   [SALTA] $t" -ForegroundColor Yellow }
function Write-Err  { param($t) Write-Host "   [ERROR] $t" -ForegroundColor Red }

# --- 1. Ubicar las carpetas Plugins de SketchUp -----------------------------

Write-Paso 'Buscando instalaciones de SketchUp'

$base = Join-Path $env:APPDATA 'SketchUp'
if (-not (Test-Path $base)) {
    Write-Err "No existe $base. SketchUp no esta instalado o nunca se abrio."
    exit 1
}

$destinos = @()
Get-ChildItem $base -Directory | Where-Object { $_.Name -match '^SketchUp (\d{4})$' } | ForEach-Object {
    $anio = $Matches[1]
    if ($Version -and $anio -ne $Version) { return }
    $p = Join-Path $_.FullName 'SketchUp\Plugins'
    if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
    $destinos += [pscustomobject]@{ Anio = $anio; Ruta = $p }
}

if ($destinos.Count -eq 0) {
    Write-Err 'No se encontro ninguna carpeta de plugins de SketchUp.'
    exit 1
}
foreach ($d in $destinos) { Write-Ok "SketchUp $($d.Anio) -> $($d.Ruta)" }

# Avisar si SketchUp esta abierto: los archivos quedarian bloqueados
if (Get-Process -Name 'SketchUp' -ErrorAction SilentlyContinue) {
    Write-Err 'SketchUp esta abierto. Cerralo y volve a ejecutar el script.'
    exit 1
}

# --- 2. Descargar e instalar -------------------------------------------------

$tmp = Join-Path $env:TEMP ('su-plugins-' + (Get-Date -Format 'yyyyMMddHHmmss'))
New-Item -ItemType Directory -Path $tmp -Force | Out-Null

$instalados = @()
$fallidos   = @()

foreach ($p in $repos) {
    Write-Paso $p.Nombre

    try {
        $api = "https://api.github.com/repos/$($p.Repo)/releases/latest"
        $rel = Invoke-RestMethod -Uri $api -Headers @{ 'User-Agent' = 'PowerShell' } -TimeoutSec 30

        $asset = $rel.assets | Where-Object { $_.name -like '*.rbz' } | Select-Object -First 1
        if (-not $asset) {
            Write-Skip "La release $($rel.tag_name) no publica un .rbz. Instalalo a mano desde https://github.com/$($p.Repo)/releases"
            $fallidos += "$($p.Nombre) -> https://github.com/$($p.Repo)/releases"
            continue
        }

        Write-Host "   Version $($rel.tag_name) - $($asset.name)"
        if ($Listar) { continue }

        $rbz = Join-Path $tmp $asset.name
        Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $rbz -TimeoutSec 300

        # Un .rbz es un ZIP: se extrae directo en Plugins
        $zip = [IO.Path]::ChangeExtension($rbz, '.zip')
        Move-Item $rbz $zip -Force

        foreach ($d in $destinos) {
            Expand-Archive -Path $zip -DestinationPath $d.Ruta -Force
            Write-Ok "Instalado en SketchUp $($d.Anio)"
        }
        $instalados += "$($p.Nombre) ($($rel.tag_name))"
    }
    catch {
        Write-Err $_.Exception.Message
        $fallidos += "$($p.Nombre) -> https://github.com/$($p.Repo)/releases"
    }
}

Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue

# --- 3. Resumen --------------------------------------------------------------

Write-Host "`n============================================================" -ForegroundColor White
Write-Host ' RESUMEN' -ForegroundColor White
Write-Host '============================================================' -ForegroundColor White

if ($instalados.Count -gt 0) {
    Write-Host "`nInstalados automaticamente:" -ForegroundColor Green
    $instalados | ForEach-Object { Write-Host "  - $_" }
}

if ($fallidos.Count -gt 0) {
    Write-Host "`nNo se pudieron instalar solos (bajalos a mano):" -ForegroundColor Yellow
    $fallidos | ForEach-Object { Write-Host "  - $_" }
}

Write-Host "`nPendientes de instalar a mano (requieren cuenta o son pagos):" -ForegroundColor Yellow
foreach ($m in $manuales) {
    Write-Host ("  - {0,-32} [{1}]" -f $m.Nombre, $m.Costo)
    Write-Host "      $($m.Donde)" -ForegroundColor DarkGray
}

Write-Host "`nAbri SketchUp y revisa Ventana > Extension Manager para confirmar." -ForegroundColor Cyan
Write-Host "Para instalar un .rbz a mano: Ventana > Preferencias > Extensiones > Instalar extension`n"
