from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login as login_django,
    logout as logout_django,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import EnderecoForm
from .models import Endereco, Perfil


def login_usuario(request):
    if request.user.is_authenticated:
        return redirect("principal")

    proximo = request.POST.get("next") or request.GET.get("next", "")

    if request.method == "POST":
        usuario = request.POST.get("usuario", "").strip()
        senha = request.POST.get("senha", "")

        user = authenticate(
            request,
            username=usuario,
            password=senha
        )

        if user is not None:
            login_django(request, user)

            messages.success(
                request,
                "Login realizado com sucesso!"
            )

            if proximo and url_has_allowed_host_and_scheme(
                url=proximo,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            ):
                return redirect(proximo)

            return redirect("principal")

        messages.error(
            request,
            "Usuário ou senha inválidos."
        )

    return render(
        request,
        "login.html",
        {"proximo": proximo}
    )


def cadastro_usuario(request):
    if request.user.is_authenticated:
        return redirect("principal")

    if request.method == "POST":
        usuario = request.POST.get("usuario", "").strip()
        email = request.POST.get("email", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        senha = request.POST.get("senha", "")
        confirmar_senha = request.POST.get("confirmar_senha", "")

        if not usuario or not senha:
            messages.error(
                request,
                "Preencha os campos obrigatórios."
            )

        elif senha != confirmar_senha:
            messages.error(
                request,
                "As senhas não coincidem."
            )

        elif User.objects.filter(username__iexact=usuario).exists():
            messages.error(
                request,
                "Já existe um usuário com esse nome."
            )

        elif email and User.objects.filter(email__iexact=email).exists():
            messages.error(
                request,
                "Já existe um usuário cadastrado com esse e-mail."
            )

        else:
            novo_usuario = User(
                username=usuario,
                email=email
            )

            try:
                validate_password(
                    senha,
                    user=novo_usuario
                )

            except ValidationError as erro:
                for mensagem in erro.messages:
                    messages.error(request, mensagem)

            else:
                with transaction.atomic():
                    novo_usuario.set_password(senha)
                    novo_usuario.save()

                    perfil, criado = Perfil.objects.get_or_create(
                        user=novo_usuario,
                        defaults={
                            "tipo": "cliente",
                            "telefone": telefone
                        }
                    )

                    if not criado:
                        perfil.telefone = telefone
                        perfil.save(update_fields=["telefone"])

                login_django(request, novo_usuario)

                messages.success(
                    request,
                    "Cadastro realizado com sucesso! Bem-vindo ao Acervo Sonoro!"
                )

                return redirect("principal")

    return render(request, "cadastro.html")


@require_POST
def logout_usuario(request):
    logout_django(request)

    messages.success(
        request,
        "Você saiu da sua conta com sucesso!"
    )

    return redirect("login")


@login_required
def listar_enderecos(request):
    enderecos = Endereco.objects.filter(
        user=request.user
    ).order_by("id")

    return render(
        request,
        "enderecos_lista.html",
        {"enderecos": enderecos}
    )


@login_required
def cadastrar_endereco(request):
    if request.method == "POST":
        formulario = EnderecoForm(request.POST)

        if formulario.is_valid():
            endereco = formulario.save(commit=False)

            endereco.user = request.user

            endereco.save()

            messages.success(
                request,
                "Endereço cadastrado com sucesso!"
            )

            return redirect("enderecos_lista")

    else:
        formulario = EnderecoForm()

    return render(
        request,
        "enderecos_formulario.html",
        {"formulario": formulario}
    )


@login_required
def editar_endereco(request, pk):
    endereco = get_object_or_404(
        Endereco,
        pk=pk,
        user=request.user
    )

    if request.method == "POST":
        formulario = EnderecoForm(
            request.POST,
            instance=endereco
        )

        if formulario.is_valid():
            formulario.save()

            messages.success(
                request,
                "Endereço atualizado com sucesso!"
            )

            return redirect("enderecos_lista")

    else:
        formulario = EnderecoForm(
            instance=endereco
        )

    return render(
        request,
        "enderecos_formulario.html",
        {
            "formulario": formulario,
            "endereco": endereco
        }
    )


@login_required
@require_POST
def excluir_endereco(request, pk):
    endereco = get_object_or_404(
        Endereco,
        pk=pk,
        user=request.user
    )

    try:
        endereco.delete()

    except ProtectedError:
        messages.error(
            request,
            "Este endereço não pode ser excluído porque está vinculado a um pedido."
        )

    else:
        messages.success(
            request,
            "Endereço excluído com sucesso!"
        )

    return redirect("enderecos_lista")
