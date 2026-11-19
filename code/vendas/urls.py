from django.urls import path

from .views import AdicionarAoCarrinhoView, AtualizarItemView, CarrinhoView, RemoverItemView

urlpatterns = [
    path("carrinho/", CarrinhoView.as_view(), name="carrinho"),
    path("carrinho/adicionar/<int:produto_id>/", AdicionarAoCarrinhoView.as_view(), name="carrinho_adicionar"),
    path("carrinho/item/<int:pk>/atualizar/", AtualizarItemView.as_view(), name="carrinho_atualizar"),
    path("carrinho/item/<int:pk>/remover/", RemoverItemView.as_view(), name="carrinho_remover"),
]
