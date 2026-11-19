from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Album, Artista, Genero, Produto


class ViewPrincipalTestCase(TestCase):
    def test_pagina_principal(self):
        resposta = self.client.get(reverse("principal"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Acervo Sonoro")
        self.assertContains(resposta, 'id="botao-tema"')

    def test_sem_albuns_nao_mostra_novidades(self):
        resposta = self.client.get(reverse("principal"))
        self.assertNotContains(resposta, "Novidades no acervo")

    def test_mostra_no_maximo_seis_albuns_mais_recentes(self):
        artista = Artista.objects.create(nome="Artista")
        albuns = [
            Album.objects.create(titulo=f"Álbum {i}", ano=2000, artista=artista)
            for i in range(8)
        ]
        resposta = self.client.get(reverse("principal"))
        self.assertContains(resposta, "Novidades no acervo")
        ultimos = list(resposta.context["ultimos"])
        self.assertEqual(len(ultimos), 6)
        self.assertEqual(ultimos, list(reversed(albuns))[:6])


class AlbumListViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rock = Genero.objects.create(nome="Rock")
        cls.jazz = Genero.objects.create(nome="Jazz")
        cls.beatles = Artista.objects.create(nome="The Beatles")
        cls.miles = Artista.objects.create(nome="Miles Davis")

        cls.abbey = Album.objects.create(titulo="Abbey Road", ano=1969, artista=cls.beatles)
        cls.abbey.generos.add(cls.rock)
        cls.kind = Album.objects.create(titulo="Kind of Blue", ano=1959, artista=cls.miles)
        cls.kind.generos.add(cls.jazz)
        cls.help = Album.objects.create(titulo="Help!", ano=1965, artista=cls.beatles)
        cls.help.generos.add(cls.rock)

        Produto.objects.create(album=cls.abbey, formato="cd", preco=Decimal("50.00"), estoque=5)
        Produto.objects.create(album=cls.abbey, formato="vinil", preco=Decimal("20.00"), estoque=5, ativo=False)
        Produto.objects.create(album=cls.kind, formato="vinil", preco=Decimal("150.00"), estoque=2)
        Produto.objects.create(album=cls.help, formato="cd", preco=Decimal("30.00"), estoque=1)

    def listar(self, **parametros):
        resposta = self.client.get(reverse("albuns"), parametros)
        self.assertEqual(resposta.status_code, 200)
        return list(resposta.context["albuns"])

    def test_lista_do_mais_recente_ao_mais_antigo(self):
        self.assertEqual(self.listar(), [self.abbey, self.help, self.kind])

    def test_busca_por_titulo(self):
        self.assertEqual(self.listar(q="kind"), [self.kind])

    def test_busca_por_artista(self):
        self.assertEqual(self.listar(q="beatles"), [self.abbey, self.help])

    def test_filtro_por_genero(self):
        self.assertEqual(self.listar(genero=self.jazz.pk), [self.kind])

    def test_filtro_por_artista(self):
        self.assertEqual(self.listar(artista=self.miles.pk), [self.kind])

    def test_filtro_de_formato_ignora_produto_inativo(self):
        self.assertEqual(self.listar(formato="vinil"), [self.kind])

    def test_ordena_por_menor_preco(self):
        self.assertEqual(self.listar(ordem="preco"), [self.help, self.abbey, self.kind])

    def test_preco_minimo_considera_so_produtos_ativos(self):
        abbey = [album for album in self.listar() if album == self.abbey][0]
        self.assertEqual(abbey.preco_minimo, Decimal("50.00"))

    def test_parametros_invalidos_nao_quebram(self):
        albuns = self.listar(genero="abc", artista="x", formato="fita", ordem="qualquer")
        self.assertEqual(albuns, [self.abbey, self.help, self.kind])

    def test_paginacao_mantem_os_filtros(self):
        for i in range(10):
            Album.objects.create(titulo=f"Beatles {i}", ano=1970, artista=self.beatles)
        resposta = self.client.get(reverse("albuns"), {"artista": self.beatles.pk})
        self.assertEqual(len(resposta.context["albuns"]), 9)
        self.assertContains(resposta, f"?artista={self.beatles.pk}&page=2")
        resposta = self.client.get(reverse("albuns"), {"artista": self.beatles.pk, "page": 2})
        self.assertEqual(len(resposta.context["albuns"]), 3)

    def test_sem_resultados_mostra_aviso(self):
        resposta = self.client.get(reverse("albuns"), {"q": "inexistente"})
        self.assertContains(resposta, "Nenhum álbum encontrado com esses filtros.")
