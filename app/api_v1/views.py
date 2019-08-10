import datetime
import json
from distutils.version import LooseVersion

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Subquery, Count
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.functions import TruncMonth
from django.core.serializers.json import DjangoJSONEncoder

from ports.models import Port, BuildHistory, Builder, Submission, PortInstallation
from .serializers import PortSerializer, BuildHistorySerializer, PortNameSerializer
from ports.validators import validate_stats_days, validate_int
from ports.utilities.sort_by_version import sort_list_of_dicts_by_version
from ports.filters import PortFilterByMultiple, BuildHistoryFilter

ERROR405 = {
    'message': 'Method Not Allowed',
    'status_code': 405
}


@csrf_exempt
def api_port_info(request, name):
    if request.method == 'GET':
        try:
            fields = request.GET.get('fields')
            port = Port.objects.get(name__iexact=name)
            serializer = PortSerializer(port, context={'request': request}, fields=fields)
            return JsonResponse(serializer.data, safe=False)
        except Port.DoesNotExist:
            response = dict()
            response['message'] = "Requested port does not exist"
            response['status_code'] = 404
            return JsonResponse(response)
    else:
        return JsonResponse(ERROR405)


def api_port_builds(request, name):
    if request.method == 'GET':
        count = request.GET.get('count', 100)
        builder = request.GET.get('builder')
        status = request.GET.get('status')

        builds = BuildHistory.objects.filter(port_name__iexact=name).order_by('-time_start')[:count]

        if not builds.count() > 0:
            return JsonResponse({
                "message": "No builds found for {}".format(name),
                "status_code": 200
            })

        if builder is not None:
            builds.filter(builder_name__name=builder)
        if status is not None:
            builds.filter(status=status)

        serializer = BuildHistorySerializer(builds, many=True)

        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse(ERROR405)


def api_port_health(request, name):
    if request.method == 'GET':

        try:
            port = Port.objects.get(name__iexact=name)
        except Port.DoesNotExist:
            return JsonResponse({
                "message": "The port {} does not exist.".format(name),
                "status_code": 404
            })

        all_latest_builds = BuildHistory.objects.all()\
            .order_by('port_name', 'builder_name', '-build_id')\
            .distinct('port_name', 'builder_name')

        port_latest_builds = list(BuildHistory.objects.filter(id__in=Subquery(all_latest_builds.values('id')), port_name__iexact=name)
                                  .values('builder_name__name', 'build_id', 'status'))

        builders = list(Builder.objects.all().values_list('name', flat=True))

        if len(port_latest_builds) == 0:
            return JsonResponse({
                "message": "No builds found for {}.".format(name),
                "status_code": 200
            })
        builders.sort(key=LooseVersion, reverse=True)

        return JsonResponse(port_latest_builds, safe=False)
    else:
        return JsonResponse(ERROR405)


