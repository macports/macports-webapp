import django_filters

from ports.models import Port


class PortsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='search')

    class Meta:
        model = Port
        fields = ['categories__name', 'maintainers__name', 'maintainers__github']
