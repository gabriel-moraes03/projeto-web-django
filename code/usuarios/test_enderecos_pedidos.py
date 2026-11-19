from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Endereco
from vendas.models import Pedido


class ProtecaoEnderecoPedidoTestCase(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="cliente_pedido",
            password="SenhaForte@2026!"
        )

        self.endereco = Endereco.objects.create(
            user=self.usuario,
            cep="37200-000",
            rua="Rua Original",
            numero="123",
            complemento="Apartamento 2",
            bairro="Centro",
            cidade="Lavras",
            uf="MG"
        )

        self.pedido = Pedido.objects.create(
            user=self.usuario,
            endereco=self.endereco,
            status="pendente"
        )

        self.url_editar = reverse(
            "enderecos_editar",
            args=[self.endereco.pk]
        )

        self.url_lista = reverse("enderecos_lista")

        self.dados_alterados = {
            "cep": "37000-000",
            "rua": "Rua Modificada",
            "numero": "456",
            "complemento": "Casa",
            "bairro": "Jardim",
            "cidade": "Lavras",
            "uf": "MG",
        }

        self.client.force_login(self.usuario)

    def test_nao_permite_abrir_edicao_de_endereco_com_pedido(self):
        resposta = self.client.get(
            self.url_editar,
            follow=True
        )

        self.assertRedirects(
            resposta,
            self.url_lista
        )

        self.assertContains(
            resposta,
            "Este endereço não pode ser editado porque está vinculado a um pedido."
        )

        self.endereco.refresh_from_db()

        self.assertEqual(
            self.endereco.rua,
            "Rua Original"
        )

    def test_nao_permite_alterar_endereco_com_pedido_por_post(self):
        resposta = self.client.post(
            self.url_editar,
            self.dados_alterados,
            follow=True
        )

        self.assertRedirects(
            resposta,
            self.url_lista
        )

        self.assertContains(
            resposta,
            "Este endereço não pode ser editado porque está vinculado a um pedido."
        )

        self.endereco.refresh_from_db()

        self.assertEqual(
            self.endereco.rua,
            "Rua Original"
        )

        self.assertEqual(
            self.endereco.numero,
            "123"
        )

        self.assertEqual(
            self.endereco.cep,
            "37200-000"
        )

        self.pedido.refresh_from_db()

        self.assertEqual(
            self.pedido.endereco,
            self.endereco
        )

    def test_nao_permite_editar_endereco_de_pedido_cancelado(self):
        self.pedido.status = "cancelado"
        self.pedido.save()

        resposta = self.client.post(
            self.url_editar,
            self.dados_alterados,
            follow=True
        )

        self.assertRedirects(
            resposta,
            self.url_lista
        )

        self.assertContains(
            resposta,
            "Este endereço não pode ser editado porque está vinculado a um pedido."
        )

        self.endereco.refresh_from_db()

        self.assertEqual(
            self.endereco.rua,
            "Rua Original"
        )

        self.assertEqual(
            self.endereco.numero,
            "123"
        )

        self.assertEqual(
            self.endereco.cep,
            "37200-000"
        )
