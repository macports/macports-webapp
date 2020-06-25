from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.functions import Lower

from port.models import Port


def get_my_ports_context(request, using):
    user = request.user
    emails = EmailAddress.objects.filter(user=user, verified=True).values_list('email', flat=True)
    github = SocialAccount.objects.filter(user=user).values_list('extra_data', flat=True)

    handles, ports_github = get_ports_by_github(github)
    ports_email = get_ports_by_email(emails)

    requested = ports_email.order_by(Lower('name')).select_related('livecheck') if using == 'email' else ports_github.order_by(Lower('name')).select_related('livecheck')

    paginated_ports = Paginator(requested, 100)
    page = request.GET.get('page', 1)
    try:
        ports = paginated_ports.get_page(page)
    except PageNotAnInteger:
        ports = paginated_ports.get_page(1)
    except EmptyPage:
        ports = paginated_ports.get_page(paginated_ports.num_pages)

    return handles, emails, ports_github.count(), ports_email.count(), ports


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
