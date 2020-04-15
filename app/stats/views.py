import json
import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Subquery, Count, Case, IntegerField, When, Q
from django.db.models.functions import TruncMonth, Lower

from stats.models import Submission, PortInstallation
from stats.validators import validate_stats_days, validate_columns_port_installations, validate_unique_columns_port_installations, ALLOWED_DAYS_FOR_STATS
from stats.utilities.sort_by_version import sort_list_of_dicts_by_version


def stats(request):
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

    current_week = datetime.datetime.today().isocalendar()[1]
    all_submissions = Submission.objects.all()
    total_unique_users = all_submissions.distinct('user').count()
    current_week_unique = all_submissions.filter(timestamp__week=current_week).distinct('user').count()
    last_week_unique = all_submissions.filter(timestamp__week=current_week - 1).distinct('user').count()

    # Number of unique users vs month
    users_by_month = Submission.objects.annotate(month=TruncMonth('timestamp')).values('month').annotate(num=Count('user_id', distinct=True))[:12]

    # System Stats for Current Users
    submissions_last_x_days = Submission.objects.filter(timestamp__range=[start_date, end_date]).order_by('user', '-timestamp').distinct('user')
    submissions_unique = Submission.objects.filter(id__in=Subquery(submissions_last_x_days.values('id')))
    macports_version = sort_list_of_dicts_by_version(list(submissions_unique.values('macports_version').annotate(num=Count('macports_version'))), 'macports_version')
    os_version_and_clt_version = sort_list_of_dicts_by_version(list(submissions_unique.values('clt_version', 'os_version').annotate(num=Count('user_id', distinct=True))), 'os_version')
    os_version_build_arch_and_stdlib = sort_list_of_dicts_by_version(list(submissions_unique.values('os_version', 'build_arch', 'cxx_stdlib').annotate(num=Count('user_id', distinct=True))), 'os_version')
    os_version_and_xcode_version = sort_list_of_dicts_by_version(list(submissions_unique.values('xcode_version', 'os_version').annotate(num=Count('user_id', distinct=True))), 'os_version')

    return render(request, 'stats/stats.html', {
        'total_submissions': all_submissions.count(),
        'unique_users': total_unique_users,
        'current_week': current_week_unique,
        'last_week': last_week_unique,
        'users_by_month': users_by_month,
        'os_version_build_arch_and_stdlib': os_version_build_arch_and_stdlib,
        'macports_version': macports_version,
        'os_version_and_xcode_version': os_version_and_xcode_version,
        'os_version_and_clt_version': os_version_and_clt_version,
        'days': days,
        'days_ago': days_ago,
        'start_date': start_date,
        'end_date': end_date,
        'users_count_in_duration': submissions_last_x_days.count(),
        'allowed_days': ALLOWED_DAYS_FOR_STATS
    })


def stats_port_installations(request):
    days = request.GET.get('days', 30)
    first = str(request.GET.get('first', '-total_count'))
    second = str(request.GET.get('second', '-req_count'))
    third = str(request.GET.get('third', 'port'))
    columns = [first, second, third]

    # Validate days
    check, message = validate_stats_days(days)
    if check is False:
        return HttpResponse(message)

    # Validate columns
    check, message = validate_columns_port_installations(columns)
    if check is False:
        return HttpResponse(message)

    # Validate unique columns
    check, message = validate_unique_columns_port_installations(columns)
    if check is False:
        return HttpResponse(message)

    return render(request, 'stats/stats_port_installations.html', {
        'days': int(days),
        'first': first,
        'second': second,
        'third': third,
        'allowed_days': ALLOWED_DAYS_FOR_STATS
    })


def stats_port_installations_filter(request):
    days = request.GET.get('days', 30)
    order_by_1 = str(request.GET.get('order_by_1', '-total_count'))
    order_by_2 = str(request.GET.get('order_by_2', '-req_count'))
    order_by_3 = str(request.GET.get('order_by_3', 'port'))
    search_by = str(request.GET.get('search_by', ''))
    columns = [order_by_1, order_by_2, order_by_3]

    # Validate days
    check, message = validate_stats_days(days)
    if check is False:
        return HttpResponse(message)

    # Validate columns
    check, message = validate_columns_port_installations(columns)
    if check is False:
        return HttpResponse(message)

    # Validate unique columns
    check, message = validate_unique_columns_port_installations(columns)
    if check is False:
        return HttpResponse(message)

    days = int(days)

    submissions_unique = Submission.objects.filter(timestamp__gte=datetime.datetime.now(tz=datetime.timezone.utc)-datetime.timedelta(days=days)).order_by('user', '-timestamp').distinct('user')
    installations = PortInstallation.objects.order_by('port')\
        .filter(submission_id__in=Subquery(submissions_unique.values('id')))\
        .values('port').annotate(total_count=Count('port'))\
        .annotate(req_count=Count(Case(When(requested=True, then=1), output_field=IntegerField())))\
        .exclude(port__icontains='mpstats')\
        .filter(port__icontains=search_by)\
        .extra(select={'port': 'lower(port)'})\
        .order_by(order_by_1, order_by_2, order_by_3)

    paginated_obj = Paginator(installations, 100)
    page = request.GET.get('page', 1)
    try:
        installs = paginated_obj.get_page(page)
    except PageNotAnInteger:
        installs = paginated_obj.get_page(1)
    except EmptyPage:
        installs = paginated_obj.get_page(paginated_obj.num_pages)

    return render(request, 'stats/port_installations_table.html', {
        'installs': installs,
        'search_by': search_by
    })


def stats_faq(request):
    return render(request, 'stats/stats_faq.html')


@csrf_exempt
def stats_submit(request):
    if request.method == "POST":
        try:
            received_body = request.body.decode()
            prefix = 'submission[data]='
            if not received_body.startswith(prefix):
                return HttpResponse("Invalid body of the request.")

            received_json = json.loads(received_body[len(prefix):], encoding='utf-8')
            submission_id = Submission.populate(received_json, datetime.datetime.now(tz=datetime.timezone.utc))
            PortInstallation.populate(received_json['active_ports'], submission_id)

            return HttpResponse("Success")

        except:
            return HttpResponse("Something went wrong")
    else:
        return HttpResponse("Method Not Allowed")
