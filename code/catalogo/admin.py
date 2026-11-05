from django.contrib import admin
from .models import Artista, Genero, Gravadora, Album, Faixa, Produto


class FaixaInline(admin.TabularInline):
    model = Faixa
    extra = 1


class ProdutoInline(admin.TabularInline):
    model = Produto
    extra = 1


class ArtistaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


class GravadoraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pais')
    search_fields = ('nome',)


class AlbumAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'artista', 'ano', 'gravadora')
    search_fields = ('titulo', 'artista__nome')
    list_filter = ('generos', 'ano', 'gravadora') 
    filter_horizontal = ('generos',)
    ordering = ('titulo',)
    inlines = [FaixaInline, ProdutoInline]


admin.site.register(Artista, ArtistaAdmin)
admin.site.register(Genero, GeneroAdmin)
admin.site.register(Gravadora, GravadoraAdmin)
admin.site.register(Album, AlbumAdmin)