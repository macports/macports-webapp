import json

from django.shortcuts import render, HttpResponse
from django.db.models import Subquery
from rest_framework import viewsets, filters
from django.core.mail import send_mail
import django_filters

from utilities import paginate
from buildhistory.models import BuildHistory, Builder, TempBuildJSON
from django.views.decorators.csrf import csrf_exempt
from buildhistory.forms import BuildHistoryForm
from buildhistory.filters import BuildHistoryFilter
from buildhistory.serializers import BuilderSerializer, BuildHistorySerializer, BuildFilesSerializer


def all_builds(request):
    # get page state (filter parameters)
    builder_list = request.GET.getlist('builder_name__name')
    unresolved = request.GET.get('unresolved')
    port_name = request.GET.get('port_name')

    # generate querysets
    if unresolved:
        all_latest_builds = BuildHistory.objects.all().order_by('port_name', 'builder_name__display_name', '-build_id').distinct('port_name', 'builder_name__display_name')
        builds = BuildHistoryFilter(
            {
                'builder_name__name': builder_list,
                'port_name': port_name,
            },
            queryset=BuildHistory.objects.filter(id__in=Subquery(all_latest_builds.values('id')), status__icontains='failed').select_related('builder_name').order_by('-time_start')
        ).qs
    else:
        builds = BuildHistoryFilter(
            request.GET,
            queryset=BuildHistory.objects.all().select_related('builder_name').order_by('-time_start')
        ).qs

    results = paginate(request, builds, 100)

    return render(request, 'buildhistory/all_builds.html', {
        'builds': results,
        'form': BuildHistoryForm(request.GET)
    })


@csrf_exempt
def buildbot2_submit(request):
    received_body = request.body.decode()

    try:
        received_json = json.loads(received_body, encoding='utf-8')
        obj = TempBuildJSON()
        obj.build_data = received_json
        obj.save()

        BuildHistory.buildbot2_parse(received_json)

        return HttpResponse("Build data parsed successfully")
    except KeyError:
        return HttpResponse("Failed to parse build data")


class BuilderAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = Builder.objects.all()
    serializer_class = BuilderSerializer
    detail_serializer_class = BuildHistorySerializer
    lookup_value_regex = '[a-zA-Z0-9_.]+'


class BuildHistoryAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = BuildHistory.objects.all()
    serializer_class = BuildHistorySerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter]
    lookup_value_regex = '[a-zA-Z0-9_.]+'
    ordering_fields = ['builder_name__name', 'builder_name__display_name', 'status', 'build_id', 'time_start']
    ordering = ['-time_start']
    filterset_fields = ['builder_name__name', 'builder_name__display_name', 'status', 'port_name']


class InstalledFilesAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = BuildHistory.objects.all()
    serializer_class = BuildFilesSerializer
