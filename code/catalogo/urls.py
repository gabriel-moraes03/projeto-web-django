from django.urls import path

from .views import AlbumListView, PrincipalView

urlpatterns = [
    path("", PrincipalView.as_view(), name="principal"),
    path("albuns/", AlbumListView.as_view(), name="albuns"),
]
