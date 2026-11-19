from django.contrib.auth.models import Group, User
from django.test import TestCase

from usuarios.models import Perfil
from usuarios.signals import GRUPO_CLIENTE, GRUPO_GERENTE


class PerfisPermissoesTests(TestCase):
    def test_novo_usuario_ganha_perfil_cliente_e_grupo(self):
        user = User.objects.create_user(username="cliente1", password="123")
        user.refresh_from_db()

        self.assertTrue(hasattr(user, "perfil"))
        self.assertEqual(user.perfil.tipo, "cliente")
        self.assertTrue(user.perfil.eh_cliente)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.groups.filter(name=GRUPO_CLIENTE).exists())
        self.assertFalse(user.groups.filter(name=GRUPO_GERENTE).exists())

    def test_superusuario_ganha_perfil_gerente(self):
        admin_user = User.objects.create_superuser(
            username="chefe", email="chefe@acervo.com", password="123"
        )
        admin_user.refresh_from_db()

        self.assertEqual(admin_user.perfil.tipo, "gerente")
        self.assertTrue(admin_user.perfil.eh_gerente)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.groups.filter(name=GRUPO_GERENTE).exists())

    def test_promover_cliente_para_gerente_atualiza_grupo_acesso_e_permissoes(self):
        user = User.objects.create_user(username="func", password="123")
        user.perfil.tipo = "gerente"
        user.perfil.save()

        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.groups.filter(name=GRUPO_GERENTE).exists())
        self.assertFalse(user.groups.filter(name=GRUPO_CLIENTE).exists())

        # Gerencia catálogo
        self.assertTrue(user.has_perm("catalogo.add_album"))
        self.assertTrue(user.has_perm("catalogo.change_album"))
        self.assertTrue(user.has_perm("catalogo.delete_album"))
        self.assertTrue(user.has_perm("catalogo.view_produto"))

        # Nos pedidos: só visualiza e altera, sem excluir
        self.assertTrue(user.has_perm("vendas.view_pedido"))
        self.assertTrue(user.has_perm("vendas.change_pedido"))
        self.assertFalse(user.has_perm("vendas.delete_pedido"))
        self.assertFalse(user.has_perm("vendas.delete_itempedido"))

    def test_rebaixar_gerente_para_cliente_remove_acesso_admin(self):
        user = User.objects.create_user(username="exgerente", password="123")
        user.perfil.tipo = "gerente"
        user.perfil.save()

        user.perfil.tipo = "cliente"
        user.perfil.save()

        user = User.objects.get(pk=user.pk)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.groups.filter(name=GRUPO_CLIENTE).exists())
        self.assertFalse(user.groups.filter(name=GRUPO_GERENTE).exists())

    def test_cliente_nao_acessa_admin_e_gerente_acessa(self):
        cliente = User.objects.create_user(username="comprador", password="123")
        gerente = User.objects.create_user(username="gestor", password="123")
        gerente.perfil.tipo = "gerente"
        gerente.perfil.save()

        self.client.force_login(cliente)
        resp_cliente = self.client.get("/admin/")
        self.assertEqual(resp_cliente.status_code, 302)

        self.client.force_login(gerente)
        resp_gerente = self.client.get("/admin/")
        self.assertEqual(resp_gerente.status_code, 200)

    def test_grupos_existem_com_permissoes_corretas(self):
        User.objects.create_user(username="u1", password="123")
        grupo_cliente = Group.objects.get(name=GRUPO_CLIENTE)
        grupo_gerente = Group.objects.get(name=GRUPO_GERENTE)

        self.assertEqual(grupo_cliente.permissions.count(), 0)
        self.assertTrue(grupo_gerente.permissions.filter(codename="add_album").exists())
        self.assertTrue(grupo_gerente.permissions.filter(codename="change_pedido").exists())
        self.assertFalse(grupo_gerente.permissions.filter(codename="delete_pedido").exists())