from django import forms

from .models import Endereco


class EnderecoForm(forms.ModelForm):

    class Meta:
        model = Endereco

        fields = [
            "cep",
            "rua",
            "numero",
            "complemento",
            "bairro",
            "cidade",
            "uf",
        ]

        labels = {
            "cep": "CEP",
            "rua": "Rua",
            "numero": "Número",
            "complemento": "Complemento",
            "bairro": "Bairro",
            "cidade": "Cidade",
            "uf": "UF",
        }

        widgets = {
            "cep": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "00000-000",
                }
            ),
            "rua": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "numero": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "complemento": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "bairro": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "cidade": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "uf": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "MG",
                    "maxlength": "2",
                }
            ),
        }
