import datetime
from distutils.version import LooseVersion

from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Subquery, Count, Case, IntegerField, When, Q
from django.db.models.functions import TruncMonth, Lower

from port_detail.models import Port, Maintainer, Dependency, Variant
from ports.models import BuildHistory, Builder, Submission, PortInstallation
from ports.filters import BuildHistoryFilter
from ports.validators import validate_stats_days, ALLOWED_DAYS_FOR_STATS
from ports.utilities.sort_by_version import sort_list_of_dicts_by_version


def port_detail(request, name, slug="summary"):
    try:
        req_port = Port.objects.get(name__iexact=name)
        days = request.GET.get('days', 30)
        days_ago = request.GET.get('days_ago', 0)
        tab = str(slug)
        allowed_tabs = ["summary", "builds", "stats", "tickets"]
        if tab not in allowed_tabs:
            return HttpResponse("Invalid tab requested. Expected values: {}".format(allowed_tabs))

        all_latest_builds = BuildHistory.objects.all().order_by('port_name', 'builder_name__display_name', '-time_start').distinct('port_name', 'builder_name__display_name')
        port_latest_builds = list(BuildHistory.objects.filter(id__in=Subquery(all_latest_builds.values('id')), port_name__iexact=name).values('builder_name__name', 'builder_name__display_name', 'build_id', 'status'))

        builders = list(Builder.objects.all().order_by('display_name').distinct('display_name').values_list('display_name', flat=True))

        builders.sort(key=LooseVersion, reverse=True)
        latest_builds = {}
        for builder in builders:
            latest_builds[builder] = next((item for item in port_latest_builds if item['builder_name__display_name'] == builder), False)
        return render(request, 'port_detail/port_detail_parent.html', {
            'req_port': req_port,
            'latest_builds': latest_builds,
            'tab': tab,
            'days': days,
            'days_ago': days_ago,
        })
    except Port.DoesNotExist:
        return render(request, 'port_detail/exceptions/port_not_found.html', {
            'name': name
        })


def port_detail_summary(request):
    try:
        port_name = request.GET.get('port_name')
        port = Port.objects.get(name=port_name)
        port_id = port.id
        maintainers = Maintainer.objects.filter(ports__name=port_name)
        dependencies = Dependency.objects.filter(port_name_id=port_id)
        dependents = Dependency.objects.filter(dependencies__name__iexact=port_name).select_related('port_name').order_by(Lower('port_name__name'))
        variants = Variant.objects.filter(port_id=port_id).order_by(Lower('variant'))

        submissions_last_30_days = Submission.objects.filter(timestamp__gte=datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=30)).order_by('user', '-timestamp').distinct('user')
        requested_count = PortInstallation.objects.filter(submission_id__in=Subquery(submissions_last_30_days.values('id')), requested=True, port__iexact=port_name).values('port').aggregate(Count('port'))
        total_count = PortInstallation.objects.filter(submission_id__in=Subquery(submissions_last_30_days.values('id')), port__iexact=port_name).values('port').aggregate(Count('port'))

        return render(request, 'port_detail/port_detail_summary.html', {
            'port': port,
            'maintainers': maintainers,
            'dependencies': dependencies,
            'dependents': dependents,
            'variants': variants,
            'requested_count': requested_count,
            'total_count': total_count
        })
    except Port.DoesNotExist:
        return HttpResponse("Visit /port/port-name/ if you are looking for ports.")


