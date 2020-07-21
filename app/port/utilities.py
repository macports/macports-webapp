from django.http import HttpResponseRedirect

from port.models import Port


def redirect_back(request, default_uri):
    redirect_uri = request.META.get('HTTP_REFERER')
    if redirect_uri:
        return HttpResponseRedirect(redirect_uri)
    else:
        return HttpResponseRedirect(default_uri)


def get_subports(port, portdir):
    subports = None

    portdir_splitted = portdir.split('/')
    if len(portdir_splitted) < 2:
        return subports

    port_name = portdir_splitted[1]

    if port == port_name:
        subports = Port.objects.filter(portdir__iexact=portdir).exclude(name=port_name).order_by('name')

    return subports
