import datetime

from django.db.models import Subquery, Count, Q

from stats.models import Submission, PortInstallation


def get_install_count(port_name, days):
    last_x_days = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=days)
    submissions_last_x_days = Submission.objects.filter(timestamp__gte=last_x_days).order_by('user', '-timestamp').distinct('user')
    installations = PortInstallation.objects.filter(submission_id__in=Subquery(submissions_last_x_days.values('id')),port__iexact=port_name).select_related('submission').defer('submission__raw_json')
    count = installations.aggregate(requested=Count('submission__user_id', filter=Q(requested=True)), all=Count('submission__user_id'))
    return count
