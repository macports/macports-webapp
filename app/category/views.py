from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.functions import Lower
from rest_framework import viewsets, mixins

from category.models import Category
from category.forms import CategoryAutocompleteForm
from category.serializers import CategoriesListSerializer, CategoryHaystackSerializer
from port.models import Port
from port.filters import PortFilterByMultiple


def category(request, cat):
    try:
        category_obj = Category.objects.get(name__iexact=cat)
        all_ports = Port.get_active.filter(categories__name=cat).order_by(Lower('name'))
        portscount = all_ports.count()
        paginated_ports = Paginator(all_ports, 100)
        page = request.GET.get('page', 1)
        try:
            ports = paginated_ports.get_page(page)
        except PageNotAnInteger:
            ports = paginated_ports.get_page(1)
        except EmptyPage:
            ports = paginated_ports.get_page(paginated_ports.num_pages)
        return render(request, 'category/category.html',
                      {
                          'ports': ports,
                          'portscount': portscount,
                          'category': cat
                      })
    except Category.DoesNotExist:
        return render(request, 'category/exceptions/category_not_found.html')


# Respond to ajax calls for searching within a category
def search_ports_in_category(request):
    query = request.GET.get('name')
    search_in = request.GET.get('categories__name')

    filtered_ports = PortFilterByMultiple(request.GET, queryset=Port.get_active.all()).qs[:50]
    return render(request, 'filtered_table.html', {
        'ports': filtered_ports,
        'query': query,
        'search_in': search_in,
        'content': "Category"
    })


class CategoriesListView(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategoriesListSerializer
    queryset = Category.objects.all()


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
