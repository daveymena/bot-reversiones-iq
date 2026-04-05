# Script de limpieza para preparar el bot para Git y EasyPanel
# Este script elimina archivos temporales, de prueba y de configuración innecesarios

Write-Host "🧹 INICIANDO LIMPIEZA DEL REPOSITORIO..." -ForegroundColor Cyan
Write-Host ""

# Función para eliminar archivos con confirmación
function Remove-FilesPattern {
    param(
        [string]$Pattern,
        [string]$Description
    )
    
    $files = Get-ChildItem -Path . -Filter $Pattern -File -Recurse -ErrorAction SilentlyContinue
    if ($files.Count -gt 0) {
        Write-Host "❌ Eliminando $Description ($($files.Count) archivos)..." -ForegroundColor Yellow
        $files | Remove-Item -Force
        Write-Host "✅ Eliminados $($files.Count) archivos de $Description" -ForegroundColor Green
    }
}

# Fase 1: Eliminar archivos de prueba
Write-Host "📋 FASE 1: Eliminando archivos de prueba..." -ForegroundColor Cyan
Remove-FilesPattern "test_*.py" "pruebas"
Remove-FilesPattern "demo_*.py" "demos"
Remove-FilesPattern "diagnostico_*.py" "diagnósticos"
Remove-FilesPattern "analyze_*.py" "análisis"
Remove-FilesPattern "bot_*.py" "bots de prueba"
Remove-FilesPattern "run_*.py" "scripts de ejecución"
Remove-FilesPattern "fix_*.py" "scripts de corrección"
Remove-FilesPattern "debug_*.py" "scripts de debug"
Remove-FilesPattern "check_*.py" "scripts de verificación"
Remove-FilesPattern "optimize_*.py" "scripts de optimización"

# Fase 2: Eliminar archivos .bat de Windows
Write-Host ""
Write-Host "📋 FASE 2: Eliminando scripts .bat de Windows..." -ForegroundColor Cyan
$batFiles = Get-ChildItem -Path . -Filter "*.bat" -File -Recurse -ErrorAction SilentlyContinue
if ($batFiles.Count -gt 0) {
    Write-Host "❌ Eliminando scripts .bat ($($batFiles.Count) archivos)..." -ForegroundColor Yellow
    $batFiles | Remove-Item -Force
    Write-Host "✅ Eliminados $($batFiles.Count) archivos .bat" -ForegroundColor Green
}

# Fase 3: Eliminar archivos de análisis temporal en data/
Write-Host ""
Write-Host "📋 FASE 3: Limpiando archivos temporales en data/..." -ForegroundColor Cyan
Remove-FilesPattern "data/deep_analysis_*.json" "análisis temporal"
Remove-FilesPattern "data/market_profiles.json" "perfiles de mercado"
Remove-FilesPattern "data/meta_analysis.json" "análisis meta"
Remove-FilesPattern "data/meta_rules.json" "reglas meta"
Remove-FilesPattern "data/eurusd_precision_study.json" "estudios de precisión"
Remove-FilesPattern "data/bot_running.flag" "flags de ejecución"

# Fase 4: Eliminar archivos de instalación
Write-Host ""
Write-Host "📋 FASE 4: Eliminando archivos de instalación..." -ForegroundColor Cyan
Remove-FilesPattern "installer_*.iss" "scripts Inno Setup"
Remove-FilesPattern "build_installer_*.bat" "build scripts"
Remove-FilesPattern "CREAR_EJECUTABLE_*.bat" "creación de ejecutables"
Remove-FilesPattern "INSTALAR_*.bat" "scripts de instalación"

# Fase 5: Eliminar backups innecesarios
Write-Host ""
Write-Host "📋 FASE 5: Limpiando backups innecesarios..." -ForegroundColor Cyan
Remove-FilesPattern "core/trader.py.backup" "backups de trader"
Remove-FilesPattern "*.log" "archivos de log antiguos"

# Fase 6: Eliminar archivos de salida
Write-Host ""
Write-Host "📋 FASE 6: Eliminando archivos de salida..." -ForegroundColor Cyan
Remove-FilesPattern "analysis_output.txt" "salida de análisis"
Remove-FilesPattern "output_*.txt" "archivos de salida"

Write-Host ""
Write-Host "✅ LIMPIEZA COMPLETADA" -ForegroundColor Green
Write-Host ""
Write-Host "📊 RESUMEN:" -ForegroundColor Cyan
Write-Host "  ✓ Archivos de prueba eliminados"
Write-Host "  ✓ Scripts .bat eliminados"
Write-Host "  ✓ Archivos temporales eliminados"
Write-Host "  ✓ Archivos de instalación eliminados"
Write-Host "  ✓ Backups innecesarios eliminados"
Write-Host ""
Write-Host "🚀 El repositorio está listo para Git y EasyPanel" -ForegroundColor Green
