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

## Armazenamento de Imagens com SeaweedFS

A aplicação roda localmente e somente o SeaweedFS roda no Docker. Com o ambiente virtual ativo, na pasta `code`, crie o arquivo de configuração a partir do exemplo:

```bash
cp env_sample.conf env.conf
```

Suba o SeaweedFS (antes é necessário abrir o Docker Desktop):

```bash
docker compose up -d
```

Crie o bucket onde as imagens serão armazenadas:

```bash
python3 scripts-bd/cria_bucket.py
```

Depois, execute a aplicação normalmente com `python3 manage.py runserver`. O SeaweedFS (S3) fica disponível em [http://localhost:8333](http://localhost:8333).

**Atenção:** As chaves de `env_sample.conf` e `seaweedfs/s3.json` são apenas para desenvolvimento. O arquivo `env.conf` não deve ser versionado.

Para voltar ao armazenamento local, defina `USAR_SEAWEEDFS=False` no arquivo `env.conf` e reinicie a aplicação. As imagens passam a ser salvas na pasta `media`.
