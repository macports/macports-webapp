import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from port_detail.models import Port
from ports.models import BuildHistory
from .serializers import PortSerializer, BuildHistorySerializer, PortListSerializer

ERROR405 = {
    'message': 'Method Not Allowed',
    'status_code': 405
}


@csrf_exempt
def fetch_port(request, name):
    if request.method == 'GET':
        try:
            port = Port.objects.get(name__iexact=name)
            serializer = PortSerializer(port, context={'request': request})
            return JsonResponse(serializer.data, safe=False)
        except Port.DoesNotExist:
            response = dict()
            response['message'] = "Requested port does not exist"
            response['status_code'] = 200
            return JsonResponse(response)
    else:
        return JsonResponse(ERROR405)


def fetch_port_build_history(request, portname):
    if request.method == 'GET':
        builds = BuildHistory.objects.filter(port_name__iexact=portname).order_by('-time_start')
        serializer = BuildHistorySerializer(builds, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse(ERROR405)


def fetch_portnames_of_category(request, category):
    if request.method == 'GET':
        ports = Port.objects.filter(categories__name__iexact=category).only('name')
        serializer = PortListSerializer(ports, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse(ERROR405)


def fetch_total_number_of_ports(request):
    if request.method == 'GET':
        count = Port.objects.all().count()
        response = {
            'count': count,
            'time': datetime.datetime.now()
        }
        return JsonResponse(response)


def fetch_paginated_ports(request, page_size, page_num):
    if request.method == 'GET':
        start = page_size * (page_num - 1)
        end = page_size * page_num
        ports = Port.objects.all().order_by('name').only('name')[start:end]
        serializer = PortListSerializer(ports, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse(ERROR405)
