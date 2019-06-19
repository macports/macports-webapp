from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ports.models import Port, BuildHistory
from .serialisers import PortSerialiser, BuildHistorySerialiser, PortListSerialiser

ERROR405 = {
    'message': 'Method Not Allowed',
    'status_code': 405
}


@csrf_exempt
def fetch_port(request, name):
    if request.method == 'GET':
        try:
            port = Port.objects.get(name__iexact=name)
            serialiser = PortSerialiser(port, context={'request': request})
            return JsonResponse(serialiser.data, safe=False)
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
        serialiser = BuildHistorySerialiser(builds, many=True)
        return JsonResponse(serialiser.data, safe=False)
    else:
        return JsonResponse(ERROR405)


def fetch_portnames_of_category(request, category):
    if request.method == 'GET':
        ports = Port.objects.filter(categories__name__iexact=category).only('name')
        serialiser = PortListSerialiser(ports, many=True)
        return JsonResponse(serialiser.data, safe=False)
    else:
        return JsonResponse(ERROR405)
