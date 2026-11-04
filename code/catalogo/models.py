from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Artista(models.Model):
    nome = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    foto = models.ImageField(upload_to="artistas/", blank=True)

    def __str__(self):
        return self.nome


class Genero(models.Model):
    nome = models.CharField(max_length=60, unique=True)

    class Meta:
        verbose_name = "Gênero"
        verbose_name_plural = "Gêneros"

    def __str__(self):
        return self.nome


class Gravadora(models.Model):
    nome = models.CharField(max_length=120)
    pais = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return self.nome


class Album(models.Model):
    titulo = models.CharField(max_length=150)
    ano = models.PositiveSmallIntegerField()
    capa = models.ImageField(upload_to="capas/", blank=True)
    descricao = models.TextField(blank=True)
    artista = models.ForeignKey(Artista, on_delete=models.PROTECT, related_name="albuns")
    gravadora = models.ForeignKey(
        Gravadora, on_delete=models.SET_NULL, null=True, blank=True, related_name="albuns"
    )
    generos = models.ManyToManyField(Genero, related_name="albuns")

    class Meta:
        verbose_name_plural = "Álbuns"

    def __str__(self):
        return f"{self.titulo} - {self.artista.nome}"


class Faixa(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="faixas")
    numero = models.PositiveSmallIntegerField()
    titulo = models.CharField(max_length=150)
    duracao_segundos = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["album", "numero"]
        constraints = [
            models.UniqueConstraint(fields=["album", "numero"], name="faixa_unica_por_album"),
        ]

    def __str__(self):
        return f"{self.numero}. {self.titulo}"


class Produto(models.Model):
    FORMATOS = [
        ("cd", "CD"),
        ("vinil", "Vinil"),
        ("digital", "Digital"),
    ]

    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="produtos")
    formato = models.CharField(max_length=10, choices=FORMATOS)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["album", "formato"], name="produto_unico_por_formato"),
        ]

    def __str__(self):
        return f"{self.album.titulo} ({self.get_formato_display()})"


class Avaliacao(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="avaliacoes")
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="avaliacoes")
    nota = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        constraints = [
            models.UniqueConstraint(fields=["user", "album"], name="avaliacao_unica_por_usuario"),
        ]

    def __str__(self):
        return f"{self.album.titulo}: nota {self.nota} ({self.user.username})"
