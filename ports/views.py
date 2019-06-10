import os
import json
import datetime

import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from parsing_scripts import update
from .models import Port, Category, BuildHistory, Maintainer, Dependency, Builder, User, Variant
from .filters import BuildHistoryFilter, PortFilterByMultiple


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
    port_id = port.id
    maintainers = Maintainer.objects.filter(ports__name=name)
    dependencies = Dependency.objects.filter(port_name_id=port_id)
    variants = Variant.objects.filter(port_id=port_id)

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
    builders = Builder.objects.all().values_list('name', flat=True)

    return render(request, 'ports/all_builds.html', {
        'builders': builders,
    })


def all_builds_filter(request):
    if request.method == 'POST':
        builder = request.POST['builder_name__name']
        status = request.POST['status']
        port_name = request.POST['port_name']
        page = request.POST['page']

        builds = BuildHistoryFilter(request.POST, queryset=BuildHistory.objects.all().order_by('-time_start')).qs

        paginated_builds = Paginator(builds, 100)
        try:
            result = paginated_builds.get_page(page)
        except PageNotAnInteger:
            result = paginated_builds.get_page(1)
        except EmptyPage:
            result = paginated_builds.get_page(paginated_builds.num_pages)

        return render(request, 'ports/builds_filtered_table.html', {
            'builds': result,
            'builder': builder,
            'status': status,
            'port_name': port_name,
        })
    else:
        return HttpResponse("Method not allowed")


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
        results = PortFilterByMultiple(request.POST, queryset=Port.objects.all()).qs[:50]

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
        response = requests.get(URL)
        Soup = BeautifulSoup(response.content, 'html5lib')
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
def search_ports_in_category(request):
    if request.method == 'POST':
        query = request.POST['name']
        search_in = request.POST['categories__name']

        filtered_ports = PortFilterByMultiple(request.POST, queryset=Port.objects.all()).qs[:50]
        return render(request, 'ports/filtered_table.html', {
            'ports': filtered_ports,
            'query': query,
            'search_in': search_in,
            'content': "Category"
            })


# Respond to ajax calls for searching within a maintainer
def search_ports_in_maintainer(request):
    if request.method == 'POST':
        query = request.POST['name']
        search_in = request.POST['maintainers__name']

        filtered_ports = PortFilterByMultiple(request.POST, queryset=Port.objects.all()).qs[:50]
        return render(request, 'ports/filtered_table.html', {
            'ports': filtered_ports,
            'query': query,
            'search_in': search_in,
            'content': "Maintainer"
        })


# Accept submissions from mpstats and update the users table
@csrf_exempt
def stats_submit(request):
    if request.method == "POST":
        try:
            received_json = json.loads(request.POST.get('submission[data]'))

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


@csrf_exempt
def update_api(request):
    if request.method == 'POST':
        key = request.POST.get('key')
        print(key)
        if key == os.environ['UPDATE_API_KEY']:
            try:
                received_json = json.loads(request.POST.get('ports'))
                update.full_update_ports(received_json)
                update.full_update_dependencies(received_json)
                return HttpResponse("Updating successful")
            except:
                return HttpResponse("Failed to parse the JSON")

        else:
            return HttpResponse("Authentication failed. Invalid Key")

    else:
        return HttpResponse('Method not allowed')
