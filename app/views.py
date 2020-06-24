import datetime

from django.shortcuts import render
from django.db.models import Subquery, Count

from port.models import Port
from stats.models import Submission, PortInstallation
from port.filters import PortFilterByMultiple


def index(request):
    ports_count = Port.objects.filter(active=True).count()
    submissions_unique = Submission.objects.filter(timestamp__gte=datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=30)).order_by('user', '-timestamp').distinct('user')
    top_ports = PortInstallation.objects.filter(submission_id__in=Subquery(submissions_unique.values('id')), requested=True).exclude(port__icontains='mpstats').values('port').annotate(num=Count('port')).order_by('-num')[:10]

    return render(request, 'index.html', {
        'top_ports': top_ports,
        'ports_count': ports_count
    })


# Respond to ajax-call triggered by the search box
def search(request):
    query = request.GET.get('search_text', '')
    search_by = request.GET.get('search_by', '')
    ports = PortFilterByMultiple(request.GET, queryset=Port.get_active.all()).qs[:50]

    return render(request, 'filtered_table.html', {
        'ports': ports,
        'query': query,
        'search_by': search_by
    })


def about_page(request):
    return render(request, 'about.html')
