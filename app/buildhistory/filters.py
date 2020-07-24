import django_filters

from buildhistory.models import BuildHistory, Builder
from buildhistory.forms import STATUS_CHOICES


class BuildHistoryFilter(django_filters.FilterSet):
    port_name = django_filters.CharFilter(lookup_expr='iexact')
    status = django_filters.MultipleChoiceFilter(
        choices=STATUS_CHOICES
    )
    builder_name__name = django_filters.MultipleChoiceFilter(
        choices=[(builder.name, builder.name) for builder in Builder.objects.all()]
    )

    class Meta:
        model = BuildHistory
        fields = []
