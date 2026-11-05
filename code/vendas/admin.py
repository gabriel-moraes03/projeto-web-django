from django.contrib import admin
from .models import Carrinho, ItemCarrinho, Pedido, ItemPedido


class CarrinhoAdmin(admin.ModelAdmin):
    list_display = ("user", "criado_em")
    list_filter = ("criado_em",)


class ItemCarrinhoAdmin(admin.ModelAdmin):
    list_display = ("carrinho", "produto", "quantidade")
    list_filter = ("produto",)


class PedidoAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "total", "criado_em")
    list_filter = ("status", "criado_em")
    ordering = ("-criado_em",)


class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ("pedido", "produto", "quantidade", "preco_unitario")
    list_filter = ("produto",)


admin.site.register(Carrinho, CarrinhoAdmin)
admin.site.register(ItemCarrinho, ItemCarrinhoAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(ItemPedido, ItemPedidoAdmin)
