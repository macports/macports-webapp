import datetime

import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Subquery, Count, Q
from django.db.models.functions import Lower

from port_detail.models import Port, Category, Variant
from stats.models import Submission, PortInstallation
from port_detail.filters import PortFilterByMultiple


def index(request):
    categories = Category.objects.all().order_by('name').annotate(ports_count=Count('category', filter=Q(category__active=True)))
    submissions_unique = Submission.objects.filter(timestamp__gte=datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=30)).order_by('user', '-timestamp').distinct('user')
    top_ports = PortInstallation.objects.filter(submission_id__in=Subquery(submissions_unique.values('id')), requested=True).exclude(port__icontains='mpstats').values('port').annotate(num=Count('port')).order_by('-num')[:10]

    return render(request, 'ports/index.html', {
        'categories': categories,
        'top_ports': top_ports
    })


def about_page(request):
    return render(request, 'ports/about.html')


def categorylist(request, cat):
    try:
        category = Category.objects.get(name__iexact=cat)
        all_ports = Port.get_active.filter(categories__name=cat).order_by(Lower('name'))
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
    all_objects = Variant.objects.filter(variant=variant, port__active=True).select_related('port').order_by(Lower('port__name'))
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


# Respond to ajax-call triggered by the search box
def search(request):
    query = request.GET.get('search_text', '')
    search_by = request.GET.get('search_by', '')
    ports = PortFilterByMultiple(request.GET, queryset=Port.get_active.all()).qs[:50]

    return render(request, 'ports/ajax-filters/filtered_table.html', {
        'ports': ports,
        'query': query,
        'search_by': search_by
    })


# Respond to ajax calls for searching within a category
def search_ports_in_category(request):
    query = request.GET.get('name')
    search_in = request.GET.get('categories__name')

    filtered_ports = PortFilterByMultiple(request.GET, queryset=Port.get_active.all()).qs[:50]
    return render(request, 'ports/ajax-filters/filtered_table.html', {
        'ports': filtered_ports,
        'query': query,
        'search_in': search_in,
        'content': "Category"
    })


def search_ports_in_variant(request):
    query = request.GET.get('name', '')
    search_in = request.GET.get('variant', '')

    filtered_ports = Variant.objects.filter(variant=search_in, port__name__icontains=query, port__active=True)
    return render(request, 'ports/ajax-filters/filtered_table.html', {
        'ports': filtered_ports,
        'query': query,
        'search_in': search_in,
        'content': "Variant"
    })
