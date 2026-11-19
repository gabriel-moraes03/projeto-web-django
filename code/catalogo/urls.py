from django.urls import path

from .views import AlbumDetailView, AlbumListView, AvaliarView, ExcluirAvaliacaoView, PrincipalView

urlpatterns = [
    path("", PrincipalView.as_view(), name="principal"),
    path("albuns/", AlbumListView.as_view(), name="albuns"),
    path("albuns/<int:pk>/", AlbumDetailView.as_view(), name="album_detalhe"),
    path("albuns/<int:pk>/avaliar/", AvaliarView.as_view(), name="avaliar"),
    path("albuns/<int:pk>/avaliacao/excluir/", ExcluirAvaliacaoView.as_view(), name="avaliacao_excluir"),
]
