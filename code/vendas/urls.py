from django.urls import path

from .views import (
    AdicionarAoCarrinhoView,
    AtualizarItemView,
    CancelarPedidoView,
    CarrinhoView,
    CheckoutView,
    PedidoDetailView,
    PedidoListView,
    RemoverItemView,
)

urlpatterns = [
    path("carrinho/finalizar/", CheckoutView.as_view(), name="checkout"),
    path("carrinho/", CarrinhoView.as_view(), name="carrinho"),
    path("carrinho/adicionar/<int:produto_id>/", AdicionarAoCarrinhoView.as_view(), name="carrinho_adicionar"),
    path("carrinho/item/<int:pk>/atualizar/", AtualizarItemView.as_view(), name="carrinho_atualizar"),
    path("carrinho/item/<int:pk>/remover/", RemoverItemView.as_view(), name="carrinho_remover"),
    path("pedidos/", PedidoListView.as_view(), name="pedidos"),
    path("pedidos/<int:pk>/", PedidoDetailView.as_view(), name="pedido_detalhe"),
    path("pedidos/<int:pk>/cancelar/", CancelarPedidoView.as_view(), name="pedido_cancelar"),
]
