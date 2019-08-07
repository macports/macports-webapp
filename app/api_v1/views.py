import datetime
from distutils.version import LooseVersion

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Subquery

from ports.models import Port, BuildHistory, Builder
from .serializers import PortSerializer, BuildHistorySerializer, PortListSerializer

ERROR405 = {
    'message': 'Method Not Allowed',
    'status_code': 405
}


@csrf_exempt
def api_port_info(request, name):
    if request.method == 'GET':
        try:
            fields = request.GET.get('fields')
            port = Port.objects.get(name__iexact=name)
            serializer = PortSerializer(port, context={'request': request}, fields=fields)
            return JsonResponse(serializer.data, safe=False)
        except Port.DoesNotExist:
            response = dict()
            response['message'] = "Requested port does not exist"
            response['status_code'] = 404
            return JsonResponse(response)
    else:
        return JsonResponse(ERROR405)


def api_port_builds(request, name):
    if request.method == 'GET':
        count = request.GET.get('count', 100)
        builder = request.GET.get('builder')
        status = request.GET.get('status')

        builds = BuildHistory.objects.filter(port_name__iexact=name).order_by('-time_start')[:count]

        if not builds.count() > 0:
            return JsonResponse({
                "message": "No builds found for {}".format(name),
                "status_code": 200
            })

        if builder is not None:
            builds.filter(builder_name__name=builder)
        if status is not None:
            builds.filter(status=status)

        serializer = BuildHistorySerializer(builds, many=True)

        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse(ERROR405)


def api_port_health(request, name):
    if request.method == 'GET':

        try:
            port = Port.objects.get(name__iexact=name)
        except Port.DoesNotExist:
            return JsonResponse({
                "message": "The port {} does not exist.".format(name),
                "status_code": 404
            })

        all_latest_builds = BuildHistory.objects.all()\
            .order_by('port_name', 'builder_name', '-build_id')\
            .distinct('port_name', 'builder_name')

        port_latest_builds = list(BuildHistory.objects.filter(id__in=Subquery(all_latest_builds.values('id')), port_name__iexact=name)
                                  .values('builder_name__name', 'build_id', 'status'))

        builders = list(Builder.objects.all().values_list('name', flat=True))

        if len(port_latest_builds) == 0:
            return JsonResponse({
                "message": "No builds found for {}.".format(name),
                "status_code": 200
            })
        builders.sort(key=LooseVersion, reverse=True)

        return JsonResponse(port_latest_builds, safe=False)
    else:
        return JsonResponse(ERROR405)
