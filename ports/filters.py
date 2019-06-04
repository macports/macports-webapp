import django_filters

from .models import BuildHistory


class BuildHistoryFilter(django_filters.FilterSet):
    class Meta:
        model = BuildHistory
        fields = ['builder_name__name', 'status']
