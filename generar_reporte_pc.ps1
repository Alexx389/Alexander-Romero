<#
.SYNOPSIS
    Genera un reporte completo del PC (reporte_pc.md) usando WMI/CIM/PowerShell.
.DESCRIPTION
    Recolecta hardware, software instalado y estado del sistema en Windows 10/11.
    No inventa datos: todo sale de consultas reales al sistema. Si algun dato no
    esta disponible (ej. temperaturas), lo indica explicitamente.
.USAGE
    Abrir PowerShell y ejecutar:
        powershell -ExecutionPolicy Bypass -File .\generar_reporte_pc.ps1
    (Ejecutar como Administrador para obtener mas datos: temperaturas, algunos discos)
#>

$ErrorActionPreference = 'SilentlyContinue'
$out    = Join-Path (Get-Location) 'reporte_pc.md'
$fecha  = Get-Date -Format 'yyyy-MM-dd HH:mm'
$sb     = New-Object System.Text.StringBuilder

function Add-Line { param([string]$t = '') [void]$sb.AppendLine($t) }
function Bytes-GB { param([double]$b) if ($b) { [math]::Round($b / 1GB, 2) } else { 0 } }

# Detectar privilegios de admin
$esAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

Add-Line "# Reporte de PC"
Add-Line ""
Add-Line "> Generado el **$fecha** en **$env:COMPUTERNAME** por el usuario **$env:USERNAME**."
if (-not $esAdmin) {
    Add-Line ">"
    Add-Line "> _Nota: el script NO se ejecuto como Administrador. Algunos datos (temperaturas, ciertos discos) pueden faltar._"
}
Add-Line ""

# ==========================================================================
# SISTEMA OPERATIVO
# ==========================================================================
$os  = Get-CimInstance Win32_OperatingSystem
$cs  = Get-CimInstance Win32_ComputerSystem

Add-Line "## Sistema operativo"
Add-Line ""
Add-Line "| Dato | Valor |"
Add-Line "|------|-------|"
Add-Line "| Edicion | $($os.Caption) |"
Add-Line "| Version | $($os.Version) (build $($os.BuildNumber)) |"
Add-Line "| Arquitectura | $($os.OSArchitecture) |"
Add-Line "| Instalado el | $($os.InstallDate) |"
Add-Line "| Ultimo arranque | $($os.LastBootUpTime) |"
Add-Line "| Fabricante equipo | $($cs.Manufacturer) |"
Add-Line "| Modelo equipo | $($cs.Model) |"
Add-Line ""

# ==========================================================================
# 1. HARDWARE
# ==========================================================================
Add-Line "## 1. Hardware"
Add-Line ""

# ---- CPU ----
Add-Line "### CPU"
Add-Line ""
Add-Line "| Modelo | Nucleos | Hilos | Frec. base (MHz) | Frec. max (MHz) | Socket |"
Add-Line "|--------|---------|-------|------------------|-----------------|--------|"
Get-CimInstance Win32_Processor | ForEach-Object {
    Add-Line "| $($_.Name.Trim()) | $($_.NumberOfCores) | $($_.NumberOfLogicalProcessors) | $($_.CurrentClockSpeed) | $($_.MaxClockSpeed) | $($_.SocketDesignation) |"
}
Add-Line ""

# ---- RAM ----
Add-Line "### Memoria RAM"
Add-Line ""
$ramTotalGB = Bytes-GB $cs.TotalPhysicalMemory
$memArray   = Get-CimInstance Win32_PhysicalMemoryArray | Select-Object -First 1
$slotsTot   = $memArray.MemoryDevices
$modulos    = Get-CimInstance Win32_PhysicalMemory
$slotsUsados = ($modulos | Measure-Object).Count

Add-Line "- **Total instalada:** $ramTotalGB GB"
Add-Line "- **Slots:** $slotsUsados usados de $slotsTot totales"
Add-Line ""
Add-Line "| Slot | Capacidad (GB) | Velocidad (MHz) | Tipo | Fabricante | Part Number |"
Add-Line "|------|----------------|-----------------|------|------------|-------------|"
$tipoMem = @{20='DDR';21='DDR2';24='DDR3';26='DDR4';34='DDR5';0='Desconocido'}
foreach ($m in $modulos) {
    $t = $tipoMem[[int]$m.SMBIOSMemoryType]; if (-not $t) { $t = "Cod:$($m.SMBIOSMemoryType)" }
    Add-Line "| $($m.DeviceLocator) | $(Bytes-GB $m.Capacity) | $($m.Speed) | $t | $($m.Manufacturer) | $($m.PartNumber.Trim()) |"
}
Add-Line ""

