# Acervo Sonoro - Loja de CDs e Álbuns

Loja virtual de CDs e álbuns musicais, com catálogo, carrinho e pedidos para clientes e gestão de estoque para administradores.

Trabalho prático da disciplina GAC116 - Programação Web da Universidade Federal de Lavras (UFLA).

## Integrantes

* Gabriel Moraes de Oliveira
* Arthur Catarino Oliveira
* Luiz Felipe de Souza Marques

## Instalação e Execução

A aplicação roda localmente e somente o SeaweedFS, que armazena as imagens, roda no Docker. Antes de começar, abra o Docker Desktop.

```bash
git clone https://github.com/gabriel-moraes03/projeto-web-django.git
cd projeto-web-django/code
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
cp env_sample.conf env.conf
docker compose up -d
python3 scripts-bd/cria_bucket.py
python3 manage.py migrate
python3 manage.py collectstatic --noinput
python3 manage.py createsuperuser
python3 manage.py runserver
```

Acesse no navegador a página [http://127.0.0.1:8000/](http://127.0.0.1:8000/). O ambiente administrativo fica em [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) e o SeaweedFS (S3) em [http://localhost:8333](http://localhost:8333).

Se o script `cria_bucket.py` der erro de conexão, o SeaweedFS ainda está iniciando. Aguarde alguns segundos e execute-o novamente.

## Execuções Seguintes

Na pasta `code`:

```bash
source venv/bin/activate
docker compose up -d
python3 manage.py runserver
```

Para encerrar, pressione `Ctrl+C` e desligue o SeaweedFS:

```bash
docker compose down
```

## Armazenamento Local

Para rodar sem Docker, defina `USAR_SEAWEEDFS=False` no arquivo `env.conf` e reinicie a aplicação. As imagens passam a ser salvas na pasta `media`.

**Atenção:** As chaves de `env_sample.conf` e `seaweedfs/s3.json` são apenas para desenvolvimento. O arquivo `env.conf` não deve ser versionado.

## Estrutura do projeto

```text
projeto-web-django/
├── README.md
├── docs/
├── recursos/
└── code/
    ├── manage.py
    ├── requirements.txt
    ├── docker-compose.yml
    ├── env_sample.conf
    ├── seaweedfs/
    ├── scripts-bd/
    ├── static/
    ├── templates/
    ├── acervo_sonoro/
    ├── usuarios/
    ├── catalogo/
    └── vendas/
```
