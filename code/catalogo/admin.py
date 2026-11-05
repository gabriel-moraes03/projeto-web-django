from django.contrib import admin
from .models import Artista, Genero, Gravadora, Album, Faixa, Produto, Avaliacao


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

class FaixaAdmin(admin.ModelAdmin):
    list_display = ('album', 'numero', 'titulo', 'duracao')
    list_filter = ('album',)
    search_fields = ('titulo', 'album__titulo')
    ordering = ('album', 'numero')


class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('album', 'formato', 'preco', 'estoque', 'ativo')
    list_filter = ('formato', 'ativo')
    list_editable = ('preco', 'estoque')
    search_fields = ('album__titulo',)


class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('album', 'usuario', 'nota', 'data')
    list_filter = ('nota', 'data')
    search_fields = ('album__titulo', 'usuario__username')

admin.site.register(Faixa, FaixaAdmin)
admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Avaliacao, AvaliacaoAdmin)