from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from user.utilities import get_my_ports_context


def profile(request):
    return render(request, 'account/profile.html')


@login_required
def my_ports_github(request):
    handles, emails, ports_github, ports_email, ports = get_my_ports_context(request, 'GitHub')

    return render(request, 'account/my_ports.html', {
        'using': 'GitHub',
        'connections': handles,
        'ports_by_email_count': ports_email,
        'ports_by_github_count': ports_github,
        'ports': ports
    })


@login_required
def my_ports_email(request):
    handles, emails, ports_github, ports_email, ports = get_my_ports_context(request, 'email')

    return render(request, 'account/my_ports.html', {
        'using': 'email',
        'connections': emails,
        'ports_by_email_count': ports_email,
        'ports_by_github_count': ports_github,
        'ports': ports
    })
