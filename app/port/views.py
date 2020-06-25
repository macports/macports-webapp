import datetime
import requests

from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Subquery, Count, Prefetch, Q
from django.contrib.postgres.aggregates import ArrayAgg
from rest_framework import mixins, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_haystack.viewsets import HaystackViewSet
from django.views.decorators.cache import cache_page

from port.forms import AdvancedSearchForm
from port.serializers import PortHaystackSerializer, PortSerializer
from port.models import Port, Dependency
from port.database import StringToArray
from buildhistory.models import BuildHistory, Builder
from stats.models import Submission, PortInstallation
from buildhistory.filters import BuildHistoryFilter
from stats.validators import validate_stats_days, ALLOWED_DAYS_FOR_STATS
from port.serializers import SearchSerializer


def port_detail(request, name):
    try:
        port = Port.objects.get(name__iexact=name)
    except Port.DoesNotExist:
        return render(request, 'port/exceptions/port_not_found.html', {'name': name})

    this_builds = BuildHistory.objects.filter(port_name__iexact=name).annotate(files_count=Count('files')).order_by('-time_start')
    builders = Builder.objects.all().prefetch_related(Prefetch('builds', queryset=this_builds, to_attr='latest_builds')).annotate(version_array=StringToArray('name'),).order_by('-version_array')
    dependents = Dependency.objects.filter(dependencies__id=port.id).values('type').annotate(ports=ArrayAgg('port_name__name'))

    last_30_days = datetime.datetime.now(tz=datetime.timezone.utc)-datetime.timedelta(days=30)
    submissions_last_30_days = Submission.objects.filter(timestamp__gte=last_30_days).order_by('user', '-timestamp').distinct('user')
    installations = PortInstallation.objects.filter(submission_id__in=Subquery(submissions_last_30_days.values('id')), port__iexact=port.name).select_related('submission').defer('submission__raw_json')
    count = installations.aggregate(requested=Count('submission__user_id', filter=Q(requested=True)), all=Count('submission__user_id'))
    return render(request, 'port/port_detail.html', {
        'port': port,
        'builders': builders,
        'dependents': dependents,
        'count': count
    })


def port_detail_build_information(request, name):
    try:
        port = Port.objects.get(name__iexact=name)
    except Port.DoesNotExist:
        return render(request, 'port/exceptions/port_not_found.html', {'name': name})

    status = request.GET.get('status', '')
    builder = request.GET.get('builder_name__display_name', '')
    page = request.GET.get('page', 1)
    builders = Builder.objects.all().annotate(version_array=StringToArray('name'),).order_by('-version_array')
    builds = BuildHistoryFilter(
        request.GET
    , queryset=BuildHistory.objects.filter(port_name__iexact=port.name).select_related('builder_name').order_by('-time_start')).qs
    paginated_builds = Paginator(builds, 100)
    try:
        result = paginated_builds.get_page(page)
    except PageNotAnInteger:
        result = paginated_builds.get_page(1)
    except EmptyPage:
        result = paginated_builds.get_page(paginated_builds.num_pages)

    return render(request, 'port/port_detail_builds.html', {
        'port': port,
        'builds': result,
        'builder': builder,
        'builders': builders,
        'status': status,
    })


def port_detail_stats(request, name):
    try:
        port = Port.objects.get(name__iexact=name)
    except Port.DoesNotExist:
        return render(request, 'port/exceptions/port_not_found.html', {'name': name})

    days = request.GET.get('days', 30)
    days_ago = request.GET.get('days_ago', 0)

    # Validate days and days_ago
    for value in days, days_ago:
        check, message = validate_stats_days(value)
        if check is False:
            return HttpResponse(message)
    days = int(days)
    days_ago = int(days_ago)

    end_date = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=days_ago)
    start_date = end_date - datetime.timedelta(days=days)

    # Section for calculation of current stats
    submissions = Submission.objects.filter(timestamp__range=[start_date, end_date]).order_by('user', '-timestamp').distinct('user')
    port_installations = PortInstallation.objects.filter(submission_id__in=Subquery(submissions.values('id')), port__iexact=name)
    count = port_installations.aggregate(requested=Count('submission__user_id', filter=Q(requested=True)), all=Count('submission__user_id'))

    return render(request, 'port/port_detail_stats.html', {
        'count': count,
        'days': days,
        'days_ago': days_ago,
        'end_date': end_date,
        'start_date': start_date,
        'users_in_duration_count': submissions.count(),
        'allowed_days': ALLOWED_DAYS_FOR_STATS,
        'port': port
    })


# Respond to ajax call for loading tickets
# Tickets are fetched from trac.macports.org, to prevent multiple hits to trac, tickets
# should be cached. The can tolerate caching for an hour easily
@cache_page(60 * 60)
def port_detail_tickets(request, name):
    port_name = request.GET.get('port_name')
    URL = "https://trac.macports.org/report/16?max=1000&PORT=(%5E%7C%5Cs){}($%7C%5Cs)".format(port_name)
    response = requests.get(URL)
    Soup = BeautifulSoup(response.content, 'html5lib')
    all_tickets = []
    for row in Soup.findAll('tr', attrs={'class': ['color2-even', 'color2-odd', 'color1-even', 'color1-odd']}):
        srow = row.find('td', attrs={'class': 'summary'})
        idrow = row.find('td', attrs={'class': 'ticket'})
        typerow = row.find('td', attrs={'class': 'type'})
        ticket = {'url': srow.a['href'], 'title': srow.a.text, 'id': idrow.a.text, 'type': typerow.text}
        all_tickets.append(ticket)
    all_tickets = sorted(all_tickets, key=lambda x: x['id'], reverse=True)

    return render(request, 'port/port_detail_tickets.html', {
        'portname': port_name,
        'tickets': all_tickets,
    })


# VIEWS FOR DJANGO REST-FRAMEWORK


class PortAutocompleteView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PortHaystackSerializer
    form = None
    # We use the same form as used by the advanced search.
    # AdvancedSearchForm takes care of filtering the queryset itself.
    form_class = AdvancedSearchForm

    def build_form(self):
        data = self.request.GET
        return self.form_class(data, None)

    def get_queryset(self, *args, **kwargs):
        self.form = self.build_form()
        return self.form.search()


class PortAPIView(viewsets.ReadOnlyModelViewSet):
    serializer_class = PortSerializer
    queryset = Port.objects.all()
    lookup_field = 'name__iexact'
    lookup_value_regex = '[a-zA-Z0-9_.-]+'
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'maintainers__github', 'variants__variant', 'categories__name']
    filterset_fields = ['name', 'categories', 'maintainers__github', 'variants__variant']


class SearchAPIView(HaystackViewSet):
    index_models = [Port]

    serializer_class = SearchSerializer
