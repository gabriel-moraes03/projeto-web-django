from django.views.generic import TemplateView


class PrincipalView(TemplateView):
    template_name = "principal.html"
