from django.test import TestCase
from django.urls import reverse


class ViewPrincipalTestCase(TestCase):
    def test_pagina_principal(self):
        resposta = self.client.get(reverse("principal"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Acervo Sonoro")
        self.assertContains(resposta, 'id="botao-tema"')
