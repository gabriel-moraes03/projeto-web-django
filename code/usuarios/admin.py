from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Endereco, Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    extra = 0
    max_num = 1
    verbose_name_plural = "Perfil"


class UsuarioAdmin(UserAdmin):
    inlines = (PerfilInline,)
    list_display = ("username", "email", "first_name", "last_name", "tipo_perfil", "is_staff")
    list_filter = ("perfil__tipo", "is_staff", "is_superuser", "is_active")

    @admin.display(description="Tipo", ordering="perfil__tipo")
    def tipo_perfil(self, obj):
        try:
            return obj.perfil.get_tipo_display()
        except Perfil.DoesNotExist:
            return "-"

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "tipo", "telefone")
    list_filter = ("tipo",)
    search_fields = ("user__username", "user__email", "telefone")


class EnderecoAdmin(admin.ModelAdmin):
    list_display = ("user", "rua", "numero", "cidade", "uf", "cep")
    list_filter = ("uf", "cidade")
    search_fields = ("user__username", "rua", "bairro", "cidade", "cep")


admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)
admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Endereco, EnderecoAdmin)