def port_detail_build_information(request):
    status = request.GET.get('status', '')
    builder = request.GET.get('builder_name__name', '')
    port_name = request.GET.get('port_name', '')
    page = request.GET.get('page', 1)
    builders = list(Builder.objects.all().order_by('display_name').distinct('display_name').values_list('display_name', flat=True))
    builders.sort(key=LooseVersion, reverse=True)
    builds = BuildHistoryFilter({
        'builder_name__display_name': builder,
        'status': status,
    }, queryset=BuildHistory.objects.filter(port_name__iexact=port_name).select_related('builder_name').order_by('-time_start')).qs
    paginated_builds = Paginator(builds, 100)
    try:
        result = paginated_builds.get_page(page)
    except PageNotAnInteger:
        result = paginated_builds.get_page(1)
    except EmptyPage:
        result = paginated_builds.get_page(paginated_builds.num_pages)

    return render(request, 'port_detail/port_detail_builds.html', {
        'builds': result,
        'builder': builder,
        'builders_list': builders,
        'status': status,
    })


def port_detail_stats(request):
    days = request.GET.get('days', 30)
    days_ago = request.GET.get('days_ago', 0)

    # Validate days and days_ago
    for value in days, days_ago:
        check, message = validate_stats_days(value)
        if check is False:
            return HttpResponse(message)

    port_name = request.GET.get('port_name')
    port = Port.objects.get(name__iexact=port_name)
    days = int(days)
    days_ago = int(days_ago)

    end_date = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=days_ago)
    start_date = end_date - datetime.timedelta(days=days)

    # Section for calculation of current stats
    submissions = Submission.objects.filter(timestamp__range=[start_date, end_date]).order_by('user', '-timestamp').distinct('user')
    port_installations = PortInstallation.objects.filter(submission_id__in=Subquery(submissions.values('id')), port__iexact=port_name)
    requested_port_installations_count = port_installations.filter(requested=True).aggregate(Count('submission__user_id', distinct=True))
    total_port_installations_count = port_installations.aggregate(Count('submission__user_id', distinct=True))
    port_installations_by_port_version = sort_list_of_dicts_by_version(list(port_installations.values('version').annotate(num=Count('version'))), 'version')
    port_installations_by_os_and_xcode_version = sort_list_of_dicts_by_version(list(port_installations.values('submission__xcode_version', 'submission__os_version').annotate(num=Count('submission__user_id', distinct=True))), 'submission__os_version')
    port_installations_by_os_and_clt_version = sort_list_of_dicts_by_version(list(port_installations.values('submission__clt_version', 'submission__os_version').annotate(num=Count('submission__user_id', distinct=True))), 'submission__os_version')
    port_installations_by_os_stdlib_build_arch = sort_list_of_dicts_by_version(list(port_installations.values('submission__os_version', 'submission__build_arch', 'submission__cxx_stdlib').annotate(num=Count('submission__user_id', distinct=True))), 'submission__os_version')
    port_installations_by_variants = port_installations.values('variants').annotate(num=Count('submission__user_id', distinct=True))
    port_installations_by_month = PortInstallation.objects.filter(port__iexact=port_name).annotate(month=TruncMonth('submission__timestamp')).values('month').annotate(num=Count('submission__user', distinct=True))[:12]
    port_installations_by_version_and_month = PortInstallation.objects.filter(port__iexact=port_name).annotate(month=TruncMonth('submission__timestamp')).values('month', 'version').annotate(num=Count('submission__user', distinct=True))[:12]

    return render(request, 'port_detail/port_detail_stats.html', {
        'requested_port_installations_count': requested_port_installations_count,
        'total_port_installations_count': total_port_installations_count,
        'port_installations_by_port_version': port_installations_by_port_version,
        'port_installations_by_os_and_xcode_version': port_installations_by_os_and_xcode_version,
        'port_installations_by_os_and_clt_version': port_installations_by_os_and_clt_version,
        'port_installations_by_month': port_installations_by_month,
        'port_installations_by_version_and_month': port_installations_by_version_and_month,
        'port_installations_by_os_stdlib_build_arch': port_installations_by_os_stdlib_build_arch,
        'port_installations_by_variants': port_installations_by_variants,
        'days': days,
        'days_ago': days_ago,
        'end_date': end_date,
        'start_date': start_date,
        'users_in_duration_count': submissions.count(),
        'allowed_days': ALLOWED_DAYS_FOR_STATS
    })
