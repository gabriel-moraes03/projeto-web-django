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
]
