from distutils.version import LooseVersion

from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Subquery
from rest_framework import viewsets, filters
import django_filters

from buildhistory.models import BuildHistory, Builder
from buildhistory.filters import BuildHistoryFilter
from buildhistory.serializers import BuilderSerializer, BuildHistorySerializer, BuildFilesSerializer


def all_builds(request):
    # get page state (filter parameters)
    builder = request.GET.get('builder-filter', '')
    status = request.GET.get('status-filter', '')
    port_name = request.GET.get('name-filter', '')
    page = request.GET.get('page', 1)

    # generate querysets
    builders = list(Builder.objects.all().order_by('display_name').distinct('display_name').values_list('display_name', flat=True))
    builders.sort(key=LooseVersion, reverse=True)
    if status == 'unresolved':
        all_latest_builds = BuildHistory.objects.all().order_by('port_name', 'builder_name__display_name', '-build_id').distinct('port_name', 'builder_name__display_name')
        builds = BuildHistoryFilter({
            'builder_name__display_name': builder,
            'port_name': port_name,
        }, queryset=BuildHistory.objects.filter(id__in=Subquery(all_latest_builds.values('id')), status__icontains='failed').select_related('builder_name').order_by('-time_start')).qs
    else:
        builds = BuildHistoryFilter({
            'builder_name__display_name': builder,
            'port_name': port_name,
            'status': status
        }, queryset=BuildHistory.objects.all().select_related('builder_name').order_by('-time_start')).qs

    # handle pagination
    paginated_builds = Paginator(builds, 100)
    try:
        result = paginated_builds.get_page(page)
    except PageNotAnInteger:
        result = paginated_builds.get_page(1)
    except EmptyPage:
        result = paginated_builds.get_page(paginated_builds.num_pages)

    return render(request, 'buildhistory/all_builds.html', {
        'builders': builders,
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


class InstalledFilesView(viewsets.ReadOnlyModelViewSet):
    queryset = BuildHistory.objects.all()
    serializer_class = BuildFilesSerializer
