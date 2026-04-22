# Script de compilação para Windows
Write-Host "Iniciando compilação do Executável Captura Odds Rei do Pitaco..." -ForegroundColor Cyan

# Executa o PyInstaller usando as dependências gerenciadas pelo uv
uv run pyinstaller --onefile --name "CapturaOdds" --clean main.py

Write-Host "Processo de compilação concluído!" -ForegroundColor Green
Write-Host "Seu executável (CapturaOdds.exe) está localizado na pasta 'dist'." -ForegroundColor Yellow
