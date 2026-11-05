import os
import sys
import django
from decimal import Decimal
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acervo_sonoro.settings')
django.setup()

from catalogo.models import Artista, Genero, Gravadora, Album, Faixa, Produto

GENEROS = ["Rock", "MPB", "Jazz", "Metal", "Pop", "Eletrônica"]

GRAVADORAS = [
    {"nome": "Som Livre", "pais": "Brasil"},
    {"nome": "EMI", "pais": "Reino Unido"},
    {"nome": "Columbia Records", "pais": "EUA"},
    {"nome": "Universal Music", "pais": "EUA"},
]

ARTISTAS = [
    {"nome": "Legião Urbana", "bio": "Banda de rock brasileiro formada em Brasília."},
    {"nome": "Milton Nascimento", "bio": "Cantor e compositor brasileiro fundador do Clube da Esquina."},
    {"nome": "Pink Floyd", "bio": "Banda britânica de rock progressivo."},
    {"nome": "Daft Punk", "bio": "Duo francês de música eletrônica."},
    {"nome": "Miles Davis", "bio": "Trompetista e compositor norte-americano de jazz."},
    {"nome": "Iron Maiden", "bio": "Banda britânica de heavy metal."},
    {"nome": "Chico Buarque", "bio": "Músico, dramaturgo e escritor brasileiro."},
    {"nome": "Sepultura", "bio": "Banda brasileira de heavy metal formada em Belo Horizonte."},
    {"nome": "Tim Maia", "bio": "Cantor e compositor brasileiro de soul e funk."},
    {"nome": "Fleetwood Mac", "bio": "Banda anglo-americana de rock."},
]

# Exemplo da lista de 20 álbuns (2 por artista)
ALBUNS = [
    {"titulo": "Dois", "artista": "Legião Urbana", "gravadora": "EMI", "ano": 1986, "generos": ["Rock", "MPB"]},
    {"titulo": "Que País É Este", "artista": "Legião Urbana", "gravadora": "EMI", "ano": 1987, "generos": ["Rock"]},
    {"titulo": "Clube da Esquina", "artista": "Milton Nascimento", "gravadora": "EMI", "ano": 1972, "generos": ["MPB", "Jazz"]},
    {"titulo": "Minas", "artista": "Milton Nascimento", "gravadora": "EMI", "ano": 1975, "generos": ["MPB"]},
    {"titulo": "The Dark Side of the Moon", "artista": "Pink Floyd", "gravadora": "EMI", "ano": 1973, "generos": ["Rock"]},
    {"titulo": "Wish You Were Here", "artista": "Pink Floyd", "gravadora": "Columbia Records", "ano": 1975, "generos": ["Rock"]},
    {"titulo": "Discovery", "artista": "Daft Punk", "gravadora": "Universal Music", "ano": 2001, "generos": ["Eletrônica", "Pop"]},
    {"titulo": "Random Access Memories", "artista": "Daft Punk", "gravadora": "Columbia Records", "ano": 2013, "generos": ["Eletrônica", "Pop"]},
    {"titulo": "Kind of Blue", "artista": "Miles Davis", "gravadora": "Columbia Records", "ano": 1959, "generos": ["Jazz"]},
    {"titulo": "Bitches Brew", "artista": "Miles Davis", "gravadora": "Columbia Records", "ano": 1970, "generos": ["Jazz"]},
    {"titulo": "The Number of the Beast", "artista": "Iron Maiden", "gravadora": "EMI", "ano": 1982, "generos": ["Metal", "Rock"]},
    {"titulo": "Powerslave", "artista": "Iron Maiden", "gravadora": "EMI", "ano": 1984, "generos": ["Metal"]},
    {"titulo": "Construção", "artista": "Chico Buarque", "gravadora": "Universal Music", "ano": 1971, "generos": ["MPB"]},
    {"titulo": "Meus Caros Amigos", "artista": "Chico Buarque", "gravadora": "Universal Music", "ano": 1976, "generos": ["MPB"]},
    {"titulo": "Roots", "artista": "Sepultura", "gravadora": "Universal Music", "ano": 1996, "generos": ["Metal"]},
    {"titulo": "Chaos A.D.", "artista": "Sepultura", "gravadora": "Universal Music", "ano": 1993, "generos": ["Metal"]},
    {"titulo": "Tim Maia 1973", "artista": "Tim Maia", "gravadora": "Som Livre", "ano": 1973, "generos": ["MPB", "Pop"]},
    {"titulo": "Racional Vol. 1", "artista": "Tim Maia", "gravadora": "Som Livre", "ano": 1975, "generos": ["MPB"]},
    {"titulo": "Rumours", "artista": "Fleetwood Mac", "gravadora": "Universal Music", "ano": 1977, "generos": ["Rock", "Pop"]},
    {"titulo": "Tango in the Night", "artista": "Fleetwood Mac", "gravadora": "Universal Music", "ano": 1987, "generos": ["Rock", "Pop"]},
]


def popular_catalogo():
    generos_obj = {}
    for nome in GENEROS:
        obj, _ = Genero.objects.get_or_create(nome=nome)
        generos_obj[nome] = obj

    gravadoras_obj = {}
    for g in GRAVADORAS:
        obj, _ = Gravadora.objects.get_or_create(nome=g["nome"], defaults={"pais": g["pais"]})
        gravadoras_obj[g["nome"]] = obj

    artistas_obj = {}
    for a in ARTISTAS:
        obj, _ = Artista.objects.get_or_create(nome=a["nome"], defaults={"bio": a["bio"]})
        artistas_obj[a["nome"]] = obj

    for dados in ALBUNS:
        album, _ = Album.objects.get_or_create(
            titulo=dados["titulo"],
            artista=artistas_obj[dados["artista"]],
            defaults={
                "ano": dados["ano"],
                "gravadora": gravadoras_obj[dados["gravadora"]],
                "descricao": f"Álbum clássico de {dados['artista']} lançado em {dados['ano']}.",
            }
        )
        for gen_nome in dados["generos"]:
            album.generos.add(generos_obj[gen_nome])

        # Cria 3 faixas de exemplo por álbum
        for num in range(1, 4):
            Faixa.objects.get_or_create(
                album=album,
                numero=num,
                defaults={"titulo": f"{dados['titulo']} - Faixa {num}", "duracao": 180 + num * 25}
            )

        # Cria 2 formatos por álbum (atenção às choices exatas de 'formato' no seu models.py!)
        Produto.objects.get_or_create(
            album=album,
            formato="CD",
            defaults={"preco": Decimal("49.90"), "estoque": 15, "ativo": True}
        )
        Produto.objects.get_or_create(
            album=album,
            formato="VINIL",  # Confira se na choice do model é 'VINIL', 'vinil' ou 'LP'
            defaults={"preco": Decimal("149.90"), "estoque": 5, "ativo": True}
        )

    print("Catálogo populado com sucesso!")


if __name__ == '__main__':
    popular_catalogo()