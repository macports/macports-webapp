import os
import json
import datetime
from distutils.version import LooseVersion

import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Subquery

from parsing_scripts import update
from .models import Port, Category, BuildHistory, Maintainer, Dependency, Builder, User, Variant, OSDistribution, Submission, PortInstallation
from .filters import BuildHistoryFilter, PortFilterByMultiple


def index(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'ports/index.html', {
        'categories': categories
    })


def categorylist(request, cat):
    try:
        category = Category.objects.get(name__iexact=cat)
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
    except Category.DoesNotExist:
        return render(request, 'ports/exceptions/category_not_found.html')


def variantlist(request, variant):
    all_objects = Variant.objects.filter(variant=variant).select_related('port')
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


# Views for port-detail page START
def portdetail(request, name):
    try:
        req_port = Port.objects.get(name__iexact=name)

        all_latest_builds = BuildHistory.objects.all().order_by('port_name', 'builder_name', '-build_id').distinct('port_name', 'builder_name')
        port_latest_builds = list(BuildHistory.objects.filter(id__in=Subquery(all_latest_builds.values('id')), port_name__iexact=name).values('builder_name__name', 'build_id', 'status'))

        builders = list(Builder.objects.all().values_list('name', flat=True))

        builders.sort(key=LooseVersion, reverse=True)
        latest_builds = {}
        for builder in builders:
            latest_builds[builder] = next((item for item in port_latest_builds if item['builder_name__name'] == builder), False)
        return render(request, 'ports/portdetail.html', {
            'req_port': req_port,
            'latest_builds': latest_builds,
        })
    except Port.DoesNotExist:
        return render(request, 'ports/exceptions/port_not_found.html', {
            'name': name
        })


def portdetail_summary(request):
    try:
        port_name = request.GET.get('port_name')
        port = Port.objects.get(name=port_name)
        port_id = port.id
        maintainers = Maintainer.objects.filter(ports__name=port_name)
        dependencies = Dependency.objects.filter(port_name_id=port_id)
        variants = Variant.objects.filter(port_id=port_id)

        return render(request, 'ports/port-detail/summary.html', {
            'port': port,
            'maintainers': maintainers,
            'dependencies': dependencies,
            'variants': variants,
        })
    except Port.DoesNotExist:
        return HttpResponse("Visit /port/port-name/ if you are looking for ports.")


def portdetail_build_information(request):
    status = request.GET.get('status', '')
    builder = request.GET.get('builder_name__name', '')
    port_name = request.GET.get('port_name', '')
    page = request.GET.get('page', 1)
    builders = list(Builder.objects.all().values_list('name', flat=True))
    builders.sort(key=LooseVersion, reverse=True)
    builds = BuildHistoryFilter({
        'builder_name__name': builder,
        'status': status,
    }, queryset=BuildHistory.objects.filter(port_name__iexact=port_name).select_related('builder_name').order_by('-time_start')).qs
    paginated_builds = Paginator(builds, 100)
    try:
        result = paginated_builds.get_page(page)
    except PageNotAnInteger:
        result = paginated_builds.get_page(1)
    except EmptyPage:
        result = paginated_builds.get_page(paginated_builds.num_pages)

    return render(request, 'ports/port-detail/build_information.html', {
        'builds': result,
        'builder': builder,
        'builders_list': builders,
        'status': status,
    })


def portdetail_stats(request):
    return HttpResponse("To Be Added Soon")


def all_builds_view(request):
    builders = list(Builder.objects.all().values_list('name', flat=True))
    builders.sort(key=LooseVersion, reverse=True)
    jump_to_page = request.GET.get('page', 1)

    return render(request, 'ports/all_builds.html', {
        'builders': builders,
        'jump_to_page': jump_to_page
    })


