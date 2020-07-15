from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Subquery, OuterRef, Q
from django.db.models.functions import Lower

from port.models import Port
from buildhistory.models import BuildHistory, Builder


def get_my_ports_context(request, using):
    user = request.user
    builder = request.GET.get('builder', Builder.objects.first().name)
    emails = EmailAddress.objects.filter(user=user, verified=True).values_list('email', flat=True)
    github = SocialAccount.objects.filter(user=user).values_list('extra_data', flat=True)

    handles, ports_github = get_ports_by_github(github)
    ports_email = get_ports_by_email(emails)

    # Determine if the current request is made for fetching ports using Github or emails.
    # Then supply the requested ports to req_ports
    req_ports = ports_email if using == 'email' else ports_github
    ports = get_ports_context(request, req_ports, builder)

    return handles, emails, ports_github.count(), ports_email.count(), ports, builder


def get_followed_ports_context(request):
    user = request.user
    builder = request.GET.get('builder', Builder.objects.first().name)

    ports = get_ports_context(request, user.ports, builder)

    return ports, builder


def get_ports_context(request, req_ports, builder):
    builds = BuildHistory.objects.filter(port_name=OuterRef('name'), builder_name__name=builder).order_by('time_start')
    req_ports = req_ports.order_by(Lower('name')).select_related('livecheck').annotate(build=Subquery(builds.values_list('status')[:1]))
    req_ports = apply_filters(request, req_ports)

    # Paginate the req_ports
    ports = paginate(request, req_ports, 100)

    return ports


def get_ports_by_email(emails_list):
    ports_connected = Port.objects.none()
    for i in emails_list:
        try:
            name = i.split('@')[0]
            domain = i.split('@')[1]
            ports_connected = ports_connected | Port.objects.filter(maintainers__name__iexact=name,
                                                                    maintainers__domain__iexact=domain)
        except KeyError:
            continue
    return ports_connected


def get_ports_by_github(github_list):
    ports_connected = Port.objects.none()
    handles = []
    for i in github_list:
        try:
            handle = i['login']
        except KeyError:
            continue
        handles.append(handle)
        ports_connected = ports_connected | Port.objects.filter(maintainers__github__iexact=handle)
    return handles, ports_connected


def apply_filters(request, ports):
    livecheck_outdated = request.GET.get('livecheck_outdated')
    livecheck_errored = request.GET.get('livecheck_errored')
    build_broken = request.GET.get('build_broken')
    build_ok = request.GET.get('build_ok')
    no_build = request.GET.get('no_build')
    hide_deleted = request.GET.get('hide_deleted')

    livecheck_filter = Q()

    # Do OR filtering among filters related to livecheck
    if livecheck_outdated:
        livecheck_filter = livecheck_filter | Q(livecheck__has_updates=True)

    if livecheck_errored:
        livecheck_filter = livecheck_filter | Q(livecheck__error__isnull=False)

    ports = ports.filter(livecheck_filter)

    # We perform AND filtering among the set of livecheck filters and build filters
    # However, inside a set there is OR filtering among various filters

    builds_filter = Q()
    # Do OR filtering among filters related to build history
    if build_broken:
        builds_filter = builds_filter | Q(build__contains="failed")

    if build_ok:
        builds_filter = builds_filter | Q(build="build successful")

    if no_build:
        builds_filter = builds_filter | Q(build__isnull=True)

    ports = ports.filter(builds_filter)

    if hide_deleted:
        ports = ports.filter(active=True)

    return ports


def paginate(request, items, paginate_by=100):
    paginated_items = Paginator(items, paginate_by)
    page = request.GET.get('page', 1)
    try:
        page_items = paginated_items.get_page(page)
    except PageNotAnInteger:
        page_items = paginated_items.get_page(1)
    except EmptyPage:
        page_items = paginated_items.get_page(paginated_items.num_pages)

    return page_items
