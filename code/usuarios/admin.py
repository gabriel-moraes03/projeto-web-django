from django.contrib import admin
from .models import Perfil, Endereco


class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "tipo", "telefone")
    list_filter = ("tipo",)
    search_fields = ("telefone",)


class EnderecoAdmin(admin.ModelAdmin):
    list_display = ("user", "rua", "numero", "cidade", "uf", "cep")
    list_filter = ("uf", "cidade")
    search_fields = ("rua", "bairro", "cidade", "cep")


admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Endereco, EnderecoAdmin)
