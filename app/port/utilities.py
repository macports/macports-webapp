from django.http import HttpResponseRedirect


def redirect_back(request, default_uri):
    redirect_uri = request.META.get('HTTP_REFERER')
    if redirect_uri:
        return HttpResponseRedirect(redirect_uri)
    else:
        return HttpResponseRedirect(default_uri)
