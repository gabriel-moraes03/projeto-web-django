from django.db.models import Avg, Exists, F, Min, OuterRef, Q
from django.views.generic import ListView, TemplateView

from .models import Album, Artista, Genero, Produto


def albuns_com_resumo():
    return (
        Album.objects.select_related("artista")
        .prefetch_related("generos")
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
