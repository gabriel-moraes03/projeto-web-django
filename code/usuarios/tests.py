from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Perfil


class CadastroUsuarioTestCase(TestCase):

    def setUp(self):
        self.url_cadastro = reverse("cadastro")

        self.dados_validos = {
            "usuario": "cliente_novo",
            "email": "cliente@example.com",
            "telefone": "35999999999",
            "senha": "SenhaForte@2026!",
            "confirmar_senha": "SenhaForte@2026!",
        }

    def test_pagina_cadastro_carrega(self):
        resposta = self.client.get(self.url_cadastro)

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Criar conta")

    def test_cadastro_cria_usuario(self):
        resposta = self.client.post(
            self.url_cadastro,
            self.dados_validos
        )

        self.assertEqual(resposta.status_code, 302)

        self.assertTrue(
            User.objects.filter(username="cliente_novo").exists()
        )

    def test_cadastro_cria_perfil_cliente(self):
        self.client.post(
            self.url_cadastro,
            self.dados_validos
        )

        usuario = User.objects.get(username="cliente_novo")

        perfil = Perfil.objects.get(user=usuario)

        self.assertEqual(perfil.tipo, "cliente")
        self.assertEqual(perfil.telefone, "35999999999")

    def test_cadastro_realiza_login_automatico(self):
        resposta = self.client.post(
            self.url_cadastro,
            self.dados_validos
        )

        self.assertRedirects(
            resposta,
            reverse("principal")
        )

        usuario = User.objects.get(username="cliente_novo")

        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            usuario.pk
        )

    def test_cadastro_nao_aceita_senhas_diferentes(self):
        dados = self.dados_validos.copy()
        dados["confirmar_senha"] = "OutraSenha@2026!"

        resposta = self.client.post(
            self.url_cadastro,
            dados
        )

        self.assertEqual(resposta.status_code, 200)

        self.assertContains(
            resposta,
            "As senhas não coincidem."
        )

        self.assertFalse(
            User.objects.filter(username="cliente_novo").exists()
        )

    def test_cadastro_nao_aceita_senha_fraca(self):
        dados = self.dados_validos.copy()
        dados["senha"] = "123"
        dados["confirmar_senha"] = "123"

        resposta = self.client.post(
            self.url_cadastro,
            dados
        )

        self.assertEqual(resposta.status_code, 200)

        self.assertFalse(
            User.objects.filter(username="cliente_novo").exists()
        )

    def test_cadastro_nao_aceita_usuario_duplicado(self):
        User.objects.create_user(
            username="cliente_novo",
            password="SenhaExistente@2026!"
        )

        resposta = self.client.post(
            self.url_cadastro,
            self.dados_validos
        )

        self.assertEqual(resposta.status_code, 200)

        self.assertContains(
            resposta,
            "Já existe um usuário com esse nome."
        )

        self.assertEqual(
            User.objects.filter(username="cliente_novo").count(),
            1
        )

    def test_cadastro_nao_aceita_email_duplicado(self):
        User.objects.create_user(
            username="outro_cliente",
            email="cliente@example.com",
            password="SenhaExistente@2026!"
        )

        resposta = self.client.post(
            self.url_cadastro,
            self.dados_validos
        )

        self.assertEqual(resposta.status_code, 200)

        self.assertContains(
            resposta,
            "Já existe um usuário cadastrado com esse e-mail."
        )

        self.assertFalse(
            User.objects.filter(username="cliente_novo").exists()
        )

    def test_cadastro_verifica_email_sem_diferenciar_maiusculas(self):
        User.objects.create_user(
            username="outro_cliente",
            email="CLIENTE@EXAMPLE.COM",
            password="SenhaExistente@2026!"
        )

        resposta = self.client.post(
            self.url_cadastro,
            self.dados_validos
        )

        self.assertEqual(resposta.status_code, 200)

        self.assertFalse(
            User.objects.filter(username="cliente_novo").exists()
        )

    def test_usuario_autenticado_nao_acessa_cadastro(self):
        usuario = User.objects.create_user(
            username="usuario_existente",
            password="SenhaExistente@2026!"
        )

        self.client.force_login(usuario)

        resposta = self.client.get(self.url_cadastro)

        self.assertRedirects(
            resposta,
            reverse("principal")
        )


class LoginUsuarioTestCase(TestCase):

    def setUp(self):
        self.url_login = reverse("login")

        self.senha = "SenhaForte@2026!"

        self.usuario = User.objects.create_user(
            username="cliente_teste",
            email="teste@example.com",
            password=self.senha
        )

    def test_pagina_login_carrega(self):
        resposta = self.client.get(self.url_login)

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Entrar")

    def test_login_com_credenciais_corretas(self):
        resposta = self.client.post(
            self.url_login,
            {
                "usuario": "cliente_teste",
                "senha": self.senha
            }
        )

        self.assertRedirects(
            resposta,
            reverse("principal")
        )

        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.usuario.pk
        )

    def test_login_com_senha_incorreta(self):
        resposta = self.client.post(
            self.url_login,
            {
                "usuario": "cliente_teste",
                "senha": "SenhaIncorreta@2026!"
            }
        )

        self.assertEqual(resposta.status_code, 200)

        self.assertContains(
            resposta,
            "Usuário ou senha inválidos."
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session
        )

    def test_login_com_usuario_inexistente(self):
        resposta = self.client.post(
            self.url_login,
            {
                "usuario": "usuario_inexistente",
                "senha": self.senha
            }
        )

        self.assertEqual(resposta.status_code, 200)

        self.assertNotIn(
            "_auth_user_id",
            self.client.session
        )

    def test_login_redireciona_para_carrinho(self):
        resposta = self.client.post(
            self.url_login,
            {
                "usuario": "cliente_teste",
                "senha": self.senha,
                "next": "/carrinho/"
            }
        )

        self.assertRedirects(
            resposta,
            reverse("carrinho")
        )

    def test_login_nao_redireciona_para_site_externo(self):
        resposta = self.client.post(
            self.url_login,
            {
                "usuario": "cliente_teste",
                "senha": self.senha,
                "next": "https://example.com/"
            }
        )

        self.assertRedirects(
            resposta,
            reverse("principal")
        )

    def test_usuario_autenticado_nao_acessa_login(self):
        self.client.force_login(self.usuario)

        resposta = self.client.get(self.url_login)

        self.assertRedirects(
            resposta,
            reverse("principal")
        )

    def test_carrinho_exige_autenticacao(self):
        resposta = self.client.get(
            reverse("carrinho")
        )

        self.assertRedirects(
            resposta,
            "/auth/login/?next=/carrinho/",
            fetch_redirect_response=False
        )


class LogoutUsuarioTestCase(TestCase):

    def setUp(self):
        self.url_logout = reverse("logout")

        self.usuario = User.objects.create_user(
            username="cliente_teste",
            password="SenhaForte@2026!"
        )

        self.client.force_login(self.usuario)

    def test_logout_encerra_sessao(self):
        resposta = self.client.post(self.url_logout)

        self.assertRedirects(
            resposta,
            reverse("login")
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session
        )

    def test_logout_nao_aceita_get(self):
        resposta = self.client.get(self.url_logout)

        self.assertEqual(resposta.status_code, 405)

        self.assertIn(
            "_auth_user_id",
            self.client.session
        )

    def test_carrinho_exige_novo_login_apos_logout(self):
        self.client.post(self.url_logout)

        resposta = self.client.get(
            reverse("carrinho")
        )

        self.assertRedirects(
            resposta,
            "/auth/login/?next=/carrinho/",
            fetch_redirect_response=False
        )