# ---- GPU ----
Add-Line "### GPU"
Add-Line ""
Add-Line "| Modelo | VRAM (GB) | Version driver | Fecha driver | Resolucion |"
Add-Line "|--------|-----------|----------------|--------------|------------|"
$gpus = Get-CimInstance Win32_VideoController
foreach ($g in $gpus) {
    # AdapterRAM es uint32 (tope 4GB). Intentar leer VRAM real del registro.
    $vram = Bytes-GB $g.AdapterRAM
    $regBase = 'HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}'
    Get-ChildItem $regBase 2>$null | ForEach-Object {
        $p = Get-ItemProperty $_.PSPath 2>$null
        if ($p.'HardwareInformation.qwMemorySize' -and $p.DriverDesc -eq $g.Name) {
            $vram = Bytes-GB ([int64]$p.'HardwareInformation.qwMemorySize')
        }
    }
    $fecha = if ($g.DriverDate) { ([datetime]$g.DriverDate).ToString('yyyy-MM-dd') } else { 'N/D' }
    Add-Line "| $($g.Name) | $vram | $($g.DriverVersion) | $fecha | $($g.CurrentHorizontalResolution)x$($g.CurrentVerticalResolution) |"
}
Add-Line ""

# CUDA / RTX / nvidia-smi
$nvidia = $gpus | Where-Object { $_.Name -match 'NVIDIA|RTX|GTX|Quadro' }
if ($nvidia) {
    Add-Line "**GPU NVIDIA detectada** -> soporta CUDA."
    if ($nvidia.Name -match 'RTX') { Add-Line "- Serie **RTX**: soporta ray tracing por hardware (RTX) y DLSS." }
    $smi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if ($smi) {
        Add-Line ""
        Add-Line '```'
        try { & nvidia-smi --query-gpu=name,memory.total,driver_version,temperature.gpu --format=csv 2>&1 | ForEach-Object { Add-Line $_ } } catch {}
        Add-Line '```'
    }
    Add-Line ""
} elseif ($gpus | Where-Object { $_.Name -match 'AMD|Radeon' }) {
    Add-Line "**GPU AMD/Radeon detectada** -> soporta OpenCL/ROCm (no CUDA)."
    Add-Line ""
}

# ---- DISCOS ----
Add-Line "### Discos fisicos"
Add-Line ""
Add-Line "| Modelo | Tipo | Bus | Capacidad (GB) | Estado |"
Add-Line "|--------|------|-----|----------------|--------|"
$pdisks = Get-PhysicalDisk
if ($pdisks) {
    foreach ($d in $pdisks) {
        Add-Line "| $($d.FriendlyName) | $($d.MediaType) | $($d.BusType) | $([math]::Round($d.Size/1GB,2)) | $($d.HealthStatus) |"
    }
} else {
    # Fallback si Get-PhysicalDisk no esta disponible
    Get-CimInstance Win32_DiskDrive | ForEach-Object {
        Add-Line "| $($_.Model) | N/D | $($_.InterfaceType) | $([math]::Round($_.Size/1GB,2)) | $($_.Status) |"
    }
}
Add-Line ""

Add-Line "### Volumenes / particiones (espacio libre)"
Add-Line ""
Add-Line "| Unidad | Etiqueta | Sistema archivos | Total (GB) | Libre (GB) | % Libre |"
Add-Line "|--------|----------|------------------|------------|------------|---------|"
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
    $tot = Bytes-GB $_.Size
    $lib = Bytes-GB $_.FreeSpace
    $pct = if ($_.Size) { [math]::Round(($_.FreeSpace / $_.Size) * 100, 1) } else { 0 }
    Add-Line "| $($_.DeviceID) | $($_.VolumeName) | $($_.FileSystem) | $tot | $lib | $pct% |"
}
Add-Line ""

# ---- PLACA BASE / BIOS ----
$bb   = Get-CimInstance Win32_BaseBoard
$bios = Get-CimInstance Win32_BIOS
Add-Line "### Placa base y BIOS"
Add-Line ""
Add-Line "| Dato | Valor |"
Add-Line "|------|-------|"
Add-Line "| Placa base | $($bb.Manufacturer) $($bb.Product) |"
Add-Line "| Version placa | $($bb.Version) |"
Add-Line "| BIOS fabricante | $($bios.Manufacturer) |"
Add-Line "| BIOS version | $($bios.SMBIOSBIOSVersion) |"
Add-Line "| BIOS fecha | $($bios.ReleaseDate) |"
Add-Line ""

# ==========================================================================
# 2. SOFTWARE INSTALADO
# ==========================================================================
Add-Line "## 2. Software instalado"
Add-Line ""

$regPaths = @(
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
)
$apps = foreach ($p in $regPaths) {
    Get-ItemProperty $p 2>$null | Where-Object { $_.DisplayName } |
        Select-Object DisplayName, DisplayVersion, Publisher
}
$apps = $apps | Sort-Object DisplayName -Unique

