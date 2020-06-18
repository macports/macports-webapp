import json
import datetime

from django.test import TransactionTestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient

from tests import setup
from stats.models import Submission, PortInstallation, UUID
from port.models import Port
from config import TEST_SUBMISSION_JSON


def initial_data_setup():
    with open(TEST_SUBMISSION_JSON, 'r', encoding='utf-8') as file:
        data = json.loads(file.read())

    for i in data:
        submission_id = Submission.populate(i, datetime.datetime.now(tz=datetime.timezone.utc))
        PortInstallation.populate(i['active_ports'], submission_id)


QUICK_SUBMISSION_JSON = json.loads("""{
                    "id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXX6",
                    "os": {
                        "macports_version": "2.5.4",
                        "osx_version": "10.14",
                        "os_arch": "i386",
                        "os_platform": "darwin",
                        "cxx_stdlib": "libc++",
                        "build_arch": "x86_64",
                        "gcc_version": "none",
                        "prefix": "/opt/local",
                        "xcode_version": "10.3"
                    },
                    "active_ports": [
                        {"name": "port-A1", "version": "0.9"},
                        {"name": "port-A2", "version": "0.9.1"},
                        {"name": "port-B1", "version": "1.0"},
                        {"name": "port-C1", "version": "1.1.2"}
                    ]
                }""")


class TestURLsStats(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()

    def test_stats(self):
        response = self.client.get(reverse('stats'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='stats/stats.html')

    def test_port_installations(self):
        response = self.client.get(reverse('stats_port_installations'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='stats/stats_port_installations.html')

    def test_port_installations_filter(self):
        response = self.client.get(reverse('stats_port_installations_filter'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='stats/port_installations_table.html')

    def test_stats_faq(self):
        response = self.client.get(reverse('stats_faq'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='stats/stats_faq.html')


class TestStatsViews(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        # load stats
        initial_data_setup()

        # load data for ports
        setup.setup_test_data()

    def test_submission(self):
        submission_body = """submission[data]={
            "id": "974EEF9C-XXXX-XXXX-XXXX-XXXXXXXXXXX1",
            "os": {
                "macports_version": "2.5.4",
                "osx_version": "10.14",
                "os_arch": "i386",
                "os_platform": "darwin",
                "cxx_stdlib": "libc++",
                "build_arch": "x86_64",
                "gcc_version": "none",
                "prefix": "/opt/local",
                "xcode_version": "10.3"
            },
            "active_ports": [
                {"name": "db48", "version": "4.8.30_4"},
                {"name": "expat", "version": "2.2.6_1"},
                {"name": "ncurses", "version": "6.1_0"},
                {"name": "bzip2", "version": "1.0.6_0"},
                {"name": "mpstats-gsoc", "version": "0.1.8_2", "requested": "true"}
            ]
        }"""
        self.client.generic('POST', reverse('stats_submit'), submission_body)

        self.assertEquals(UUID.objects.count(), 6)
        self.assertEquals(Submission.objects.count(), 7)
        self.assertEquals(PortInstallation.objects.count(), 29)

    def test_port_installation_counts(self):
        response1 = self.client.get(reverse('port_stats', kwargs={
            'name': 'port-A1'
        }))

        self.assertEquals(response1.context['count']['all'], 4)
        self.assertEquals(response1.context['count']['requested'], 2)

    def test_time_travel(self):
        time_now = datetime.datetime.now(tz=datetime.timezone.utc)

        # Go back in time 35 days
        time_35_days_ago = time_now - datetime.timedelta(days=35)
        submission = QUICK_SUBMISSION_JSON

        # Make a submission dated 35 days ago
        submission_id = Submission.populate(submission, time_35_days_ago)
        PortInstallation.populate(submission['active_ports'], submission_id)

        # Call for stats between 30-60 days
        response1 = self.client.get(reverse('port_stats', kwargs={'name': 'port-B1'}), data={
            'days': 30,
            'days_ago': 30
        })

        # Call for stats between 30-37 days
        response2 = self.client.get(reverse('port_stats', kwargs={'name': 'port-B1'}), data={
            'days': 7,
            'days_ago': 30
        })

        # Call for stats of some other port between 30-60 days
        response3 = self.client.get(reverse('port_stats', kwargs={'name': 'port-A4'}), data={
            'days': 30,
            'days_ago': 30
        })

        Port.add_or_update([
            {
                "name": "port-A4",
                "version": "1.2.3",
                "portdir": "categoryA/port-A4"
            }
        ])

        self.assertEquals(response1.context['count']['all'], 1)
        self.assertEquals(response1.context['count']['requested'], 0)
        self.assertEquals(response2.context['count']['all'], 1)
        self.assertEquals(response2.context['count']['requested'], 0)
        self.assertEquals(response3.context['count']['all'], 0)

    def test_users_count(self):
        today_day = datetime.datetime.now().day
        three_months_ago = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=int(today_day) + 90)
        eleven_months_ago = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=int(today_day) + 335)

        eleven_months_ago_month = str(eleven_months_ago.month)
        three_months_ago_month = str(three_months_ago.month)
        eleven_months_ago_year = str(eleven_months_ago.year)
        three_months_ago_year = str(three_months_ago.year)

        submission = QUICK_SUBMISSION_JSON

        for i in three_months_ago, eleven_months_ago:
            submission_id = Submission.populate(submission, i)
            PortInstallation.populate(submission['active_ports'], submission_id)

        response = self.client.get(reverse('stats'))

        three_months_count = 0
        eleven_months_count = 0
        for i in response.context['users_by_month']:
            if i['month'] == datetime.datetime.strptime(three_months_ago_year + "-" + three_months_ago_month + "-01 00:00:00-+0000", '%Y-%m-%d %H:%M:%S-%z'):
                three_months_count = i['num']
            if i['month'] == datetime.datetime.strptime(eleven_months_ago_year + "-" + eleven_months_ago_month + "-01 00:00:00-+0000", '%Y-%m-%d %H:%M:%S-%z'):
                eleven_months_count = i['num']

        self.assertEquals(three_months_count, 1)
        self.assertEquals(eleven_months_count, 1)

        self.assertEquals(response.context['total_submissions'], 8)
        self.assertEquals(response.context['unique_users'], 6)
        self.assertEquals(response.context['current_week'], 5)
        self.assertEquals(response.context['last_week'], 0)

    def test_validation_general_stats(self):
        response1 = self.client.get(reverse('stats'), data={
            'days': 91
        })

        response2 = self.client.get(reverse('stats'), data={
            'days': "randomString"
        })

        response3 = self.client.get(reverse('stats'), data={
            'days': 30
        })

        self.assertEquals(response1.content, b"'91' is an invalid value. Allowed values are: [0, 7, 30, 90, 180, 365]")
        self.assertEquals(response2.content, b"Received 'randomString'. Expecting an integer.")
        self.assertIsInstance(response3.context['days'], int)

    def test_validation_port_stats(self):
        response1 = self.client.get(reverse('port_stats', kwargs={'name': 'port-B1'}), data={
            'days': 91
        })

        response2 = self.client.get(reverse('port_stats', kwargs={'name': 'port-B1'}), data={
            'days': "randomString"
        })

        response3 = self.client.get(reverse('port_stats', kwargs={'name': 'port-B1'}), data={
            'days': 30
        })

        self.assertEquals(response1.content, b"'91' is an invalid value. Allowed values are: [0, 7, 30, 90, 180, 365]")
        self.assertEquals(response2.content, b"Received 'randomString'. Expecting an integer.")
        self.assertIsInstance(response3.context['days'], int)
