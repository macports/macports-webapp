from stats.models import Submission
from build.models import BuildHistory
from port.models import LastPortIndexUpdate


def footer_processor(request):
    response = dict()
    try:
        obj = LastPortIndexUpdate.objects.all().first()
        port_info_updated_till_commit = obj.git_commit_hash
        port_info_updated_at = obj.updated_at
        response['port_info_updated_till_commit'] = port_info_updated_till_commit
        response['port_info_updated_at'] = port_info_updated_at
    except AttributeError:
        pass
    try:
        latest_submission_made_at = Submission.objects.all().order_by('-timestamp').first().timestamp
        response['latest_submission_made_at'] = latest_submission_made_at
    except AttributeError:
        pass
    try:
        latest_build_fetched_at = BuildHistory.objects.all().order_by('-time_start').first().time_start
        response['latest_build_fetched_at'] = latest_build_fetched_at
    except AttributeError:
        pass
    return response
