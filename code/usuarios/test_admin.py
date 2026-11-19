from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.admin import PerfilInline, UsuarioAdmin


class UsuariosAdminTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin_test", email="admin@acervo.com", password="123"
        )
        self.cliente = User.objects.create_user(username="maria", password="123")
        self.client.force_login(self.superuser)

    def test_usuario_admin_registrado_com_inline_de_perfil(self):
        model_admin = admin.site._registry[User]
        self.assertIsInstance(model_admin, UsuarioAdmin)
        self.assertIn("tipo_perfil", model_admin.list_display)
        self.assertIn(PerfilInline, model_admin.inlines)

    def test_lista_de_usuarios_mostra_tipo_do_perfil(self):
        url = reverse("admin:auth_user_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cliente")
        self.assertContains(response, "Gerente")

    def test_edicao_de_usuario_mostra_perfil_inline(self):
        url = reverse("admin:auth_user_change", args=[self.cliente.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="perfil-0-tipo"')
        self.assertContains(response, 'name="perfil-0-telefone"')

    def test_criacao_de_usuario_nao_exibe_perfil_inline(self):
        url = reverse("admin:auth_user_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="perfil-0-tipo"')