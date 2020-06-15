from django.shortcuts import HttpResponseRedirect, reverse
from rest_framework import viewsets, mixins
from rest_framework.response import Response

from category.models import Category
from category.forms import CategoryAutocompleteForm
from category.serializers import CategoriesListSerializer, CategoryHaystackSerializer, CategoryDetailSerializer


def category(request, cat):
    return HttpResponseRedirect("{}?selected_facets=categories_exact:{}".format(reverse('search'), cat))


class CategoriesListView(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategoriesListSerializer
    queryset = Category.objects.all()

    def retrieve(self, request, *args, **kwargs):
        result = CategoryDetailSerializer(self.get_object())
        return Response(result.data)


class CategoryAutocompleteView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CategoryHaystackSerializer
    form = None
    form_class = CategoryAutocompleteForm

    def build_form(self):
        data = self.request.GET
        return self.form_class(data, None)

    def get_queryset(self, *args, **kwargs):
        self.form = self.build_form()
        return self.form.search()
