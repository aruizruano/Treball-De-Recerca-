# limpiar_carpeta.ps1  (v2 - corregido)
# Borra lo que ya has confirmado:
#   - __pycache__ y .pyc  -> copia automática que Python genera solo,
#     se regenera sola, sin riesgo borrarla.
#   - Los scripts sueltos que NO hacen falta para ejecutar app.py ni
#     app_streamlit.py.
#
# NO toca: ningún .csv, .png, .pdf, ni rubrica.txt, ni nada que las
# dos webs necesiten para funcionar.
#
# Uso: desde PowerShell, dentro de la carpeta del proyecto:
#   powershell -ExecutionPolicy Bypass -File .\limpiar_carpeta.ps1

Write-Host "=== Buscando carpetas __pycache__ ===" -ForegroundColor Cyan
$pycaches = Get-ChildItem -Path . -Directory -Recurse -Force -Filter "__pycache__"
if ($pycaches.Count -eq 0) {
    Write-Host "  No se ha encontrado ninguna carpeta __pycache__."
} else {
    foreach ($carpeta in $pycaches) {
        try {
            Remove-Item -LiteralPath $carpeta.FullName -Recurse -Force -ErrorAction Stop
            Write-Host "  Borrada: $($carpeta.FullName)" -ForegroundColor Green
        } catch {
            Write-Host "  NO se pudo borrar $($carpeta.FullName) -> $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host "`n=== Buscando archivos .pyc ===" -ForegroundColor Cyan
$pycs = Get-ChildItem -Path . -File -Recurse -Force -Filter "*.pyc"
if ($pycs.Count -eq 0) {
    Write-Host "  No se ha encontrado ningún .pyc."
} else {
    foreach ($archivo in $pycs) {
        try {
            Remove-Item -LiteralPath $archivo.FullName -Force -ErrorAction Stop
            Write-Host "  Borrado: $($archivo.FullName)" -ForegroundColor Green
        } catch {
            Write-Host "  NO se pudo borrar $($archivo.FullName) -> $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host "`n=== Borrando scripts confirmados como prescindibles ===" -ForegroundColor Cyan

$archivos = @(
    "graficos_comparativa.py",
    "test.py",
    "test_confiaca.py",
    "test_confianca.py",
    "test_api_key.py",
    "prova_connexio.py",
    "analizar_corpus.py",
    "analizar_corpus_b.py",
    "analizar_corpus_nou_b.py",
    "analizar_tot.py",
    "recueperar_errores_b.py",
    "analisis_discrepancias.py",
    "comparar_a_vs_b.py",
    "comparativa_ia_manual.py",
    "generar_pdf_comparativa.py",
    "cargar_corpus.py"
)

foreach ($f in $archivos) {
    if (Test-Path -LiteralPath $f) {
        try {
            Remove-Item -LiteralPath $f -Force -ErrorAction Stop
            Write-Host "  Borrado: $f" -ForegroundColor Green
        } catch {
            Write-Host "  NO se pudo borrar $f -> $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "  (no encontrado, saltado): $f" -ForegroundColor DarkGray
    }
}

Write-Host "`n=== Listo. Todos los .csv, .png, .pdf y rubrica.txt siguen intactos. ===" -ForegroundColor Green