from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from catalogo.models import Produto

from .models import Carrinho, ItemCarrinho, ItemPedido, Pedido


class EstoqueInsuficiente(Exception):
    pass


def carrinho_do_usuario(user):
    carrinho, _ = Carrinho.objects.get_or_create(user=user)
    return carrinho


def ler_quantidade(request, padrao=1):
    try:
        return int(request.POST.get("quantidade", padrao))
    except (TypeError, ValueError):
        return padrao


class CarrinhoView(LoginRequiredMixin, TemplateView):
    template_name = "carrinho.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        carrinho = carrinho_do_usuario(self.request.user)
        itens = carrinho.itens.select_related("produto__album__artista").order_by("pk")
        contexto["itens"] = itens
        contexto["total"] = sum(item.subtotal for item in itens)
        return contexto


class AdicionarAoCarrinhoView(LoginRequiredMixin, View):
    def post(self, request, produto_id):
        produto = get_object_or_404(Produto, pk=produto_id, ativo=True)
        quantidade = max(ler_quantidade(request), 1)
        carrinho = carrinho_do_usuario(request.user)
        item = carrinho.itens.filter(produto=produto).first()
        ja_no_carrinho = item.quantidade if item else 0

        if ja_no_carrinho + quantidade > produto.estoque:
            messages.error(request, f"Só há {produto.estoque} unidade(s) de {produto} em estoque.")
        else:
            ItemCarrinho.objects.update_or_create(
                carrinho=carrinho,
                produto=produto,
                defaults={"quantidade": ja_no_carrinho + quantidade},
            )
            messages.success(request, f"{produto} adicionado ao carrinho.")
        return redirect("carrinho")


class AtualizarItemView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(ItemCarrinho, pk=pk, carrinho__user=request.user)
        quantidade = ler_quantidade(request, padrao=item.quantidade)

        if quantidade <= 0:
            item.delete()
            messages.success(request, "Item removido do carrinho.")
        elif quantidade > item.produto.estoque:
            messages.error(
                request, f"Só há {item.produto.estoque} unidade(s) de {item.produto} em estoque."
            )
        else:
            item.quantidade = quantidade
            item.save()
            messages.success(request, "Quantidade atualizada.")
        return redirect("carrinho")


class RemoverItemView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(ItemCarrinho, pk=pk, carrinho__user=request.user)
        item.delete()
        return redirect("carrinho")


class CheckoutView(LoginRequiredMixin, View):
    template_name = "checkout.html"

    def get(self, request):
        carrinho = carrinho_do_usuario(request.user)
        itens = carrinho.itens.select_related("produto__album").order_by("pk")
        if not itens:
            messages.error(request, "Seu carrinho está vazio.")
            return redirect("carrinho")
        contexto = {
            "itens": itens,
            "total": sum(item.subtotal for item in itens),
            "enderecos": request.user.enderecos.all(),
        }
        return render(request, self.template_name, contexto)

    def post(self, request):
        carrinho = carrinho_do_usuario(request.user)
        itens = list(carrinho.itens.order_by("pk"))
        if not itens:
            messages.error(request, "Seu carrinho está vazio.")
            return redirect("carrinho")

        endereco_id = request.POST.get("endereco", "")
        endereco = None
        if endereco_id.isdigit():
            endereco = request.user.enderecos.filter(pk=endereco_id).first()
        if endereco is None:
            messages.error(request, "Escolha um endereço de entrega.")
            return redirect("checkout")

        try:
            with transaction.atomic():
                pedido = Pedido.objects.create(user=request.user, endereco=endereco, status="pendente")
                produtos = Produto.objects.select_for_update().in_bulk(
                    [item.produto_id for item in itens]
                )
                total = 0
                for item in itens:
                    produto = produtos[item.produto_id]
                    if not produto.ativo or item.quantidade > produto.estoque:
                        raise EstoqueInsuficiente(produto)
                    ItemPedido.objects.create(
                        pedido=pedido,
                        produto=produto,
                        quantidade=item.quantidade,
                        preco_unitario=produto.preco,
                    )
                    produto.estoque -= item.quantidade
                    produto.save(update_fields=["estoque"])
                    total += produto.preco * item.quantidade
                pedido.total = total
                pedido.save(update_fields=["total"])
                carrinho.itens.all().delete()
        except EstoqueInsuficiente as erro:
            messages.error(
                request, f"Estoque insuficiente para {erro.args[0]}. Ajuste o carrinho e tente novamente."
            )
            return redirect("carrinho")

        messages.success(request, f"Pedido {pedido.pk} realizado com sucesso!")
        return redirect("pedido_detalhe", pk=pedido.pk)


class PedidoListView(LoginRequiredMixin, ListView):
    template_name = "pedidos_lista.html"
    context_object_name = "pedidos"

    def get_queryset(self):
        return Pedido.objects.filter(user=self.request.user).order_by("-criado_em", "-pk")


class PedidoDetailView(LoginRequiredMixin, DetailView):
    template_name = "pedido_detalhe.html"
    context_object_name = "pedido"

    def get_queryset(self):
        return Pedido.objects.filter(user=self.request.user).select_related("endereco")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["itens"] = self.object.itens.select_related("produto__album__artista").order_by("pk")
        return contexto


class CancelarPedidoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk, user=request.user)
        if pedido.status != "pendente":
            messages.error(request, "Só é possível cancelar pedidos pendentes.")
            return redirect("pedido_detalhe", pk=pedido.pk)

        with transaction.atomic():
            for item in pedido.itens.all():
                Produto.objects.filter(pk=item.produto_id).update(estoque=F("estoque") + item.quantidade)
            pedido.status = "cancelado"
            pedido.save(update_fields=["status"])
        messages.success(request, "Pedido cancelado e estoque devolvido.")
        return redirect("pedido_detalhe", pk=pedido.pk)