def api_port_stats(request, name):
    if not request.method == 'GET':
        return JsonResponse(ERROR405)

    try:
        port = Port.objects.get(name__iexact=name)
    except Port.DoesNotExist:
        return JsonResponse({
            "message": "The port {} does not exist.".format(name),
            "status_code": 404
        })

    days = request.GET.get('days', 30)
    days_ago = request.GET.get('days_ago', 0)
    criteria = request.GET.get('criteria', 'total_count,req_count,os_versions,xcode_versions,installs_count_monthly,versions_count_monthly').split(',')

    # Validate days and days_ago
    for value in days, days_ago:
        check, message = validate_stats_days(value)
        if check is False:
            return JsonResponse({
                "message": message,
                "status_code": 200
            })

    days = int(days)
    days_ago = int(days_ago)

    end_date = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=days_ago)
    start_date = end_date - datetime.timedelta(days=days)

    submissions = Submission.objects.filter(timestamp__range=[start_date, end_date]).order_by('user','-timestamp').distinct('user')
    port_installations = PortInstallation.objects.filter(submission_id__in=Subquery(submissions.values('id')), port__iexact=name)

    json_response = dict()

    if 'total_count' in criteria:
        total_port_installations_count = port_installations.aggregate(Count('submission__user_id', distinct=True))
        json_response['total_count'] = total_port_installations_count['submission__user_id__count']

    if 'req_count' in criteria:
        requested_port_installations_count = port_installations.filter(requested=True).aggregate(Count('submission__user_id', distinct=True))
        json_response['req_count'] = requested_port_installations_count['submission__user_id__count']

    if 'port_versions' in criteria:
        port_installations_by_port_version = port_installations.values('version').annotate(num=Count('version')).order_by('-num')
        json_response['port_versions'] = json.dumps(list(port_installations_by_port_version), cls=DjangoJSONEncoder)

    if 'os_versions' in criteria:
        port_installations_by_os_stdlib_build_arch = sort_list_of_dicts_by_version(list(port_installations.values('submission__os_version', 'submission__build_arch', 'submission__cxx_stdlib').annotate(num=Count('submission__user_id', distinct=True))), 'submission__os_version')
        json_response['os_versions'] = json.dumps(port_installations_by_os_stdlib_build_arch, cls=DjangoJSONEncoder)

    if 'xcode_versions' in criteria:
        port_installations_by_os_and_xcode_version = sort_list_of_dicts_by_version(list(port_installations.values('submission__xcode_version', 'submission__os_version').annotate(num=Count('submission__user_id', distinct=True))), 'submission__os_version')
        json_response['xcode_versions'] = json.dumps(port_installations_by_os_and_xcode_version, cls=DjangoJSONEncoder)

    if 'installs_count_monthly' in criteria:
        port_installations_by_month = PortInstallation.objects.filter(port__iexact=name).annotate(month=TruncMonth('submission__timestamp')).values('month').annotate(num=Count('submission__user', distinct=True))[:12]
        json_response['installs_count_monthly'] = json.dumps(list(port_installations_by_month), cls=DjangoJSONEncoder)

    if 'versions_count_monthly' in criteria:
        port_installations_by_version_and_month = PortInstallation.objects.filter(port__iexact=name).annotate(month=TruncMonth('submission__timestamp')).values('month', 'version').annotate(num=Count('submission__user', distinct=True))[:12]
        json_response['versions_count_monthly'] = json.dumps(list(port_installations_by_version_and_month), cls=DjangoJSONEncoder)

    return JsonResponse(json_response)


def api_ports_filter(request):
    if not request.method == 'GET':
        return JsonResponse(ERROR405)
    icontains = request.GET.get('icontains')
    category = request.GET.get('category')
    description = request.GET.get('description')
    maintainer_github = request.GET.get('maintainer_github')
    maintainer_name = request.GET.get('maintainer_name')
    info = request.GET.get('info', False)
    only_count = request.GET.get('only_count', False)

    ports = PortFilterByMultiple({
        'name': icontains,
        'categories__name': category,
        'description': description,
        'maintainers__github': maintainer_github,
        'maintainers__name': maintainer_name
    }, queryset=Port.objects.all()).qs

    if only_count == 'True':
        return JsonResponse({
            "count": ports.count()
        })

    if info == 'True':
        serializer = PortSerializer(ports, many=True)
    else:
        ports = ports.values('name')
        serializer = PortNameSerializer(ports, many=True)

    json_response = {
        "ports": serializer.data,
        "count": ports.count()
    }
    return JsonResponse(json_response, safe=False)


def api_builds_filter(request):
    count = request.GET.get('count', 1000)
    check, message = validate_int(count)
    if check is False:
        return JsonResponse({
            "message": message,
            "status_code": 200
        })

    page = request.GET.get('page', 1)
    paginate_by = request.GET.get('paginate_by', count)
    for i in page, paginate_by:
        check, message = validate_int(i)
        if check is False:
            return JsonResponse({
                "message": message,
                "status_code": 200
            })

    count = int(count)
    page = int(page)
    paginate_by = int(paginate_by)
    status = request.GET.get('status')
    builder = request.GET.get('builder')
    port_name = request.GET.get('port_name')

    builds = BuildHistoryFilter({
        'status': status,
        'port_name': port_name,
        'builder_name__name': builder
    }, BuildHistory.objects.all().select_related('builder_name')).qs[:count]

    paginated_builds = Paginator(builds, paginate_by)
    try:
        builds_on_page = paginated_builds.get_page(page)
    except PageNotAnInteger:
        builds_on_page = paginated_builds.get_page(1)
    except EmptyPage:
        builds_on_page = paginated_builds.get_page(paginated_builds.num_pages)

    serializer = BuildHistorySerializer(builds_on_page, many=True)

    return JsonResponse(serializer.data, safe=False)



