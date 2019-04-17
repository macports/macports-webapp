from django.shortcuts import render
from .models import Port, Category, BuildHistory, Maintainer, Dependency
from bs4 import BeautifulSoup
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import requests
import html5lib
import ssl


def index(request):
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X', 'Y', 'Z']
    categories = Category.objects.all()
    return render(request, 'ports/index.html', {
        'alphabet': alphabet,
        'categories': categories
    })


def categorylist(request, cat):
    all_ports = Port.objects.filter(categories__name=cat).order_by('id')
    portscount = all_ports.count()
    paginated_ports = Paginator(all_ports, 100)
    page = request.GET.get('page', 1)
    try:
        ports = paginated_ports.get_page(page)
    except PageNotAnInteger:
        ports = paginated_ports.get_page(1)
    except EmptyPage:
        ports = paginated_ports.get_page(paginated_ports.num_pages)
    return render(request, 'ports/categorylist.html',
                  {
                      'ports': ports,
                      'portscount': portscount,
                      'category': cat
                  })


def letterlist(request, letter):
    ports = Port.objects.all()
    sortedports = []
    for port in ports:
        firstletter = list(port.name)[0]
        if firstletter.casefold() == letter.casefold():
            sortedports.append(port)
    portscount = len(sortedports)

    return render(request, 'ports/letterlist.html',
                  {
                      'ports': sortedports,
                      'letter': letter.upper(),
                      'portscount': portscount
                  })


def portdetail(request, name):
    port = Port.objects.get(name=name)
    maintainers = Maintainer.objects.filter(ports__name= name)
    build_history = BuildHistory.objects.filter(port_name=name).order_by('-time_start')
    build_hsierra = build_history.filter(builder_name="10.13_x86_64")
    build_mojave = build_history.filter(builder_name="10.14_x86_64")
    build_sierra = build_history.filter(builder_name="10.12_x86_64")
    dependencies = Dependency.objects.filter(port_name_id=port.id)

    status = []
    if build_hsierra:
        status.append(build_hsierra[0])
    if build_mojave:
        status.append(build_mojave[0])
    if build_sierra:
        status.append(build_sierra[0])
    return render(request, 'ports/portdetail.html', {
        'port': port,
        'build_history': build_history,
        'status': status,
        'maintainers': maintainers,
        'dependencies': dependencies
    })


def stats(request):
    return render(request, 'ports/stats.html')


def stats_portdetail(request, name):
    port = Port.objects.get(name=name)
    return render(request, 'ports/stats_portdetail.html', {
        'port': port,
    })


def maintainer_detail(request, slug):
    maintainers = Maintainer.objects.filter(name=slug)
    for maintainer in maintainers:
        all_ports = maintainer.ports.all()

    all_ports_num = all_ports.count()
    paginated_ports = Paginator(all_ports, 100)
    page = request.GET.get('page', 1)
    try:
        ports = paginated_ports.get_page(page)
    except PageNotAnInteger:
        ports = paginated_ports.get_page(1)
    except EmptyPage:
        ports = paginated_ports.get_page(paginated_ports.num_pages)

    return render(request, 'ports/maintainerdetail.html', {
        'maintainer': maintainer,
        'ports': ports,
        'all_ports_num': all_ports_num
    })


def search(request):
    if request.method == 'POST':
        search_text = request.POST['search_text']
        search_results = Port.objects.filter(name__icontains=search_text)[:10]
        has_input = True
    else:
        search_results = Port.objects.none()

    return render(request, 'ports/search.html', {
        'search_results': search_results,
        'has_input': has_input
    })


def tickets(request):
    if request.method == 'POST':
        port_name = request.POST['portname']
        URL = "https://trac.macports.org/query?status=!closed&port=~{}".format(port_name)
        r = requests.get(URL)
        Soup = BeautifulSoup(r.content, 'html5lib')
        all_tickets = []
        for row in Soup.findAll('tr', attrs={'class': 'prio2'}):
            srow = row.find('td', attrs={'class': 'summary'})
            ticket = {}
            ticket['url'] = srow.a['href']
            ticket['title'] = srow.a.text
            all_tickets.append(ticket)

        return render(request, 'ports/tickets.html', {
            'portname': port_name,
            'tickets': all_tickets,
        })


def category_filter(request):
    if request.method == 'POST':
        if request.POST['content'] == "Category":
            query = request.POST['query']
            search_in = request.POST['search_in']

            filtered_ports = Port.objects.filter(categories__name=search_in, name__icontains=query)
            return render(request, 'ports/filtered_table.html', {
                'ports': filtered_ports,
                'search_in': search_in,
                'query': query,
                'content': "Category"
            })

        elif request.POST['content'] == "Maintainer":
            query = request.POST['query']
            search_in = request.POST['search_in']

            filtered_ports = Port.objects.filter(maintainers__name=search_in, name__icontains=query)
            return render(request, 'ports/filtered_table.html', {
                'ports': filtered_ports,
                'search_in': search_in,
                'query': query,
                'content': "Maintainer",
            })