def all_builds_filter(request):
    builder = request.GET.get('builder_name__name')
    status = request.GET.get('status')
    port_name = request.GET.get('port_name')
    page = request.GET.get('page')

    if status == 'unresolved':
        all_latest_builds = BuildHistory.objects.all().order_by('port_name', 'builder_name', '-build_id').distinct('port_name', 'builder_name')
        builds = BuildHistoryFilter({
            'builder_name__name': builder,
            'port_name': port_name,
        }, queryset=BuildHistory.objects.filter(id__in=Subquery(all_latest_builds.values('id')), status__icontains='failed').select_related('builder_name').order_by('-time_start')).qs
    else:
        builds = BuildHistoryFilter(request.GET, queryset=BuildHistory.objects.all().select_related('builder_name').order_by('-time_start')).qs

    paginated_builds = Paginator(builds, 100)
    try:
        result = paginated_builds.get_page(page)
    except PageNotAnInteger:
        result = paginated_builds.get_page(1)
    except EmptyPage:
        result = paginated_builds.get_page(paginated_builds.num_pages)

    return render(request, 'ports/ajax-filters/builds_filtered_table.html', {
        'builds': result,
        'builder': builder,
        'status': status,
        'port_name': port_name,
    })


def stats(request):
    current_week = datetime.datetime.today().isocalendar()[1]
    all_submissions = User.objects.all()
    total_unique_users = all_submissions.distinct('uuid').count()
    current_week_unique = all_submissions.filter(updated_at__week=current_week).distinct('uuid').count()
    last_week_unique = all_submissions.filter(updated_at__week=current_week - 1).distinct('uuid').count()

    os_dict = {}
    for os_obj in OSDistribution.objects.filter(month=datetime.datetime.now().month, year=datetime.datetime.now().year):
        os_dict[os_obj.osx_version] = os_obj.users.distinct('uuid').count()

    return render(request, 'ports/stats.html', {
        'total_submissions': all_submissions.count(),
        'unique_users': total_unique_users,
        'current_week': current_week_unique,
        'last_week': last_week_unique,
        'os_dict': os_dict
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
    query = request.GET.get('search_text', '')
    search_by = request.GET.get('search_by', '')
    ports = PortFilterByMultiple(request.GET, queryset=Port.objects.all()).qs[:50]

    return render(request, 'ports/ajax-filters/filtered_table.html', {
        'ports': ports,
        'query': query,
        'search_by': search_by
    })


# Respond to ajax call for loading tickets
def tickets(request):
    port_name = request.GET.get('port_name')
    URL = "https://trac.macports.org/query?status=!closed&port=~{}".format(port_name)
    response = requests.get(URL)
    Soup = BeautifulSoup(response.content, 'html5lib')
    all_tickets = []
    for row in Soup.findAll('tr', attrs={'class': 'prio2'}):
        srow = row.find('td', attrs={'class': 'summary'})
        idrow = row.find('td', attrs={'class': 'id'})
        typerow = row.find('td', attrs={'class': 'type'})
        ticket = {}
        ticket['url'] = srow.a['href']
        ticket['title'] = srow.a.text
        ticket['id'] = idrow.a.text
        ticket['type'] = typerow.text
        all_tickets.append(ticket)

    return render(request, 'ports/ajax-filters/tickets.html', {
        'portname': port_name,
        'tickets': all_tickets,
    })


# Respond to ajax calls for searching within a category
def search_ports_in_category(request):
    query = request.GET.get('name')
    search_in = request.GET.get('categories__name')

    filtered_ports = PortFilterByMultiple(request.GET, queryset=Port.objects.all()).qs[:50]
    return render(request, 'ports/ajax-filters/filtered_table.html', {
        'ports': filtered_ports,
        'query': query,
        'search_in': search_in,
        'content': "Category"
    })


# Respond to ajax calls for searching within a maintainer
def search_ports_in_maintainer(request):
    query = request.GET.get('name', '')
    search_in = request.GET.get('maintainers__name', '')

    filtered_ports = PortFilterByMultiple(request.GET, queryset=Port.objects.all()).qs[:50]
    return render(request, 'ports/ajax-filters/filtered_table.html', {
        'ports': filtered_ports,
        'query': query,
        'search_in': search_in,
        'content': "Maintainer"
    })


def search_ports_in_variant(request):
    query = request.GET.get('name', '')
    search_in = request.GET.get('variant', '')

    filtered_ports = Variant.objects.filter(variant=search_in, port__name__icontains=query)
    return render(request, 'ports/ajax-filters/filtered_table.html', {
        'ports': filtered_ports,
        'query': query,
        'search_in': search_in,
        'content': "Variant"
    })


@csrf_exempt
def stats_submit(request):
    if request.method == "POST":
        try:
            received_json = json.loads(request.POST.get('submission[data]'))

            Submission.populate(received_json)
            PortInstallation.populate(received_json['active_json'])

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
