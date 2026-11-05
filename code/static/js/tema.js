var CHAVE_TEMA = "tema-acervo-sonoro";

function lerTemaSalvo() {
    try {
        return localStorage.getItem(CHAVE_TEMA);
    } catch (erro) {
        return null;
    }
}

function salvarTema(tema) {
    try {
        localStorage.setItem(CHAVE_TEMA, tema);
    } catch (erro) {
        // sem localStorage, o tema vale só para esta página
    }
}

function temaInicial() {
    var salvo = lerTemaSalvo();
    if (salvo === "light" || salvo === "dark") {
        return salvo;
    }
    // sem valor salvo, segue a preferência do sistema
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function aplicarTema(tema) {
    document.documentElement.setAttribute("data-bs-theme", tema);
}

// o rótulo indica o tema para o qual o botão vai trocar
function atualizarBotao(botao, tema) {
    if (tema === "dark") {
        botao.innerHTML = '<i class="fa-solid fa-sun"></i> Claro';
    } else {
        botao.innerHTML = '<i class="fa-solid fa-moon"></i> Escuro';
    }
}

// aplica já no carregamento para evitar piscar
aplicarTema(temaInicial());

document.addEventListener("DOMContentLoaded", function () {
    var botao = document.getElementById("botao-tema");
    atualizarBotao(botao, document.documentElement.getAttribute("data-bs-theme"));

    botao.addEventListener("click", function () {
        var atual = document.documentElement.getAttribute("data-bs-theme");
        var novo = atual === "dark" ? "light" : "dark";
        aplicarTema(novo);
        salvarTema(novo);
        atualizarBotao(botao, novo);
    });
});
