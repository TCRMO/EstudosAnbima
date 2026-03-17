"""
Script de setup inicial do projeto CFG/CGA Anbima.
Execute: python setup_inicial.py

Faz:
1. Migra o banco de dados
2. Importa as questões do cfg_questoes.json e cga_questoes.json
3. Inicia o servidor de desenvolvimento
"""

import os
import subprocess
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anbima_cfg.settings')
    base_dir = os.path.dirname(os.path.abspath(__file__))
    manage_py = os.path.join(base_dir, 'manage.py')

    print('=' * 60)
    print('  CFG/CGA Anbima - Setup Inicial')
    print('=' * 60)

    # 1. Migrate
    print('\n[1/4] Aplicando migrações...')
    subprocess.run([sys.executable, manage_py, 'migrate'], check=True)

    # 2. Importar questões CFG
    print('\n[2/4] Importando questões CFG...')
    subprocess.run(
        [sys.executable, manage_py, 'importar_questoes', '--arquivo', 'cfg_questoes.json'],
        check=True,
    )

    # 3. Importar questões CGA
    print('\n[3/4] Importando questões CGA...')
    subprocess.run(
        [sys.executable, manage_py, 'importar_questoes', '--arquivo', 'cga_questoes.json'],
        check=True,
    )

    # 4. Servidor
    print('\n[4/4] Iniciando servidor de desenvolvimento...')
    print('=' * 60)
    print('  Acesse: http://127.0.0.1:8000')
    print('=' * 60)
    subprocess.run([sys.executable, manage_py, 'runserver'])


if __name__ == '__main__':
    main()
