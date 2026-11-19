from django.contrib.auth.models import Group, Permission, User
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import Perfil

GRUPO_CLIENTE = "Cliente"
GRUPO_GERENTE = "Gerente"

PERMISSOES_PEDIDOS_GERENTE = (
    "view_pedido",
    "change_pedido",
    "view_itempedido",
    "change_itempedido",
)


def configurar_grupos_e_permissoes(**kwargs):
    grupo_cliente, _ = Group.objects.get_or_create(name=GRUPO_CLIENTE)
    grupo_cliente.permissions.clear()

    grupo_gerente, _ = Group.objects.get_or_create(name=GRUPO_GERENTE)

    permissoes_catalogo = Permission.objects.filter(content_type__app_label="catalogo")
    permissoes_pedidos = Permission.objects.filter(
        content_type__app_label="vendas",
        codename__in=PERMISSOES_PEDIDOS_GERENTE,
    )
    permissoes_suporte = Permission.objects.filter(
        content_type__app_label="usuarios",
        codename__in=("view_perfil", "view_endereco"),
    ) | Permission.objects.filter(
        content_type__app_label="auth",
        codename="view_user",
    )

    permissoes_gerente = (permissoes_catalogo | permissoes_pedidos | permissoes_suporte).distinct()
    grupo_gerente.permissions.set(permissoes_gerente)

    return grupo_cliente, grupo_gerente


def sincronizar_perfil(perfil):
    grupo_cliente = Group.objects.filter(name=GRUPO_CLIENTE).first()
    grupo_gerente = Group.objects.filter(name=GRUPO_GERENTE).first()
    if not grupo_cliente or not grupo_gerente or not grupo_gerente.permissions.exists():
        grupo_cliente, grupo_gerente = configurar_grupos_e_permissoes()

    user = perfil.user
    if perfil.tipo == "gerente":
        user.groups.add(grupo_gerente)
        user.groups.remove(grupo_cliente)
        novo_is_staff = True
    else:
        user.groups.add(grupo_cliente)
        user.groups.remove(grupo_gerente)
        novo_is_staff = user.is_superuser

    if user.is_staff != novo_is_staff:
        User.objects.filter(pk=user.pk).update(is_staff=novo_is_staff)
        user.is_staff = novo_is_staff


@receiver(post_migrate)
def criar_grupos_apos_migrate(sender, **kwargs):
    configurar_grupos_e_permissoes()


@receiver(post_save, sender=User)
def criar_perfil_para_novo_usuario(sender, instance, created, **kwargs):
    if created:
        tipo_inicial = "gerente" if instance.is_superuser else "cliente"
        Perfil.objects.get_or_create(user=instance, defaults={"tipo": tipo_inicial})


@receiver(post_save, sender=Perfil)
def atualizar_grupo_e_acesso_ao_salvar_perfil(sender, instance, **kwargs):
    sincronizar_perfil(instance)