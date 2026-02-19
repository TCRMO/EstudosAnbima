# Guia de Deploy no PythonAnywhere

## Passo 1: Criar Conta no PythonAnywhere

1. Acesse: https://www.pythonanywhere.com
2. Clique em "Pricing & signup"
3. Escolha "Create a Beginner account" (gratuita)
4. Preencha seus dados e confirme o email

## Passo 2: Preparar o Projeto Localmente

Seu projeto já está configurado! Certifique-se de ter um repositório Git:

```bash
# No diretório do projeto
git init
git add .
git commit -m "Preparar projeto para deploy no PythonAnywhere"
```

## Passo 3: Enviar para o GitHub (ou GitLab/Bitbucket)

1. Crie um repositório no GitHub (público ou privado)
2. Adicione o remote e envie o código:

```bash
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git branch -M main
git push -u origin main
```

## Passo 4: Configurar no PythonAnywhere

### 4.1. Abrir Console Bash

1. Faça login no PythonAnywhere
2. Vá em "Consoles" no menu
3. Clique em "Bash"

### 4.2. Clonar o Repositório

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
```

### 4.3. Criar Ambiente Virtual

```bash
mkvirtualenv --python=/usr/bin/python3.10 anbima-env
```

### 4.4. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4.5. Configurar Banco de Dados

```bash
python manage.py migrate
python manage.py createsuperuser
# Preencha os dados do superusuário
```

### 4.6. Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

## Passo 5: Configurar Web App

### 5.1. Criar Web App

1. Vá em "Web" no menu principal
2. Clique em "Add a new web app"
3. Escolha "Manual configuration"
4. Selecione "Python 3.10"

### 5.2. Configurar WSGI

1. Na página Web, clique no link do arquivo WSGI
2. Delete todo o conteúdo e substitua por:

```python
import os
import sys

# Adicionar o diretório do projeto ao path
path = '/home/SEU_USUARIO_PYTHONANYWHERE/SEU_REPOSITORIO'
if path not in sys.path:
    sys.path.append(path)

# Configurar variável de ambiente do Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'anbima_cfg.settings'

# Importar a aplicação WSGI do Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**IMPORTANTE**: Substitua `SEU_USUARIO_PYTHONANYWHERE` e `SEU_REPOSITORIO` pelos valores corretos!

### 5.3. Configurar Virtualenv

Na página Web, na seção "Virtualenv":

1. Clique em "Enter path to a virtualenv"
2. Digite: `/home/SEU_USUARIO_PYTHONANYWHERE/.virtualenvs/anbima-env`

### 5.4. Configurar Arquivos Estáticos

Na seção "Static files", adicione:

- **URL**: `/static/`
- **Directory**: `/home/SEU_USUARIO_PYTHONANYWHERE/SEU_REPOSITORIO/staticfiles`

### 5.5. Configurar ALLOWED_HOSTS

Volte ao console Bash e edite o settings.py:

```bash
nano anbima_cfg/settings.py
```

Encontre a linha `ALLOWED_HOSTS = []` e altere para:

```python
ALLOWED_HOSTS = ['SEU_USUARIO.pythonanywhere.com']
```

Salve com `Ctrl+O`, Enter, e saia com `Ctrl+X`.

### 5.6. Desativar DEBUG (Recomendado para Produção)

No mesmo arquivo `settings.py`, altere:

```python
DEBUG = False
```

### 5.7. Atualizar SECRET_KEY (Importante!)

Gere uma nova SECRET_KEY para produção:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copie a chave gerada e substitua no `settings.py`.

## Passo 6: Recarregar o Site

1. Volte para a página "Web"
2. Clique no botão verde "Reload SEU_USUARIO.pythonanywhere.com"
3. Aguarde alguns segundos

## Passo 7: Acessar seu Site

Acesse: `https://SEU_USUARIO.pythonanywhere.com`

## Solução de Problemas

### Erro 502 ou 500

1. Vá em "Web" → "Error log" para ver os erros
2. Verifique se:
   - O caminho no WSGI está correto
   - O virtualenv está ativo
   - As dependências foram instaladas
   - `collectstatic` foi executado

### Site sem CSS/JavaScript

1. Verifique se `collectstatic` foi executado
2. Confirme o caminho dos arquivos estáticos na configuração Web

### Atualizar o Código

Quando fizer alterações:

```bash
# No console Bash do PythonAnywhere
cd SEU_REPOSITORIO
git pull
python manage.py migrate  # Se houver mudanças no banco
python manage.py collectstatic --noinput
# Reload na página Web
```

## Limitações da Conta Gratuita

- 1 web app
- 512 MB de espaço em disco
- Conexões HTTP apenas (HTTPS só em *.pythonanywhere.com)
- Site "dorme" após 3 meses sem acessos
- CPU limitada

## Próximos Passos

- Configure o admin do Django: `/admin`
- Se houver comando de importação, execute: `python manage.py importar_questoes`
- Teste todas as funcionalidades do site

## Recursos Úteis

- Documentação PythonAnywhere: https://help.pythonanywhere.com/
- Tutorial Django: https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/
- Suporte: forums.pythonanywhere.com
