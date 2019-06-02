import requests
import json
import datetime

from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Port, Category, BuildHistory, Maintainer, Dependency, Builder, User, Variant


def index(request):
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X', 'Y', 'Z']
    categories = Category.objects.all().order_by('name')
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

def variantlist(request, variant):
    all_objects = Variant.objects.filter(variant=variant)
    all_objects_count = all_objects.count()
    paginated_objects = Paginator(all_objects, 100)
    page = request.GET.get('page', 1)
    try:
        objects = paginated_objects.get_page(page)
    except PageNotAnInteger:
        objects = paginated_objects.get_page(1)
    except EmptyPage:
        objects = paginated_objects.get_page(paginated_objects.num_pages)
    return render(request, 'ports/variantlist.html', {
        'objects': objects,
        'variant': variant,
        'all_objects_count': all_objects_count
    })


def portdetail(request, name):
    port = Port.objects.get(name=name)
    id = port.id
    maintainers = Maintainer.objects.filter(ports__name=name)
    dependencies = Dependency.objects.filter(port_name_id=id)
    variants = Variant.objects.filter(port_id=id)

    builders = Builder.objects.values_list('name', flat=True)
    build_history = {}
    for builder in builders:
        build_history[builder] = BuildHistory.objects.filter(builder_name__name=builder, port_name=name).order_by('-time_start')
    return render(request, 'ports/portdetail.html', {
        'port': port,
        'build_history': build_history,
        'maintainers': maintainers,
        'dependencies': dependencies,
        'variants': variants,
        'builders_list': builders,
    })


def all_builds_view(request):
    filter_applied = False
    if request.method == 'POST':
        if request.POST['status-filter']:
            filter_by = request.POST['status-filter']
            if filter_by == "All Builds":
                all_builds = BuildHistory.objects.all().order_by('-time_start')
            else:
                all_builds = BuildHistory.objects.filter(status=filter_by).order_by('-time_start')
                filter_applied = filter_by
        else:
            return HttpResponse("Something went wrong")
    else:
        all_builds = BuildHistory.objects.all().order_by('-time_start')
    paginated_builds = Paginator(all_builds, 100)
    page = request.GET.get('page', 1)
    try:
        builds = paginated_builds.get_page(page)
    except PageNotAnInteger:
        builds = paginated_builds.get_page(1)
    except EmptyPage:
        builds = paginated_builds.get_page(paginated_builds.num_pages)

    return render(request, 'ports/all_builds.html', {
        'all_builds': builds,
        'filter_applied': filter_applied,
    })


def stats(request):
    current_week = datetime.datetime.today().isocalendar()[1]
    all_submissions = User.objects.all()
    total_unique_users = all_submissions.distinct('uuid').count()
    current_week_unique = all_submissions.filter(updated_at__week=current_week).distinct('uuid').count()
    last_week_unique = all_submissions.filter(updated_at__week=current_week-1).distinct('uuid').count()
    return render(request, 'ports/stats.html', {
        'total_submissions': all_submissions.count(),
        'unique_users': total_unique_users,
        'current_week': current_week_unique,
        'last_week': last_week_unique
    })


def stats_portdetail(request, name):
    port = Port.objects.get(name=name)
    return render(request, 'ports/stats_portdetail.html', {
        'port': port,
    })


def get_ports_of_maintainers(maintainers, request):
    i = 0
    for maintainer in maintainers:
        if i > 0:
            all_ports = maintainer.ports.all().order_by('id') | all_ports
        else:
            all_ports = maintainer.ports.all().order_by('id')
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
    ports, all_ports_num = get_ports_of_maintainers(maintainers, request)

    return render(request, 'ports/maintainerdetail.html', {
        'maintainers': maintainers,
        'maintainer': github_handle,
        'all_ports_num': all_ports_num,
        'ports': ports,
        'github': True,
    })


def maintainer_detail_email(request, name, domain):
    maintainers = Maintainer.objects.filter(name=name, domain=domain)
    ports, all_ports_num = get_ports_of_maintainers(maintainers, request)

    return render(request, 'ports/maintainerdetail.html', {
        'maintainers': maintainers,
        'maintainer': name,
        'ports': ports,
        'all_ports_num': all_ports_num,
        'github': False
    })


# Respond to ajax-call triggered by the search box
def search(request):
    if request.method == 'POST':
        search_text = request.POST['search_text']
        search_by = request.POST['search_by']
        if search_by == "search-by-port-name":
            results = Port.objects.filter(name__icontains=search_text)[:50]
        elif search_by == "search-by-description":
            results = Port.objects.filter(description__search=search_text)[:50]

    return render(request, 'ports/search.html', {
        'results': results,
        'search_text': search_text,
        'search_by': search_by
    })


# Respond to ajax call for loading tickets
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


# Respond to ajax calls for searching within a category
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

        elif request.POST['content'] == "Variant":
            query = request.POST['query']
            search_in = request.POST['search_in']

            filtered_ports = Port.objects.filter(ports__variant__in=search_in)
            return render(request, 'ports/filtered_table.html', {
                'ports': filtered_ports,
                'search_in': search_in,
                'query': query,
                'content': "Maintainer",
            })


# Accept submissions from mpstats and update the users table
@csrf_exempt
def stats_submit(request):
    if request.method == "POST":
        try:
            submitted = request.body.decode("utf-8")
            received_json = json.loads(submitted.split('=')[1])

            user = User()
            user.uuid = received_json['id']
            user.osx_version = received_json['os']['osx_version']
            user.macports_version = received_json['os']['macports_version']
            user.os_arch = received_json['os']['os_arch']
            user.xcode_version = received_json['os']['xcode_version']
            user.full_json = received_json
            user.save()

            return HttpResponse("Success")

        except:
            return HttpResponse("Something went wrong")
    else:
        return HttpResponse("Method Not Allowed")