# Software de arquitectura / diseno / render destacado
$patrones = 'AutoCAD|SketchUp|D5|Revit|Photoshop|Lumion|Twinmotion|3ds Max|3dsMax|Blender|Rhino|Rhinoceros|V-Ray|VRay|Corona|Enscape|ArchiCAD|Cinema 4D|Maya|Illustrator|InDesign|Vectorworks|Chief Architect|Substance|ZBrush|Keyshot|Unreal|Unity|Civil 3D|Navisworks|Fusion 360|SolidWorks|Inventor|Nuke|After Effects|DaVinci|Marmoset'
$destacados = $apps | Where-Object { $_.DisplayName -match $patrones }

if ($destacados) {
    Add-Line "### Software de arquitectura / diseno / render detectado"
    Add-Line ""
    Add-Line "| Programa | Version | Editor |"
    Add-Line "|----------|---------|--------|"
    foreach ($a in $destacados) {
        Add-Line "| **$($a.DisplayName)** | $($a.DisplayVersion) | $($a.Publisher) |"
    }
    Add-Line ""
} else {
    Add-Line "### Software de arquitectura / diseno / render detectado"
    Add-Line ""
    Add-Line "_No se detectaron programas de arquitectura/render conocidos en la lista de instalados._"
    Add-Line ""
}

Add-Line "### Todos los programas instalados ($($apps.Count))"
Add-Line ""
Add-Line "| Programa | Version | Editor |"
Add-Line "|----------|---------|--------|"
foreach ($a in $apps) {
    Add-Line "| $($a.DisplayName) | $($a.DisplayVersion) | $($a.Publisher) |"
}
Add-Line ""

# ==========================================================================
# 3. ESTADO DEL SISTEMA
# ==========================================================================
Add-Line "## 3. Estado del sistema"
Add-Line ""

# RAM en uso
$totKB  = $os.TotalVisibleMemorySize
$freeKB = $os.FreePhysicalMemory
$usoKB  = $totKB - $freeKB
$usoPct = if ($totKB) { [math]::Round(($usoKB / $totKB) * 100, 1) } else { 0 }
Add-Line "### Uso de memoria RAM"
Add-Line ""
Add-Line "- **Total:** $([math]::Round($totKB/1MB,2)) GB"
Add-Line "- **En uso:** $([math]::Round($usoKB/1MB,2)) GB ($usoPct%)"
Add-Line "- **Libre:** $([math]::Round($freeKB/1MB,2)) GB"
Add-Line ""

# Uso de disco (resumen)
Add-Line "### Uso de disco"
Add-Line ""
Add-Line "| Unidad | Usado (GB) | Libre (GB) | % Usado |"
Add-Line "|--------|------------|------------|---------|"
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
    $usado = Bytes-GB ($_.Size - $_.FreeSpace)
    $libre = Bytes-GB $_.FreeSpace
    $pctU  = if ($_.Size) { [math]::Round((($_.Size - $_.FreeSpace) / $_.Size) * 100, 1) } else { 0 }
    Add-Line "| $($_.DeviceID) | $usado | $libre | $pctU% |"
}
Add-Line ""

# Temperaturas
Add-Line "### Temperaturas"
Add-Line ""
$tempOK = $false

# CPU via WMI ACPI thermal zone (requiere admin, no siempre disponible)
$tz = Get-CimInstance -Namespace 'root/wmi' -ClassName MSAcpi_ThermalZoneTemperature 2>$null
if ($tz) {
    foreach ($z in $tz) {
        $c = [math]::Round(($z.CurrentTemperature / 10) - 273.15, 1)
        Add-Line "- **Zona termica ($($z.InstanceName)):** $c C"
        $tempOK = $true
    }
}

# GPU NVIDIA via nvidia-smi
if ($nvidia -and (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
    $gpuTemp = & nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader 2>$null
    if ($gpuTemp) { Add-Line "- **GPU NVIDIA:** $gpuTemp C"; $tempOK = $true }
}

if (-not $tempOK) {
    Add-Line "_No se pudo leer temperatura por WMI/nvidia-smi. Windows rara vez la expone sin drivers/admin._"
    Add-Line ""
    Add-Line "> Para temperaturas confiables usar herramientas dedicadas: **HWiNFO**, **HWMonitor** o **Open Hardware Monitor**."
}
Add-Line ""

Add-Line "---"
Add-Line "_Reporte generado automaticamente. Datos obtenidos via WMI/CIM/PowerShell._"

# Guardar
$sb.ToString() | Out-File -FilePath $out -Encoding UTF8
Write-Host "Reporte generado en: $out" -ForegroundColor Green
