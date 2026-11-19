from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from catalogo.models import Album, Artista, Produto

from .models import Carrinho, ItemCarrinho


class VendasTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        artista = Artista.objects.create(nome="Nirvana")
        cls.album = Album.objects.create(titulo="Nevermind", ano=1991, artista=artista)
        cls.cd = Produto.objects.create(album=cls.album, formato="cd", preco=Decimal("40.00"), estoque=5)
        cls.vinil = Produto.objects.create(album=cls.album, formato="vinil", preco=Decimal("150.00"), estoque=2)
        cls.inativo = Produto.objects.create(
            album=cls.album, formato="digital", preco=Decimal("20.00"), estoque=10, ativo=False
        )
        cls.cliente = User.objects.create_user("cliente", password="senha-forte-123")
        cls.outro = User.objects.create_user("outro", password="senha-forte-123")

    def setUp(self):
        self.client.force_login(self.cliente)

    def adicionar(self, produto, quantidade=1):
        return self.client.post(
            reverse("carrinho_adicionar", args=[produto.pk]), {"quantidade": quantidade}
        )

    def item_no_carrinho(self, user, produto, quantidade):
        carrinho, _ = Carrinho.objects.get_or_create(user=user)
        return ItemCarrinho.objects.create(carrinho=carrinho, produto=produto, quantidade=quantidade)


class CarrinhoTestCase(VendasTestCase):
    def test_carrinho_exige_login(self):
        self.client.logout()
        resposta = self.client.get(reverse("carrinho"))
        self.assertRedirects(resposta, "/auth/login/?next=/carrinho/", fetch_redirect_response=False)

    def test_carrinho_vazio(self):
        resposta = self.client.get(reverse("carrinho"))
        self.assertContains(resposta, "Seu carrinho está vazio.")

    def test_adicionar_cria_carrinho_e_soma_quantidades(self):
        resposta = self.adicionar(self.cd, 2)
        self.assertRedirects(resposta, reverse("carrinho"))
        self.adicionar(self.cd, 1)
        item = ItemCarrinho.objects.get(carrinho__user=self.cliente, produto=self.cd)
        self.assertEqual(item.quantidade, 3)

    def test_adicionar_nao_passa_do_estoque(self):
        self.adicionar(self.vinil, 2)
        resposta = self.adicionar(self.vinil, 1)
        item = ItemCarrinho.objects.get(carrinho__user=self.cliente, produto=self.vinil)
        self.assertEqual(item.quantidade, 2)
        self.assertContains(self.client.get(resposta.url), "Só há 2 unidade(s)")

    def test_produto_inativo_da_404(self):
        resposta = self.adicionar(self.inativo)
        self.assertEqual(resposta.status_code, 404)
        self.assertFalse(ItemCarrinho.objects.exists())

    def test_total_do_carrinho(self):
        self.adicionar(self.cd, 2)
        self.adicionar(self.vinil, 1)
        resposta = self.client.get(reverse("carrinho"))
        self.assertEqual(resposta.context["total"], Decimal("230.00"))
        self.assertEqual(self.cliente.carrinho.total, Decimal("230.00"))
        self.assertContains(resposta, "230,00")

    def test_atualizar_quantidade(self):
        item = self.item_no_carrinho(self.cliente, self.cd, 1)
        self.client.post(reverse("carrinho_atualizar", args=[item.pk]), {"quantidade": 4})
        item.refresh_from_db()
        self.assertEqual(item.quantidade, 4)

    def test_atualizar_acima_do_estoque_e_ignorado(self):
        item = self.item_no_carrinho(self.cliente, self.cd, 1)
        self.client.post(reverse("carrinho_atualizar", args=[item.pk]), {"quantidade": 99})
        item.refresh_from_db()
        self.assertEqual(item.quantidade, 1)

    def test_atualizar_para_zero_remove(self):
        item = self.item_no_carrinho(self.cliente, self.cd, 1)
        self.client.post(reverse("carrinho_atualizar", args=[item.pk]), {"quantidade": 0})
        self.assertFalse(ItemCarrinho.objects.filter(pk=item.pk).exists())

    def test_remover_item(self):
        item = self.item_no_carrinho(self.cliente, self.cd, 1)
        resposta = self.client.post(reverse("carrinho_remover", args=[item.pk]))
        self.assertRedirects(resposta, reverse("carrinho"))
        self.assertFalse(ItemCarrinho.objects.filter(pk=item.pk).exists())

    def test_nao_mexe_em_item_de_outro_usuario(self):
        item = self.item_no_carrinho(self.outro, self.cd, 1)
        resposta = self.client.post(reverse("carrinho_atualizar", args=[item.pk]), {"quantidade": 3})
        self.assertEqual(resposta.status_code, 404)
        resposta = self.client.post(reverse("carrinho_remover", args=[item.pk]))
        self.assertEqual(resposta.status_code, 404)
        item.refresh_from_db()
        self.assertEqual(item.quantidade, 1)
