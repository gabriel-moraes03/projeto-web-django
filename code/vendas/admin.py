from django.contrib import admin, messages

from .models import Carrinho, ItemCarrinho, ItemPedido, Pedido


class ItemCarrinhoInline(admin.TabularInline):
    model = ItemCarrinho
    extra = 0


class CarrinhoAdmin(admin.ModelAdmin):
    list_display = ("user", "criado_em")
    list_filter = ("criado_em",)
    search_fields = ("user__username",)
    inlines = [ItemCarrinhoInline]


class ItemCarrinhoAdmin(admin.ModelAdmin):
    list_display = ("carrinho", "produto", "quantidade")
    list_filter = ("produto",)


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    fields = ("produto", "quantidade", "preco_unitario", "subtotal_item")
    readonly_fields = ("subtotal_item",)

    @admin.display(description="Subtotal")
    def subtotal_item(self, obj):
        if obj.pk and obj.preco_unitario is not None:
            return f"R$ {obj.subtotal:.2f}"
        return "-"


class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total", "criado_em")
    list_filter = ("status", "criado_em")
    search_fields = ("id", "user__username", "user__email")
    ordering = ("-criado_em",)
    date_hierarchy = "criado_em"
    inlines = [ItemPedidoInline]
    actions = ["marcar_como_pago", "marcar_como_enviado"]

    @admin.action(description="Marcar pedidos selecionados como pago")
    def marcar_como_pago(self, request, queryset):
        atualizados = queryset.exclude(status="cancelado").update(status="pago")
        ignorados = queryset.filter(status="cancelado").count()
        self.message_user(
            request,
            f"{atualizados} pedido(s) marcado(s) como pago.",
            level=messages.SUCCESS,
        )
        if ignorados:
            self.message_user(
                request,
                f"{ignorados} pedido(s) cancelado(s) não foram alterados.",
                level=messages.WARNING,
            )

    @admin.action(description="Marcar pedidos selecionados como enviado")
    def marcar_como_enviado(self, request, queryset):
        atualizados = queryset.exclude(status="cancelado").update(status="enviado")
        ignorados = queryset.filter(status="cancelado").count()
        self.message_user(
            request,
            f"{atualizados} pedido(s) marcado(s) como enviado.",
            level=messages.SUCCESS,
        )
        if ignorados:
            self.message_user(
                request,
                f"{ignorados} pedido(s) cancelado(s) não foram alterados.",
                level=messages.WARNING,
            )


class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ("pedido", "produto", "quantidade", "preco_unitario")
    list_filter = ("produto",)


admin.site.register(Carrinho, CarrinhoAdmin)
admin.site.register(ItemCarrinho, ItemCarrinhoAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(ItemPedido, ItemPedidoAdmin)