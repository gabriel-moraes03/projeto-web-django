from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from catalogo.models import Produto

from .models import Carrinho, ItemCarrinho


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
