from django.urls import path

from .views import PrincipalView

urlpatterns = [
    path("", PrincipalView.as_view(), name="principal"),
]
