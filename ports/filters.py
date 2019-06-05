import django_filters

from .models import BuildHistory, Port


class BuildHistoryFilter(django_filters.FilterSet):
    class Meta:
        model = BuildHistory
        fields = ['builder_name__name', 'status']


class PortFilterByMultiple(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='search')

    class Meta:
        model = Port
        fields = ['categories__name', 'maintainers__name']
