@echo off
echo ============================================================
echo   CFG Anbima - Plataforma de Estudos
echo ============================================================
echo.

echo [1/3] Aplicando migracoes do banco de dados...
python manage.py migrate
echo.

echo [2/3] Importando questoes do cfg_questoes.json...
python manage.py importar_questoes
echo.

echo [3/3] Iniciando servidor...
echo.
echo ============================================================
echo   Acesse: http://127.0.0.1:8000
echo ============================================================
echo.
python manage.py runserver
pause
