from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ports.models import Port
from .serialisers import PortSerialiser

@csrf_exempt
def fetch_port(request, name):
    if request.method == 'GET':
        try:
            port = Port.objects.get(name=name)
            serialiser = PortSerialiser(port, context={'request': request})
            return JsonResponse(serialiser.data, safe=False)
        except Port.DoesNotExist:
            response = dict()
            response['message'] = "Requested port does not exist"
            response['status_code'] = 200
            return JsonResponse(response)
    else:
        response = dict()
        response['message'] = "Method Not Allowed"
        response['status_code'] = 405
        return JsonResponse(response)
