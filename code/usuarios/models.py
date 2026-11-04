from django.contrib.auth.models import User
from django.db import models


class Perfil(models.Model):
    TIPOS = [
        ("cliente", "Cliente"),
        ("gerente", "Gerente"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    tipo = models.CharField(max_length=10, choices=TIPOS, default="cliente")
    telefone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_tipo_display()})"


class Endereco(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enderecos")
    cep = models.CharField(max_length=9)
    rua = models.CharField(max_length=150)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=60, blank=True)
    bairro = models.CharField(max_length=80)
    cidade = models.CharField(max_length=80)
    uf = models.CharField(max_length=2)

    class Meta:
        verbose_name_plural = "Endereços"

    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.cidade}/{self.uf}"
