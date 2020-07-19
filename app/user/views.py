from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator

from user.utilities import get_my_ports_context, get_followed_ports_context, get_ports_by_email, get_ports_by_github, paginate
from user.forms import MyPortsForm
from user.serializers import FollowedPortsSerializer


@login_required
def profile(request):
    usr = request.user

    usr_emails = EmailAddress.objects.filter(user=usr, verified=True).values_list('email', flat=True)
    usr_github = SocialAccount.objects.filter(user=usr).values_list('extra_data', flat=True)

    github, ports_by_github = get_ports_by_github(usr_github)
    ports_by_email = get_ports_by_email(usr_emails)

    return render(request, 'account/profile.html', {
        'followed_count': usr.ports.all().count(),
        'emails': usr_emails,
        'ports_by_emails_count': ports_by_email.count(),
        'github_handles': github,
        'ports_by_github_count': ports_by_github.count()
    })


@login_required
def my_ports_github(request):
    handles, emails, ports_github, ports_email, ports, builder = get_my_ports_context(request, 'GitHub')

    return render(request, 'account/my_ports.html', {
        'using': 'GitHub',
        'connections': handles,
        'ports_by_email_count': ports_email,
        'ports_by_github_count': ports_github,
        'ports': ports,
        'builder': builder,
        'form': MyPortsForm(request.GET)
    })


@login_required
def my_ports_email(request):
    handles, emails, ports_github, ports_email, ports, builder = get_my_ports_context(request, 'email')

    return render(request, 'account/my_ports.html', {
        'using': 'email',
        'connections': emails,
        'ports_by_email_count': ports_email,
        'ports_by_github_count': ports_github,
        'ports': ports,
        'builder': builder,
        'form': MyPortsForm(request.GET)
    })


@login_required
def followed_ports(request):
    ports, builder = get_followed_ports_context(request)

    return render(request, 'account/followed_ports.html', {
        'ports': ports,
        'builder': builder,
        'form': MyPortsForm(request.GET)
    })


@login_required
def notifications_all(request):
    usr = request.user
    notifications_all_items = usr.notifications.all()

    # paginate the notifications
    notifications = paginate(request, notifications_all_items, 100)

    return render(request, 'account/notifications.html', {
        'notifications': notifications,
    })


class FollowedPortsAPIView(APIView):
    def get(self, request):
        usr = request.user
        if not usr.is_authenticated:
            return Response([])
        result = FollowedPortsSerializer(
            User.objects.all(),
            context={
                'user': request.user
            }
        )
        return Response(result.data)
