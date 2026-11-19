from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Endereco
from vendas.models import Pedido


class GerenciamentoEnderecosTestCase(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="cliente_teste",
            password="SenhaForte@2026!"
        )

        self.outro_usuario = User.objects.create_user(
            username="outro_cliente",
            password="OutraSenha@2026!"
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

        self.endereco_outro_usuario = Endereco.objects.create(
            user=self.outro_usuario,
            cep="30100-000",
            rua="Rua de Outro Usuario",
            numero="999",
            bairro="Funcionarios",
            cidade="Belo Horizonte",
            uf="MG"
        )

        self.url_lista = reverse("enderecos_lista")
        self.url_novo = reverse("enderecos_novo")

        self.url_editar = reverse(
            "enderecos_editar",
            args=[self.endereco.pk]
        )

        self.url_excluir = reverse(
            "enderecos_excluir",
            args=[self.endereco.pk]
        )

        self.dados_validos = {
            "cep": "37000-000",
            "rua": "Rua Nova",
            "numero": "456",
            "complemento": "Casa",
            "bairro": "Jardim",
            "cidade": "Lavras",
            "uf": "MG",
        }

    # --------------------------------------------------
    # AUTENTICACAO
    # --------------------------------------------------

    def test_listagem_exige_login(self):
        resposta = self.client.get(self.url_lista)

        self.assertRedirects(
            resposta,
            f"{reverse('login')}?next={self.url_lista}",
            fetch_redirect_response=False
        )

    def test_formulario_novo_exige_login(self):
        resposta = self.client.get(self.url_novo)

        self.assertRedirects(
            resposta,
            f"{reverse('login')}?next={self.url_novo}",
            fetch_redirect_response=False
        )

    def test_cadastro_por_post_exige_login(self):
        resposta = self.client.post(
            self.url_novo,
            self.dados_validos
        )

        self.assertRedirects(
            resposta,
            f"{reverse('login')}?next={self.url_novo}",
            fetch_redirect_response=False
        )

        self.assertFalse(
            Endereco.objects.filter(rua="Rua Nova").exists()
        )

    def test_edicao_exige_login(self):
        resposta = self.client.get(self.url_editar)

        self.assertRedirects(
            resposta,
            f"{reverse('login')}?next={self.url_editar}",
            fetch_redirect_response=False
        )

    def test_exclusao_exige_login(self):
        resposta = self.client.post(self.url_excluir)

        self.assertRedirects(
            resposta,
            f"{reverse('login')}?next={self.url_excluir}",
            fetch_redirect_response=False
        )

        self.assertTrue(
            Endereco.objects.filter(
                pk=self.endereco.pk
            ).exists()
        )

    # --------------------------------------------------
    # LISTAGEM
    # --------------------------------------------------

    def test_listagem_exibe_apenas_enderecos_do_usuario(self):
        self.client.force_login(self.usuario)

        resposta = self.client.get(self.url_lista)

        self.assertEqual(resposta.status_code, 200)

        self.assertContains(
            resposta,
            "Rua Original"
        )

        self.assertNotContains(
            resposta,
            "Rua de Outro Usuario"
        )

    def test_listagem_sem_enderecos(self):
        usuario_sem_endereco = User.objects.create_user(
            username="cliente_sem_endereco",
            password="SenhaForte@2026!"
        )

        self.client.force_login(usuario_sem_endereco)

        resposta = self.client.get(self.url_lista)

        self.assertEqual(resposta.status_code, 200)

        self.assertContains(
            resposta,
            "Você ainda não cadastrou nenhum endereço."
        )

    # --------------------------------------------------
    # CADASTRO
    # --------------------------------------------------

    def test_formulario_cadastro_carrega(self):
        self.client.force_login(self.usuario)

        resposta = self.client.get(self.url_novo)

        self.assertEqual(resposta.status_code, 200)

        self.assertContains(
            resposta,
            "Cadastrar endereço"
        )

    def test_formulario_nao_permite_escolher_usuario(self):
        self.client.force_login(self.usuario)

        resposta = self.client.get(self.url_novo)

        formulario = resposta.context["formulario"]

        self.assertNotIn(
            "user",
            formulario.fields
        )

    def test_cadastro_cria_endereco_para_usuario(self):
        self.client.force_login(self.usuario)

        resposta = self.client.post(
            self.url_novo,
            self.dados_validos
        )

        self.assertRedirects(
            resposta,
            self.url_lista
        )

        endereco = Endereco.objects.get(
            rua="Rua Nova"
        )

        self.assertEqual(
            endereco.user,
            self.usuario
        )

        self.assertEqual(
            endereco.numero,
            "456"
        )

    def test_cadastro_ignora_usuario_enviado_no_post(self):
        self.client.force_login(self.usuario)

        dados = self.dados_validos.copy()

        dados["user"] = self.outro_usuario.pk

        resposta = self.client.post(
            self.url_novo,
            dados
        )

        self.assertRedirects(
            resposta,
            self.url_lista
        )

        endereco = Endereco.objects.get(
            rua="Rua Nova"
        )

        self.assertEqual(
            endereco.user,
            self.usuario
        )

    def test_cadastro_nao_aceita_rua_vazia(self):
        self.client.force_login(self.usuario)

        dados = self.dados_validos.copy()

        dados["rua"] = ""

        resposta = self.client.post(
            self.url_novo,
            dados
        )

        self.assertEqual(resposta.status_code, 200)

        self.assertIn(
            "rua",
            resposta.context["formulario"].errors
        )

        self.assertFalse(
            Endereco.objects.filter(
                numero="456",
                user=self.usuario
            ).exists()
        )

    def test_cadastro_rejeita_cep_maior_que_limite(self):
        self.client.force_login(self.usuario)

        dados = self.dados_validos.copy()

        dados["cep"] = "1234567890"

        resposta = self.client.post(
            self.url_novo,
            dados
        )

        self.assertEqual(resposta.status_code, 200)

        self.assertIn(
            "cep",
            resposta.context["formulario"].errors
        )

        self.assertFalse(
            Endereco.objects.filter(
                rua="Rua Nova"
            ).exists()
        )

    # --------------------------------------------------
    # EDICAO
    # --------------------------------------------------

    def test_edicao_carrega_dados_existentes(self):
        self.client.force_login(self.usuario)

        resposta = self.client.get(self.url_editar)

        self.assertEqual(resposta.status_code, 200)

        self.assertContains(
            resposta,
            "Rua Original"
        )

        self.assertContains(
            resposta,
            "Editar endereço"
        )

    def test_edicao_atualiza_endereco_existente(self):
        self.client.force_login(self.usuario)

        resposta = self.client.post(
            self.url_editar,
            self.dados_validos
        )

        self.assertRedirects(
            resposta,
            self.url_lista
        )

        self.endereco.refresh_from_db()

        self.assertEqual(
            self.endereco.rua,
            "Rua Nova"
        )

        self.assertEqual(
            self.endereco.numero,
            "456"
        )

        self.assertEqual(
            Endereco.objects.filter(
                user=self.usuario
            ).count(),
            1
        )

    def test_edicao_nao_permite_trocar_proprietario(self):
        self.client.force_login(self.usuario)

        dados = self.dados_validos.copy()

        dados["user"] = self.outro_usuario.pk

        resposta = self.client.post(
            self.url_editar,
            dados
        )

        self.assertRedirects(
            resposta,
            self.url_lista
        )

        self.endereco.refresh_from_db()

        self.assertEqual(
            self.endereco.user,
            self.usuario
        )

    def test_edicao_invalida_preserva_dados_originais(self):
        self.client.force_login(self.usuario)

        dados = self.dados_validos.copy()

        dados["rua"] = ""

        resposta = self.client.post(
            self.url_editar,
            dados
        )

        self.assertEqual(resposta.status_code, 200)

        self.assertIn(
            "rua",
            resposta.context["formulario"].errors
        )

        self.endereco.refresh_from_db()

        self.assertEqual(
            self.endereco.rua,
            "Rua Original"
        )

    def test_usuario_nao_acessa_edicao_de_outro_por_get(self):
        self.client.force_login(self.usuario)

        url = reverse(
            "enderecos_editar",
            args=[self.endereco_outro_usuario.pk]
        )

        resposta = self.client.get(url)

        self.assertEqual(
            resposta.status_code,
            404
        )

    def test_usuario_nao_edita_endereco_de_outro_por_post(self):
        self.client.force_login(self.usuario)

        url = reverse(
            "enderecos_editar",
            args=[self.endereco_outro_usuario.pk]
        )

        resposta = self.client.post(
            url,
            self.dados_validos
        )

        self.assertEqual(
            resposta.status_code,
            404
        )

        self.endereco_outro_usuario.refresh_from_db()

        self.assertEqual(
            self.endereco_outro_usuario.rua,
            "Rua de Outro Usuario"
        )

    # --------------------------------------------------
    # EXCLUSAO
    # --------------------------------------------------

    def test_exclusao_por_post_remove_endereco(self):
        self.client.force_login(self.usuario)

        resposta = self.client.post(
            self.url_excluir
        )

        self.assertRedirects(
            resposta,
            self.url_lista
        )

        self.assertFalse(
            Endereco.objects.filter(
                pk=self.endereco.pk
            ).exists()
        )

        self.assertTrue(
            Endereco.objects.filter(
                pk=self.endereco_outro_usuario.pk
            ).exists()
        )

    def test_exclusao_por_get_e_bloqueada(self):
        self.client.force_login(self.usuario)

        resposta = self.client.get(
            self.url_excluir
        )

        self.assertEqual(
            resposta.status_code,
            405
        )

        self.assertTrue(
            Endereco.objects.filter(
                pk=self.endereco.pk
            ).exists()
        )

    def test_usuario_nao_exclui_endereco_de_outro(self):
        self.client.force_login(self.usuario)

        url = reverse(
            "enderecos_excluir",
            args=[self.endereco_outro_usuario.pk]
        )

        resposta = self.client.post(url)

        self.assertEqual(
            resposta.status_code,
            404
        )

        self.assertTrue(
            Endereco.objects.filter(
                pk=self.endereco_outro_usuario.pk
            ).exists()
        )

    def test_nao_exclui_endereco_vinculado_a_pedido(self):
        pedido = Pedido.objects.create(
            user=self.usuario,
            endereco=self.endereco
        )

        self.client.force_login(self.usuario)

        resposta = self.client.post(
            self.url_excluir,
            follow=True
        )

        self.assertRedirects(
            resposta,
            self.url_lista
        )

        self.assertTrue(
            Endereco.objects.filter(
                pk=self.endereco.pk
            ).exists()
        )

        self.assertTrue(
            Pedido.objects.filter(
                pk=pedido.pk
            ).exists()
        )

        self.assertContains(
            resposta,
            "Este endereço não pode ser excluído porque está vinculado a um pedido."
        )

    def test_nao_exclui_endereco_de_pedido_cancelado(self):
        Pedido.objects.create(
            user=self.usuario,
            endereco=self.endereco,
            status="cancelado"
        )

        self.client.force_login(self.usuario)

        resposta = self.client.post(
            self.url_excluir,
            follow=True
        )

        self.assertRedirects(
            resposta,
            self.url_lista
        )

        self.assertTrue(
            Endereco.objects.filter(
                pk=self.endereco.pk
            ).exists()
        )

        self.assertContains(
            resposta,
            "Este endereço não pode ser excluído porque está vinculado a um pedido."
        )
