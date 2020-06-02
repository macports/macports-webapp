import datetime

from rest_framework import serializers
from django.db.models import Count, Subquery, Value, CharField
from django.db.models.functions import TruncMonth, Cast, ExtractMonth, ExtractYear, Concat

from stats.models import PortInstallation
from stats.models import Submission
from stats.utilities.sort_by_version import sort_list_of_dicts_by_version
from stats.validators import ALLOWED_DAYS_FOR_STATS as ALLOWED_DAYS
from stats.validators import ALLOWED_PROPERTIES


class PortStatisticsSerializer(serializers.Serializer):
    result = serializers.SerializerMethodField()

    sort_by = None
    days = None
    days_ago = None
    properties = []
    port_name = None

    class Meta:
        fields = ('property', 'result')

    def validate_context(self):
        days = self.context.get('days', '30')
        days_ago = self.context.get('days_ago', '0')
        if (not days.isnumeric()) or (not days_ago.isnumeric()):
            return False

        days = int(days)
        days_ago = int(days_ago)

        if (days not in ALLOWED_DAYS) or (days_ago not in ALLOWED_DAYS):
            return False

        self.days = int(days)
        self.days_ago = int(days_ago)
        return self.validate_properties()

    def validate_properties(self):
        properties = self.context.get('property')
        for p in properties:
            if p not in ALLOWED_PROPERTIES:
                return False
        self.properties = properties
        return self.validate_port()

    def validate_sorting(self):
        sort_by = self.context.get('sort_by')
        if sort_by == "" or sort_by is None:
            return
        if sort_by == "variants" or sort_by == "requested":
            return
        if sort_by not in ALLOWED_PROPERTIES or sort_by not in self.properties:
            return
        self.sort_by = sort_by
        return

    def validate_port(self):
        port_name = self.context.get('name')
        if port_name is None or port_name == "":
            return False
        self.port_name = port_name
        return True

    def generate_time_range_query(self):
        is_valid = self.validate_context()
        if not is_valid:
            return PortInstallation.objects.none()

        end_date = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=self.days_ago)
        start_date = end_date - datetime.timedelta(days=self.days)
        submissions = Submission.objects.defer('raw_json').filter(timestamp__range=[start_date, end_date]).order_by('user', '-timestamp').distinct('user')
        port_installations = PortInstallation.objects\
            .filter(
                submission_id__in=Subquery(submissions.values('id')),
                port__iexact=self.port_name
            )\
            .select_related('submission')\
            .only(
                'submission__user_id',
            )
        return port_installations

    def get_result(self, obj):
        result = self.generate_time_range_query().values(*self.properties).annotate(count=Count('submission__user_id'))
        self.validate_sorting()
        if self.sort_by:
            result = sort_list_of_dicts_by_version(list(result), self.sort_by)
        return result



class PortMonthlyInstallationsSerializer(serializers.Serializer):
    result = serializers.SerializerMethodField()

    port_name = None

    class Meta:
        fields = ('result', )

    def validate_context(self):
        port_name = self.context.get('name')
        if port_name == "" or port_name is None:
            return False
        self.port_name = port_name
        return True

    def get_result(self, obj):
        is_valid = self.validate_context()
        if not is_valid:
            return PortInstallation.objects.none()
        today_day = datetime.datetime.now().day
        last_12_months = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=int(today_day) + 365)

        result = PortInstallation.objects \
            .select_related('submission') \
            .only('submission__user_id', 'submission__timestamp', 'port') \
            .filter(port__iexact=self.port_name, submission__timestamp__gte=last_12_months) \
            .annotate(datetime=TruncMonth('submission__timestamp')) \
            .order_by('datetime') \
            .annotate(
                m=Cast(ExtractMonth('datetime'), CharField()),
                y=Cast(ExtractYear('datetime'), CharField()),
                month=Concat('y', Value(','), 'm')
            ) \
            .values('month', 'version') \
            .annotate(count=Count('submission__user_id', distinct=True))

        return result
