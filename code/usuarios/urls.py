from django.urls import path
from . import views


urlpatterns = [
    path("auth/login/", views.login_usuario, name="login"),
    path("auth/cadastro/", views.cadastro_usuario, name="cadastro"),
    path("auth/logout/", views.logout_usuario, name="logout"),

    path(
        "conta/enderecos/",
        views.listar_enderecos,
        name="enderecos_lista"
    ),

    path(
        "conta/enderecos/novo/",
        views.cadastrar_endereco,
        name="enderecos_novo"
    ),

    path(
        "conta/enderecos/<int:pk>/editar/",
        views.editar_endereco,
        name="enderecos_editar"
    ),

    path(
        "conta/enderecos/<int:pk>/excluir/",
        views.excluir_endereco,
        name="enderecos_excluir"
    ),
]
