from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Album, Artista, Avaliacao, Faixa, Genero, Produto


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


class AlbumDetailViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        artista = Artista.objects.create(nome="Pink Floyd")
        cls.album = Album.objects.create(titulo="Animals", ano=1977, artista=artista)
        Faixa.objects.create(album=cls.album, numero=1, titulo="Pigs on the Wing", duracao_segundos=185)
        cls.cd = Produto.objects.create(album=cls.album, formato="cd", preco=Decimal("40.00"), estoque=3)
        cls.vinil = Produto.objects.create(album=cls.album, formato="vinil", preco=Decimal("120.00"), estoque=0)
        cls.digital = Produto.objects.create(
            album=cls.album, formato="digital", preco=Decimal("15.00"), estoque=10, ativo=False
        )
        cls.cliente = User.objects.create_user("cliente", password="senha-forte-123")
        cls.outro = User.objects.create_user("outro", password="senha-forte-123")

    def url_detalhe(self):
        return reverse("album_detalhe", args=[self.album.pk])

    def url_avaliar(self):
        return reverse("avaliar", args=[self.album.pk])

    def test_mostra_faixas_e_duracao(self):
        resposta = self.client.get(self.url_detalhe())
        self.assertContains(resposta, "Pigs on the Wing")
        self.assertContains(resposta, "3:05")

    def test_mostra_so_produtos_ativos_e_esgotado(self):
        resposta = self.client.get(self.url_detalhe())
        self.assertEqual(list(resposta.context["produtos"]), [self.cd, self.vinil])
        self.assertNotContains(resposta, "Digital")
        self.assertContains(resposta, "Esgotado")

    def test_visitante_ve_entre_para_comprar(self):
        resposta = self.client.get(self.url_detalhe())
        self.assertContains(resposta, "Entre para comprar")
        self.assertNotContains(resposta, f"/carrinho/adicionar/{self.cd.pk}/")

    def test_cliente_ve_formulario_do_carrinho(self):
        self.client.force_login(self.cliente)
        resposta = self.client.get(self.url_detalhe())
        self.assertContains(resposta, f'action="/carrinho/adicionar/{self.cd.pk}/"')
        self.assertNotContains(resposta, "Entre para comprar")

    def test_album_inexistente_da_404(self):
        resposta = self.client.get(reverse("album_detalhe", args=[9999]))
        self.assertEqual(resposta.status_code, 404)

    def test_avaliar_exige_login(self):
        resposta = self.client.post(self.url_avaliar(), {"nota": 5})
        self.assertRedirects(
            resposta, f"/auth/login/?next={self.url_avaliar()}", fetch_redirect_response=False
        )
        self.assertFalse(Avaliacao.objects.exists())

    def test_criar_e_atualizar_mantem_uma_avaliacao(self):
        self.client.force_login(self.cliente)
        resposta = self.client.post(self.url_avaliar(), {"nota": 4, "comentario": "Bom"})
        self.assertRedirects(resposta, self.url_detalhe())
        self.client.post(self.url_avaliar(), {"nota": 2, "comentario": "Mudei de ideia"})
        avaliacoes = Avaliacao.objects.filter(user=self.cliente, album=self.album)
        self.assertEqual(avaliacoes.count(), 1)
        self.assertEqual(avaliacoes.get().nota, 2)

    def test_nota_fora_do_intervalo_e_rejeitada(self):
        self.client.force_login(self.cliente)
        for nota in [0, 6, "abc"]:
            self.client.post(self.url_avaliar(), {"nota": nota})
        self.assertFalse(Avaliacao.objects.exists())

    def test_excluir_remove_so_a_propria(self):
        Avaliacao.objects.create(user=self.cliente, album=self.album, nota=5)
        Avaliacao.objects.create(user=self.outro, album=self.album, nota=3)
        self.client.force_login(self.cliente)
        resposta = self.client.post(reverse("avaliacao_excluir", args=[self.album.pk]))
        self.assertRedirects(resposta, self.url_detalhe())
        self.assertFalse(Avaliacao.objects.filter(user=self.cliente).exists())
        self.assertTrue(Avaliacao.objects.filter(user=self.outro).exists())

    def test_detalhe_mostra_media_e_formulario_preenchido(self):
        Avaliacao.objects.create(user=self.cliente, album=self.album, nota=5, comentario="Obra-prima")
        Avaliacao.objects.create(user=self.outro, album=self.album, nota=2)
        self.client.force_login(self.cliente)
        resposta = self.client.get(self.url_detalhe())
        self.assertEqual(resposta.context["nota_media"], 3.5)
        self.assertContains(resposta, "3,5")
        self.assertContains(resposta, "Sua avaliação")
        self.assertEqual(resposta.context["form_avaliacao"].instance.nota, 5)
        self.assertContains(resposta, "Obra-prima")
