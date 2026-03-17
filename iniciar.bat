@echo off
echo ============================================================
echo   CFG/CGA Anbima - Plataforma de Estudos
echo ============================================================
echo.

echo [1/4] Aplicando migracoes do banco de dados...
python manage.py migrate
echo.

echo [2/4] Importando questoes do cfg_questoes.json...
python manage.py importar_questoes --arquivo cfg_questoes.json
echo.

echo [3/4] Importando questoes do cga_questoes.json...
python manage.py importar_questoes --arquivo cga_questoes.json
echo.

echo [4/4] Iniciando servidor...
echo.
echo ============================================================
echo   Acesse: http://127.0.0.1:8000
echo ============================================================
echo.
python manage.py runserver
pause
