from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from catalogo.models import Album, Artista, Produto

from usuarios.models import Endereco

from .models import Carrinho, ItemCarrinho, ItemPedido, Pedido


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

    def criar_endereco(self, user):
        return Endereco.objects.create(
            user=user, cep="37200-000", rua="Rua A", numero="10",
            bairro="Centro", cidade="Lavras", uf="MG",
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


class CheckoutTestCase(VendasTestCase):
    def setUp(self):
        super().setUp()
        self.endereco = self.criar_endereco(self.cliente)

    def finalizar(self, endereco=None):
        endereco = endereco or self.endereco
        return self.client.post(reverse("checkout"), {"endereco": endereco.pk})

    def test_checkout_exige_login(self):
        self.client.logout()
        resposta = self.client.get(reverse("checkout"))
        self.assertRedirects(
            resposta, "/auth/login/?next=/carrinho/finalizar/", fetch_redirect_response=False
        )

    def test_checkout_exige_carrinho_nao_vazio(self):
        resposta = self.client.get(reverse("checkout"))
        self.assertRedirects(resposta, reverse("carrinho"), fetch_redirect_response=False)
        resposta = self.finalizar()
        self.assertRedirects(resposta, reverse("carrinho"), fetch_redirect_response=False)
        self.assertFalse(Pedido.objects.exists())

    def test_checkout_mostra_resumo_e_enderecos(self):
        self.item_no_carrinho(self.cliente, self.cd, 2)
        resposta = self.client.get(reverse("checkout"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "2 x Nevermind (CD)")
        self.assertContains(resposta, f'value="{self.endereco.pk}"')

    def test_gera_pedido(self):
        self.item_no_carrinho(self.cliente, self.cd, 2)
        self.item_no_carrinho(self.cliente, self.vinil, 1)
        resposta = self.finalizar()

        pedido = Pedido.objects.get(user=self.cliente)
        self.assertRedirects(resposta, reverse("pedido_detalhe", args=[pedido.pk]))
        self.assertEqual(pedido.status, "pendente")
        self.assertEqual(pedido.endereco, self.endereco)
        self.assertEqual(pedido.total, Decimal("230.00"))
        self.assertEqual(pedido.itens.count(), 2)
        self.cd.refresh_from_db()
        self.vinil.refresh_from_db()
        self.assertEqual(self.cd.estoque, 3)
        self.assertEqual(self.vinil.estoque, 1)
        self.assertFalse(ItemCarrinho.objects.filter(carrinho__user=self.cliente).exists())

    def test_preco_do_item_fica_congelado(self):
        self.item_no_carrinho(self.cliente, self.cd, 1)
        self.finalizar()
        self.cd.preco = Decimal("99.00")
        self.cd.save()
        item = ItemPedido.objects.get(produto=self.cd)
        self.assertEqual(item.preco_unitario, Decimal("40.00"))
        self.assertEqual(item.pedido.total, Decimal("40.00"))

    def test_sem_estoque_em_um_item_nada_e_gravado(self):
        self.item_no_carrinho(self.cliente, self.cd, 2)
        self.item_no_carrinho(self.cliente, self.vinil, 2)
        Produto.objects.filter(pk=self.vinil.pk).update(estoque=1)

        resposta = self.finalizar()
        self.assertRedirects(resposta, reverse("carrinho"), fetch_redirect_response=False)
        self.assertContains(self.client.get(resposta.url), "Estoque insuficiente")
        self.assertFalse(Pedido.objects.exists())
        self.assertFalse(ItemPedido.objects.exists())
        self.cd.refresh_from_db()
        self.assertEqual(self.cd.estoque, 5)
        self.assertEqual(ItemCarrinho.objects.filter(carrinho__user=self.cliente).count(), 2)

    def test_endereco_de_outro_usuario_e_rejeitado(self):
        self.item_no_carrinho(self.cliente, self.cd, 1)
        endereco_alheio = self.criar_endereco(self.outro)
        resposta = self.finalizar(endereco_alheio)
        self.assertRedirects(resposta, reverse("checkout"), fetch_redirect_response=False)
        self.assertFalse(Pedido.objects.exists())

    def test_endereco_invalido_e_rejeitado(self):
        self.item_no_carrinho(self.cliente, self.cd, 1)
        resposta = self.client.post(reverse("checkout"), {"endereco": "abc"})
        self.assertRedirects(resposta, reverse("checkout"), fetch_redirect_response=False)
        self.assertFalse(Pedido.objects.exists())

    def test_sem_endereco_cadastrado_avisa(self):
        self.endereco.delete()
        self.item_no_carrinho(self.cliente, self.cd, 1)
        resposta = self.client.get(reverse("checkout"))
        self.assertContains(resposta, "Você ainda não tem endereço cadastrado.")
        self.assertContains(resposta, "/conta/enderecos/novo/")
        self.assertNotContains(resposta, "Confirmar pedido")


class PedidosTestCase(VendasTestCase):
    def setUp(self):
        super().setUp()
        self.endereco = self.criar_endereco(self.cliente)
        self.pedido = self.criar_pedido(self.cliente, self.endereco, "pendente")

    def criar_pedido(self, user, endereco, status):
        pedido = Pedido.objects.create(user=user, endereco=endereco, status=status, total=Decimal("80.00"))
        ItemPedido.objects.create(pedido=pedido, produto=self.cd, quantidade=2, preco_unitario=Decimal("40.00"))
        return pedido

    def test_pedidos_exigem_login(self):
        self.client.logout()
        resposta = self.client.get(reverse("pedidos"))
        self.assertRedirects(resposta, "/auth/login/?next=/pedidos/", fetch_redirect_response=False)

    def test_lista_os_proprios_pedidos(self):
        pedido_alheio = self.criar_pedido(self.outro, self.criar_endereco(self.outro), "pendente")
        resposta = self.client.get(reverse("pedidos"))
        self.assertEqual(list(resposta.context["pedidos"]), [self.pedido])
        self.assertContains(resposta, f"#{self.pedido.pk}")
        self.assertContains(resposta, "80,00")
        self.assertNotContains(resposta, f"/pedidos/{pedido_alheio.pk}/")

    def test_detalhe_do_proprio_pedido(self):
        resposta = self.client.get(reverse("pedido_detalhe", args=[self.pedido.pk]))
        self.assertContains(resposta, "Nevermind")
        self.assertContains(resposta, "80,00")
        self.assertContains(resposta, "Rua A, 10")
        self.assertContains(resposta, "Cancelar pedido")

    def test_outro_usuario_recebe_404(self):
        self.client.force_login(self.outro)
        resposta = self.client.get(reverse("pedido_detalhe", args=[self.pedido.pk]))
        self.assertEqual(resposta.status_code, 404)
        resposta = self.client.post(reverse("pedido_cancelar", args=[self.pedido.pk]))
        self.assertEqual(resposta.status_code, 404)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status, "pendente")

    def test_cancelar_pedido_pendente_devolve_estoque(self):
        resposta = self.client.post(reverse("pedido_cancelar", args=[self.pedido.pk]))
        self.assertRedirects(resposta, reverse("pedido_detalhe", args=[self.pedido.pk]))
        self.pedido.refresh_from_db()
        self.cd.refresh_from_db()
        self.assertEqual(self.pedido.status, "cancelado")
        self.assertEqual(self.cd.estoque, 7)

    def test_pedido_pago_nao_pode_ser_cancelado(self):
        pago = self.criar_pedido(self.cliente, self.endereco, "pago")
        resposta = self.client.get(reverse("pedido_detalhe", args=[pago.pk]))
        self.assertNotContains(resposta, "Cancelar pedido")
        self.client.post(reverse("pedido_cancelar", args=[pago.pk]))
        pago.refresh_from_db()
        self.cd.refresh_from_db()
        self.assertEqual(pago.status, "pago")
        self.assertEqual(self.cd.estoque, 5)
