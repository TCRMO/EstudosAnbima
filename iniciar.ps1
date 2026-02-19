Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  CFG Anbima - Plataforma de Estudos" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Aplicando migracoes do banco de dados..." -ForegroundColor Yellow
python manage.py migrate
Write-Host ""

Write-Host "[2/3] Importando questoes do cfg_questoes.json..." -ForegroundColor Yellow
python manage.py importar_questoes
Write-Host ""

Write-Host "[3/3] Iniciando servidor de desenvolvimento..." -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Acesse: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
python manage.py runserver
