import os
import sys
import django
from pathlib import Path

# Ajusta o path para encontrar o pacote acervo_sonoro na pasta code/
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acervo_sonoro.settings')
django.setup()

from catalogo.models import Avaliacao, Produto, Faixa, Album, Artista, Genero, Gravadora


def deletar_catalogo():
    print("Removendo dados do catálogo...")
    Avaliacao.objects.all().delete()
    Produto.objects.all().delete()
    Faixa.objects.all().delete()
    Album.objects.all().delete()
    Artista.objects.all().delete()
    Gravadora.objects.all().delete()
    Genero.objects.all().delete()
    print("Catálogo limpo com sucesso!")


if __name__ == '__main__':
    deletar_catalogo()