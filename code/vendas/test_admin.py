from decimal import Decimal

from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from catalogo.models import Album, Artista, Produto
from usuarios.models import Endereco
from vendas.admin import ItemPedidoInline, PedidoAdmin
from vendas.models import ItemPedido, Pedido


class VendasAdminTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin_vendas", email="vendas@acervo.com", password="123"
        )
        self.cliente = User.objects.create_user(username="cliente_vendas", password="123")
        self.endereco = Endereco.objects.create(
            user=self.cliente,
            cep="37200-000",
            rua="Rua Principal",
            numero="100",
            bairro="Centro",
            cidade="Lavras",
            uf="MG",
        )
        artista = Artista.objects.create(nome="Artista Teste")
        album = Album.objects.create(titulo="Álbum Teste", ano=2020, artista=artista)
        self.produto = Produto.objects.create(
            album=album, formato="cd", preco=Decimal("49.90"), estoque=10, ativo=True
        )
        self.pedido = Pedido.objects.create(
            user=self.cliente,
            endereco=self.endereco,
            status="pendente",
            total=Decimal("99.80"),
        )
        self.item = ItemPedido.objects.create(
            pedido=self.pedido,
            produto=self.produto,
            quantidade=2,
            preco_unitario=Decimal("49.90"),
        )
        self.client.force_login(self.superuser)

    def test_pedido_admin_possui_inline_e_acoes(self):
        model_admin = admin.site._registry[Pedido]
        self.assertIsInstance(model_admin, PedidoAdmin)
        self.assertIn(ItemPedidoInline, model_admin.inlines)
        self.assertIn("marcar_como_pago", model_admin.actions)
        self.assertIn("marcar_como_enviado", model_admin.actions)

    def test_tela_de_pedido_exibe_itens_inline(self):
        url = reverse("admin:vendas_pedido_change", args=[self.pedido.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Álbum Teste")
        self.assertContains(response, "99.80")

    def test_acao_marcar_como_pago_ignora_cancelados(self):
        cancelado = Pedido.objects.create(
            user=self.cliente,
            endereco=self.endereco,
            status="cancelado",
            total=Decimal("49.90"),
        )
        url = reverse("admin:vendas_pedido_changelist")
        response = self.client.post(
            url,
            {
                "action": "marcar_como_pago",
                "_selected_action": [str(self.pedido.pk), str(cancelado.pk)],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.pedido.refresh_from_db()
        cancelado.refresh_from_db()
        self.assertEqual(self.pedido.status, "pago")
        self.assertEqual(cancelado.status, "cancelado")

    def test_acao_marcar_como_enviado_ignora_cancelados(self):
        cancelado = Pedido.objects.create(
            user=self.cliente,
            endereco=self.endereco,
            status="cancelado",
            total=Decimal("49.90"),
        )
        url = reverse("admin:vendas_pedido_changelist")
        response = self.client.post(
            url,
            {
                "action": "marcar_como_enviado",
                "_selected_action": [str(self.pedido.pk), str(cancelado.pk)],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.pedido.refresh_from_db()
        cancelado.refresh_from_db()
        self.assertEqual(self.pedido.status, "enviado")
        self.assertEqual(cancelado.status, "cancelado")

    def test_gerente_visualiza_e_altera_pedido_mas_nao_exclui(self):
        gerente = User.objects.create_user(username="gerente_vendas", password="123")
        gerente.perfil.tipo = "gerente"
        gerente.perfil.save()
        gerente = User.objects.get(pk=gerente.pk)

        self.client.force_login(gerente)

        url_change = reverse("admin:vendas_pedido_change", args=[self.pedido.pk])
        self.assertEqual(self.client.get(url_change).status_code, 200)

        url_delete = reverse("admin:vendas_pedido_delete", args=[self.pedido.pk])
        self.assertEqual(self.client.get(url_delete).status_code, 403)