from distutils.version import LooseVersion

from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Subquery
from rest_framework import viewsets, filters
import django_filters

from buildhistory.models import BuildHistory, Builder
from buildhistory.filters import BuildHistoryFilter
from buildhistory.serializers import BuilderSerializer, BuildHistorySerializer


def all_builds(request):
    builders = list(Builder.objects.all().order_by('display_name').distinct('display_name').values_list('display_name', flat=True))
    builders.sort(key=LooseVersion, reverse=True)
    jump_to_page = request.GET.get('page', 1)

    return render(request, 'buildhistory/all_builds.html', {
        'builders': builders,
        'jump_to_page': jump_to_page
    })


def all_builds_filter(request):
    builder = request.GET.get('builder_name__display_name')
    status = request.GET.get('status')
    port_name = request.GET.get('port_name')
    page = request.GET.get('page')

    if status == 'unresolved':
        all_latest_builds = BuildHistory.objects.all().order_by('port_name', 'builder_name__display_name', '-build_id').distinct('port_name', 'builder_name__display_name')
        builds = BuildHistoryFilter({
            'builder_name__display_name': builder,
            'port_name': port_name,
        }, queryset=BuildHistory.objects.filter(id__in=Subquery(all_latest_builds.values('id')), status__icontains='failed').select_related('builder_name').order_by('-time_start')).qs
    else:
        builds = BuildHistoryFilter(request.GET, queryset=BuildHistory.objects.all().select_related('builder_name').order_by('-time_start')).qs

    paginated_builds = Paginator(builds, 100)
    try:
        result = paginated_builds.get_page(page)
    except PageNotAnInteger:
        result = paginated_builds.get_page(1)
    except EmptyPage:
        result = paginated_builds.get_page(paginated_builds.num_pages)

    return render(request, 'buildhistory/builds_filtered_table.html', {
        'builds': result,
        'builder': builder,
        'status': status,
        'port_name': port_name,
    })


class BuilderView(viewsets.ReadOnlyModelViewSet):
    queryset = Builder.objects.all()
    serializer_class = BuilderSerializer
    detail_serializer_class = BuildHistorySerializer
    lookup_value_regex = '[a-zA-Z0-9_.]+'


class BuildHistoryView(viewsets.ReadOnlyModelViewSet):
    queryset = BuildHistory.objects.all()
    serializer_class = BuildHistorySerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter]
    lookup_value_regex = '[a-zA-Z0-9_.]+'
    ordering_fields = ['builder_name__name', 'builder_name__display_name', 'status', 'build_id', 'time_start']
    ordering = ['-time_start']
    filterset_fields = ['builder_name__name', 'builder_name__display_name', 'status']
