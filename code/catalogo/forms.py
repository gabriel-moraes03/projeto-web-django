from django import forms

from .models import Avaliacao

OPCOES_NOTA = [(nota, f"{nota} {'★' * nota}") for nota in range(5, 0, -1)]


class AvaliacaoForm(forms.ModelForm):
    nota = forms.TypedChoiceField(
        choices=OPCOES_NOTA,
        coerce=int,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Avaliacao
        fields = ["nota", "comentario"]
        widgets = {
            "comentario": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
