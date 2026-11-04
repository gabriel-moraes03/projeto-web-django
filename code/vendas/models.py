from django.contrib.auth.models import User
from django.db import models

from catalogo.models import Produto
from usuarios.models import Endereco


class Carrinho(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="carrinho")
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrinho de {self.user.username}"


class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["carrinho", "produto"], name="produto_unico_por_carrinho"),
        ]

    def __str__(self):
        return f"{self.quantidade}x {self.produto}"


class Pedido(models.Model):
    STATUS = [
        ("pendente", "Pendente"),
        ("pago", "Pago"),
        ("enviado", "Enviado"),
        ("cancelado", "Cancelado"),
    ]

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="pedidos")
    endereco = models.ForeignKey(Endereco, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=STATUS, default="pendente")
    criado_em = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Pedido {self.pk} de {self.user.username} ({self.get_status_display()})"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    # guarda o preço no momento da compra
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.produto}"
