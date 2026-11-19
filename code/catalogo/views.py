from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Exists, F, Min, OuterRef, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from .forms import AvaliacaoForm
from .models import Album, Artista, Avaliacao, Genero, Produto


def albuns_com_resumo():
    return (
        Album.objects.select_related("artista")
        .prefetch_related(
            "generos",
            Prefetch(
                "produtos",
                queryset=Produto.objects.filter(ativo=True).order_by("preco"),
                to_attr="produtos_ativos",
            ),
        )
        .annotate(
            preco_minimo=Min("produtos__preco", filter=Q(produtos__ativo=True)),
            nota_media=Avg("avaliacoes__nota"),
        )
    )


class PrincipalView(TemplateView):
    template_name = "principal.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["ultimos"] = albuns_com_resumo().order_by("-id")[:6]
        contexto["mais_avaliados"] = (
            albuns_com_resumo()
            .filter(nota_media__isnull=False)
            .order_by(F("nota_media").desc(), "titulo")[:4]
        )
        contexto["generos"] = Genero.objects.annotate(total=Count("albuns")).filter(total__gt=0).order_by("nome")
        return contexto


class AlbumListView(ListView):
    template_name = "albuns_lista.html"
    context_object_name = "albuns"
    paginate_by = 9

    def get_queryset(self):
        albuns = albuns_com_resumo()
        parametros = self.request.GET

        busca = parametros.get("q", "").strip()
        if busca:
            albuns = albuns.filter(Q(titulo__icontains=busca) | Q(artista__nome__icontains=busca))

        genero = parametros.get("genero", "")
        if genero.isdigit():
            albuns = albuns.filter(generos__id=genero)

        artista = parametros.get("artista", "")
        if artista.isdigit():
            albuns = albuns.filter(artista_id=artista)

        formato = parametros.get("formato", "")
        if formato in dict(Produto.FORMATOS):
            produto_do_formato = Produto.objects.filter(
                album=OuterRef("pk"), formato=formato, ativo=True
            )
            albuns = albuns.filter(Exists(produto_do_formato))

        ordem = parametros.get("ordem", "recentes")
        if ordem == "titulo":
            albuns = albuns.order_by("titulo")
        elif ordem == "preco":
            albuns = albuns.order_by(F("preco_minimo").asc(nulls_last=True), "titulo")
        elif ordem == "nota":
            albuns = albuns.order_by(F("nota_media").desc(nulls_last=True), "titulo")
        else:
            albuns = albuns.order_by("-ano", "titulo")

        return albuns

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["generos"] = Genero.objects.order_by("nome")
        contexto["artistas"] = Artista.objects.order_by("nome")
        contexto["formatos"] = Produto.FORMATOS
        contexto["filtros"] = self.request.GET
        parametros = self.request.GET.copy()
        parametros.pop("page", None)
        contexto["querystring"] = parametros.urlencode()
        return contexto


class AlbumDetailView(DetailView):
    template_name = "album_detalhe.html"
    context_object_name = "album"
    queryset = Album.objects.select_related("artista", "gravadora").prefetch_related(
        "generos", "faixas"
    )

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        album = self.object
        contexto["produtos"] = album.produtos.filter(ativo=True).order_by("preco")
        contexto["avaliacoes"] = album.avaliacoes.select_related("user").order_by("-criado_em")
        contexto["nota_media"] = album.avaliacoes.aggregate(media=Avg("nota"))["media"]
        if self.request.user.is_authenticated:
            minha_avaliacao = album.avaliacoes.filter(user=self.request.user).first()
            contexto["minha_avaliacao"] = minha_avaliacao
            contexto["form_avaliacao"] = AvaliacaoForm(instance=minha_avaliacao)
        return contexto


class AvaliarView(LoginRequiredMixin, View):
    def post(self, request, pk):
        album = get_object_or_404(Album, pk=pk)
        minha_avaliacao = Avaliacao.objects.filter(user=request.user, album=album).first()
        form = AvaliacaoForm(request.POST, instance=minha_avaliacao)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.user = request.user
            avaliacao.album = album
            avaliacao.save()
            messages.success(request, "Avaliação salva.")
        else:
            messages.error(request, "Não foi possível salvar: informe uma nota de 1 a 5.")
        return redirect("album_detalhe", pk=album.pk)


class ExcluirAvaliacaoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        album = get_object_or_404(Album, pk=pk)
        Avaliacao.objects.filter(user=request.user, album=album).delete()
        messages.success(request, "Avaliação removida.")
        return redirect("album_detalhe", pk=album.pk)
