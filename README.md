# Acervo Sonoro - Loja de CDs e Álbuns

Loja virtual de CDs e álbuns musicais, com catálogo, carrinho e pedidos para clientes e gestão de estoque para administradores.

Trabalho prático da disciplina GAC116 - Programação Web da Universidade Federal de Lavras (UFLA).

## Integrantes

* Gabriel Moraes de Oliveira
* (incluir integrante 2)
* (incluir integrante 3)

## Instalação

Clone o repositório:

```bash
git clone <url-do-repositorio>
```

Navegue até a pasta do projeto Django:

```bash
cd projeto-web-django/code
```

Crie e ative o ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

Instale as dependências do projeto:

```bash
python3 -m pip install -r requirements.txt
```

## Execução

Aplique as migrações do banco de dados:

```bash
python3 manage.py migrate
```

Copie os arquivos estáticos:

```bash
python3 manage.py collectstatic
```

Inicie a execução do projeto Django:

```bash
python3 manage.py runserver
```

Acesse no navegador a página [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
