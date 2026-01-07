# Script de PowerShell para instalar Python 3.11 automáticamente
# Ejecutar como: powershell -ExecutionPolicy Bypass -File instalar_python311.ps1

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     INSTALACIÓN AUTOMÁTICA DE PYTHON 3.11                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Configuración
$pythonVersion = "3.11.9"
$pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"
$installerPath = "$env:TEMP\python-$pythonVersion-amd64.exe"

Write-Host "[1/5] 📥 Descargando Python $pythonVersion..." -ForegroundColor Yellow
Write-Host ""

try {
    # Habilitar TLS 1.2
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    
    # Descargar con barra de progreso
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
    $ProgressPreference = 'Continue'
    
    Write-Host "✅ Python $pythonVersion descargado" -ForegroundColor Green
    Write-Host "   Ubicación: $installerPath" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "❌ Error al descargar Python" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Descarga manualmente desde:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/release/python-3119/" -ForegroundColor Cyan
    pause
    exit 1
}

Write-Host "[2/5] 📦 Instalando Python $pythonVersion..." -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  Instalación silenciosa en progreso..." -ForegroundColor Yellow
Write-Host "   - Se instalará en: C:\Program Files\Python311" -ForegroundColor Gray
Write-Host "   - Se agregará al PATH automáticamente" -ForegroundColor Gray
Write-Host ""

try {
    # Instalar Python silenciosamente
    $arguments = @(
        "/quiet",
        "InstallAllUsers=1",
        "PrependPath=1",
        "Include_test=0",
        "Include_doc=0",
        "Include_dev=0",
        "Include_pip=1",
        "Include_tcltk=0"
    )
    
    $process = Start-Process -FilePath $installerPath -ArgumentList $arguments -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "✅ Python $pythonVersion instalado correctamente" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "⚠️  Instalación completada con código: $($process.ExitCode)" -ForegroundColor Yellow
        Write-Host ""
    }
} catch {
    Write-Host "❌ Error durante la instalación" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "[3/5] 🔄 Actualizando variables de entorno..." -ForegroundColor Yellow
Write-Host ""

# Actualizar PATH en la sesión actual
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "✅ Variables actualizadas" -ForegroundColor Green
Write-Host ""

Write-Host "[4/5] 🔍 Verificando instalación..." -ForegroundColor Yellow
Write-Host ""

Start-Sleep -Seconds 2

try {
    $pythonPath = "C:\Program Files\Python311\python.exe"
    
    if (Test-Path $pythonPath) {
        $version = & $pythonPath --version 2>&1
        Write-Host "✅ Python instalado correctamente" -ForegroundColor Green
        Write-Host "   Versión: $version" -ForegroundColor Gray
        Write-Host "   Ruta: $pythonPath" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "⚠️  Python instalado pero no encontrado en la ruta esperada" -ForegroundColor Yellow
        Write-Host ""
    }
} catch {
    Write-Host "⚠️  No se pudo verificar la instalación" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "[5/5] 📦 Instalando dependencias del proyecto..." -ForegroundColor Yellow
Write-Host ""

try {
    # Cambiar al directorio del proyecto
    Set-Location "C:\trading\trading"
    
    Write-Host "   Actualizando pip..." -ForegroundColor Gray
    & "C:\Program Files\Python311\python.exe" -m pip install --upgrade pip --quiet
    
    Write-Host "   Instalando dependencias (esto puede tardar varios minutos)..." -ForegroundColor Gray
    & "C:\Program Files\Python311\python.exe" -m pip install -r requirements.txt --quiet
    
    Write-Host ""
    Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "⚠️  Error al instalar dependencias" -ForegroundColor Yellow
    Write-Host "   Instala manualmente con:" -ForegroundColor Gray
    Write-Host "   C:\Program Files\Python311\python.exe -m pip install -r requirements.txt" -ForegroundColor Cyan
    Write-Host ""
}

# Limpiar instalador
if (Test-Path $installerPath) {
    Remove-Item $installerPath -Force
}

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║          ✅ INSTALACIÓN COMPLETADA                        ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Próximos pasos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   1. Cierra esta ventana" -ForegroundColor White
Write-Host "   2. Abre una NUEVA terminal PowerShell" -ForegroundColor White
Write-Host "   3. Navega a: cd C:\trading\trading" -ForegroundColor White
Write-Host "   4. Compila el bot con Python 3.11:" -ForegroundColor White
Write-Host ""
Write-Host "      & 'C:\Program Files\Python311\python.exe' -m PyInstaller --version" -ForegroundColor Cyan
Write-Host "      & 'C:\Program Files\Python311\python.exe' -m pip install pyinstaller" -ForegroundColor Cyan
Write-Host "      .\COMPILAR_LIMPIO.bat" -ForegroundColor Cyan
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""

pause
