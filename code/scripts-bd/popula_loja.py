"""Carga completa para demonstrar a loja: catálogo, preços variados, faixas,
clientes de exemplo, endereços e avaliações. Pode ser rodado mais de uma vez.

Uso (dentro de code/, com a venv ativa):
    python3 scripts-bd/popula_loja.py
"""
import os
import sys
from decimal import Decimal
from pathlib import Path

import django

sys.path.append(str(Path(__file__).resolve().parent.parent))
sys.path.append(str(Path(__file__).resolve().parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "acervo_sonoro.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from catalogo.models import Album, Avaliacao, Faixa, Produto  # noqa: E402
from popula_catalogo import popular_catalogo  # noqa: E402
from usuarios.models import Endereco  # noqa: E402

# título: (preço CD, preço vinil, preço digital ou None, estoque CD, estoque vinil)
PRECOS = {
    "Dois": ("39.90", "159.90", "19.90", 12, 4),
    "Que País É Este": ("34.90", "139.90", None, 8, 0),
    "Clube da Esquina": ("54.90", "219.90", "24.90", 10, 3),
    "Minas": ("44.90", "169.90", None, 6, 2),
    "The Dark Side of the Moon": ("59.90", "249.90", "29.90", 20, 6),
    "Wish You Were Here": ("54.90", "229.90", "29.90", 14, 0),
    "Discovery": ("49.90", "199.90", "24.90", 9, 5),
    "Random Access Memories": ("64.90", "279.90", "34.90", 18, 7),
    "Kind of Blue": ("44.90", "189.90", "19.90", 11, 4),
    "Bitches Brew": ("69.90", "259.90", None, 3, 1),
    "The Number of the Beast": ("49.90", "209.90", "24.90", 15, 3),
    "Powerslave": ("49.90", "199.90", None, 7, 2),
    "Construção": ("39.90", "179.90", "19.90", 13, 5),
    "Meus Caros Amigos": ("34.90", "149.90", None, 5, 0),
    "Roots": ("44.90", "189.90", "22.90", 10, 4),
    "Chaos A.D.": ("42.90", "179.90", None, 0, 2),
    "Tim Maia 1973": ("37.90", "169.90", "17.90", 9, 3),
    "Racional Vol. 1": ("79.90", "349.90", None, 2, 1),
    "Rumours": ("54.90", "239.90", "27.90", 16, 6),
    "Tango in the Night": ("44.90", "189.90", None, 6, 0),
}

# faixas reais de alguns álbuns: (título, "m:ss")
FAIXAS = {
    "The Dark Side of the Moon": [
        ("Speak to Me", "1:07"), ("Breathe", "2:49"), ("On the Run", "3:45"), ("Time", "6:53"),
        ("The Great Gig in the Sky", "4:44"), ("Money", "6:23"), ("Us and Them", "7:49"),
        ("Any Colour You Like", "3:26"), ("Brain Damage", "3:46"), ("Eclipse", "2:12"),
    ],
    "Kind of Blue": [
        ("So What", "9:22"), ("Freddie Freeloader", "9:46"), ("Blue in Green", "5:37"),
        ("All Blues", "11:33"), ("Flamenco Sketches", "9:26"),
    ],
    "Rumours": [
        ("Second Hand News", "2:43"), ("Dreams", "4:14"), ("Never Going Back Again", "2:02"),
        ("Don't Stop", "3:11"), ("Go Your Own Way", "3:38"), ("Songbird", "3:20"),
        ("The Chain", "4:28"), ("You Make Loving Fun", "3:31"), ("I Don't Want to Know", "3:11"),
        ("Oh Daddy", "3:56"), ("Gold Dust Woman", "4:51"),
    ],
    "Discovery": [
        ("One More Time", "5:20"), ("Aerodynamic", "3:27"), ("Digital Love", "4:58"),
        ("Harder, Better, Faster, Stronger", "3:44"), ("Crescendolls", "3:31"),
        ("Nightvision", "1:44"), ("Superheroes", "3:57"), ("High Life", "3:21"),
        ("Something About Us", "3:51"), ("Voyager", "3:47"), ("Veridis Quo", "5:44"),
        ("Short Circuit", "3:26"), ("Face to Face", "4:00"), ("Too Long", "10:00"),
    ],
    "Construção": [
        ("Deus Lhe Pague", "3:19"), ("Cotidiano", "2:51"), ("Desalento", "2:47"),
        ("Construção", "6:24"), ("Cordão", "2:33"), ("Olha Maria", "3:58"),
        ("Samba de Orly", "2:40"), ("Valsinha", "2:00"), ("Minha História", "3:03"),
        ("Acalanto", "1:49"),
    ],
    "The Number of the Beast": [
        ("Invaders", "3:20"), ("Children of the Damned", "4:34"), ("The Prisoner", "6:02"),
        ("22 Acacia Avenue", "6:34"), ("The Number of the Beast", "4:25"),
        ("Run to the Hills", "3:50"), ("Gangland", "3:46"), ("Hallowed Be Thy Name", "7:08"),
    ],
}

CLIENTES = [
    ("cliente", "Ana", "Souza"),
    ("joao", "João", "Pereira"),
    ("marina", "Marina", "Lima"),
]
SENHA_CLIENTES = "acervo123"

# (usuário, álbum, nota, comentário)
AVALIACOES = [
    ("cliente", "The Dark Side of the Moon", 5, "Prensagem impecável, som cristalino."),
    ("joao", "The Dark Side of the Moon", 5, "Obrigatório em qualquer coleção."),
    ("marina", "The Dark Side of the Moon", 4, "Excelente, mas a capa do CD veio simples."),
    ("cliente", "Kind of Blue", 5, "O disco de jazz mais bonito que já ouvi."),
    ("joao", "Kind of Blue", 4, ""),
    ("marina", "Clube da Esquina", 5, "Uma obra-prima da música brasileira."),
    ("cliente", "Clube da Esquina", 5, "Chegou rápido e muito bem embalado."),
    ("joao", "Discovery", 4, "Dançante do início ao fim."),
    ("marina", "Random Access Memories", 5, "O vinil duplo é lindo!"),
    ("cliente", "Rumours", 4, "Clássico absoluto."),
    ("joao", "Roots", 5, "Pesado e cheio de brasilidade."),
    ("marina", "Construção", 5, ""),
    ("joao", "The Number of the Beast", 4, "Run to the Hills no talo."),
    ("cliente", "Tim Maia 1973", 4, "Groove puro."),
    ("marina", "Tango in the Night", 3, "Bom, mas prefiro o Rumours."),
]


def segundos(duracao):
    minutos, resto = duracao.split(":")
    return int(minutos) * 60 + int(resto)


def ajustar_produtos():
    for titulo, (cd, vinil, digital, estoque_cd, estoque_vinil) in PRECOS.items():
        album = Album.objects.get(titulo=titulo)
        Produto.objects.update_or_create(
            album=album, formato="cd", defaults={"preco": Decimal(cd), "estoque": estoque_cd, "ativo": True}
        )
        Produto.objects.update_or_create(
            album=album, formato="vinil",
            defaults={"preco": Decimal(vinil), "estoque": estoque_vinil, "ativo": True},
        )
        if digital:
            Produto.objects.update_or_create(
                album=album, formato="digital",
                defaults={"preco": Decimal(digital), "estoque": 999, "ativo": True},
            )


def ajustar_faixas():
    for titulo, faixas in FAIXAS.items():
        album = Album.objects.get(titulo=titulo)
        album.faixas.all().delete()
        for numero, (nome, duracao) in enumerate(faixas, start=1):
            Faixa.objects.create(album=album, numero=numero, titulo=nome, duracao_segundos=segundos(duracao))


def criar_clientes():
    for username, nome, sobrenome in CLIENTES:
        user, criado = User.objects.get_or_create(
            username=username, defaults={"first_name": nome, "last_name": sobrenome}
        )
        if criado:
            user.set_password(SENHA_CLIENTES)
            user.save()

    # endereço para os clientes e para os administradores, que já podem testar a compra
    for user in User.objects.filter(username__in=[c[0] for c in CLIENTES]) | User.objects.filter(is_staff=True):
        Endereco.objects.get_or_create(
            user=user,
            cep="37200-900",
            defaults={
                "rua": "Avenida Doutor Sylvio Menicucci", "numero": "1001", "bairro": "Kennedy",
                "cidade": "Lavras", "uf": "MG",
            },
        )


def criar_avaliacoes():
    for username, titulo, nota, comentario in AVALIACOES:
        Avaliacao.objects.update_or_create(
            user=User.objects.get(username=username),
            album=Album.objects.get(titulo=titulo),
            defaults={"nota": nota, "comentario": comentario},
        )


if __name__ == "__main__":
    popular_catalogo()
    ajustar_produtos()
    ajustar_faixas()
    criar_clientes()
    criar_avaliacoes()
    print("Loja pronta para demonstração!")
    print(f"Clientes: {', '.join(c[0] for c in CLIENTES)} (senha: {SENHA_CLIENTES})")
