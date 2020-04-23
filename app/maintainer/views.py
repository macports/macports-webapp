from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from maintainer.models import Maintainer
from port.models import Port
from port.filters import PortFilterByMultiple


def get_ports_of_maintainers(maintainers, request):
    i = 0
    for maintainer in maintainers:
        if i > 0:
            all_ports = maintainer.ports.all().order_by('id').filter(active=True) | all_ports
        else:
            all_ports = maintainer.ports.all().order_by('id').filter(active=True)
        i = i + 1
    all_ports_num = all_ports.count()
    paginated_ports = Paginator(all_ports, 100)
    page = request.GET.get('page', 1)
    try:
        ports = paginated_ports.get_page(page)
    except PageNotAnInteger:
        ports = paginated_ports.get_page(1)
    except EmptyPage:
        ports = paginated_ports.get_page(paginated_ports.num_pages)

    return ports, all_ports_num


def maintainer_detail_github(request, github_handle):
    maintainers = Maintainer.objects.filter(github=github_handle)
    if maintainers.count() == 0:
        return render(request, '../templates/404.html')
    ports, all_ports_num = get_ports_of_maintainers(maintainers, request)

    return render(request, 'maintainer/maintainerdetail.html', {
        'maintainers': maintainers,
        'maintainer': github_handle,
        'all_ports_num': all_ports_num,
        'ports': ports,
        'github': True,
    })


def maintainer_detail_email(request, name, domain):
    maintainers = Maintainer.objects.filter(name=name, domain=domain)
    if maintainers.count() == 0:
        return render(request, '404.html')
    ports, all_ports_num = get_ports_of_maintainers(maintainers, request)

    return render(request, 'maintainer/maintainerdetail.html', {
        'maintainers': maintainers,
        'maintainer': name,
        'ports': ports,
        'all_ports_num': all_ports_num,
        'github': False
    })


# Respond to ajax calls for searching within a maintainer
def search_ports_in_maintainer(request):
    query = request.GET.get('name', '')
    name = request.GET.get('maintainers__name', '')
    github = request.GET.get('maintainers__github')
    if name is None or name == '':
        search_in = github
    else:
        search_in = name

    filtered_ports = PortFilterByMultiple(request.GET, queryset=Port.get_active.all()).qs
    return render(request, 'filtered_table.html', {
        'ports': filtered_ports,
        'query': query,
        'search_in': search_in,
        'content': "Maintainer"
    })
