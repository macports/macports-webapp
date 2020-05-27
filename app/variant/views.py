from django.shortcuts import HttpResponseRedirect, reverse
from rest_framework import viewsets, mixins

from variant.serializers import VariantHaystackSerializer
from variant.forms import VariantAutocompleteForm


def variant(request, v):
    return HttpResponseRedirect("{}?selected_facets=variants_exact:{}".format(reverse('search'), v))


class VariantAutocompleteView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = VariantHaystackSerializer
    form = None
    form_class = VariantAutocompleteForm

    def build_form(self):
        data = self.request.GET
        return self.form_class(data, None)

    def get_queryset(self, *args, **kwargs):
        self.form = self.build_form()
        return self.form.search()
