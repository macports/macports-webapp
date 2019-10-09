import django_filters

from .models import BuildHistory, Port


class BuildHistoryFilter(django_filters.FilterSet):
    port_name = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter(lookup_expr='contains')

    class Meta:
        model = BuildHistory
        fields = ['builder_name__display_name']


class PortFilterByMultiple(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='search')

    class Meta:
        model = Port
        fields = ['categories__name', 'maintainers__name', 'maintainers__github']
