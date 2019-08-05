import os
import json
import datetime

from django.test import TestCase, Client
from django.urls import reverse

from ports.models import UUID, PortInstallation, Submission, Port
from MacPorts.config import TEST_SUBMISSIONS, TEST_PORTINDEX_JSON

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


class TestStatistics(TestCase):
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        Port.load(TEST_PORTINDEX_JSON)

        with open(TEST_SUBMISSIONS, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

        for i in data:
            submission_id = Submission.populate(i, datetime.datetime.now(tz=datetime.timezone.utc))
            PortInstallation.populate(i['active_ports'], submission_id)

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

    # ====== TESTS FOR INDIVIDUAL PORT STATS START ======
    def test_port_installation_counts(self):
        response1 = self.client.get(reverse('port_detail_stats'), data={
            'port_name': 'port-A1'
        })

        response2 = self.client.get(reverse('port_detail_stats'), data={
            'port_name': 'port-B1'
        })

        self.assertEquals(response1.context['total_port_installations_count']['submission__user_id__count'], 4)
        self.assertEquals(response1.context['requested_port_installations_count']['submission__user_id__count'], 2)

        self.assertEquals(response2.context['total_port_installations_count']['submission__user_id__count'], 0)
        self.assertEquals(response2.context['requested_port_installations_count']['submission__user_id__count'], 0)

    def test_port_versions_count(self):
        response1 = self.client.get(reverse('port_detail_stats'), data={
            'port_name': 'port-C1'
        })

        counter = 0
        for i in response1.context['port_installations_by_port_version']:
            if i['version'] == '1.0':
                self.assertEquals(i['num'], 1)
                counter += 1
            elif i['version'] == '1.2':
                self.assertEquals(i['num'], 2)
                counter += 1
        self.assertEquals(counter, 2)

    def test_os_version_and_xcode_version(self):
        response1 = self.client.get(reverse('port_detail_stats'), data={
            'port_name': 'port-C1'
        })

        counter = 0
        for i in response1.context['port_installations_by_os_and_xcode_version']:
            if i['submission__os_version'] == '10.14' and i['submission__xcode_version'] == '10.3':
                self.assertEquals(i['num'], 2)
                counter += 1
            elif i['submission__os_version'] == '10.13' and i['submission__xcode_version'] == '10.2.1':
                self.assertEquals(i['num'], 1)
                counter += 1
        self.assertEquals(counter, 2)

    def test_os_stdlib_build_arch(self):
        response1 = self.client.get(reverse('port_detail_stats'), data={
            'port_name': 'port-A3-diff'
        })

        counter = 0
        for i in response1.context['port_installations_by_os_stdlib_build_arch']:
            if i['submission__os_version'] == '10.14' and i['submission__build_arch'] == 'x86_64' and i['submission__cxx_stdlib'] == 'libc++':
                self.assertEquals(i['num'], 3)
                counter += 1
            elif i['submission__os_version'] == '10.12' and i['submission__build_arch'] == 'x86_64' and i['submission__cxx_stdlib'] == 'libc++':
                self.assertEquals(i['num'], 1)
                counter += 1
        self.assertEquals(counter, 2)

    def test_time_travel(self):
        time_now = datetime.datetime.now(tz=datetime.timezone.utc)

        # Go back in time 35 days
        time_35_days_ago = time_now - datetime.timedelta(days=35)
        submission = QUICK_SUBMISSION_JSON

        # Make a submission dated 35 days ago
        submission_id = Submission.populate(submission, time_35_days_ago)
        PortInstallation.populate(submission['active_ports'], submission_id)

        # Call for stats between 30-60 days
        response1 = self.client.get(reverse('port_detail_stats'), data={
            'port_name': 'port-B1',
            'days': 30,
            'days_ago': 30
        })

        # Call for stats between 30-37 days
        response2 = self.client.get(reverse('port_detail_stats'), data={
            'port_name': 'port-B1',
            'days': 7,
            'days_ago': 30
        })

        # Call for stats of some other port between 30-60 days
        response3 = self.client.get(reverse('port_detail_stats'), data={
            'port_name': 'port-A4',
            'days': 30,
            'days_ago': 30
        })

        self.assertEquals(response1.context['total_port_installations_count']['submission__user_id__count'], 1)
        self.assertEquals(response1.context['requested_port_installations_count']['submission__user_id__count'], 0)
        self.assertEquals(response2.context['total_port_installations_count']['submission__user_id__count'], 1)
        self.assertEquals(response2.context['requested_port_installations_count']['submission__user_id__count'], 0)
        self.assertEquals(response3.context['total_port_installations_count']['submission__user_id__count'], 0)

    def test_installations_vs_month(self):
        date_may_2019 = "2019-05-25 10:10:10-+0000"
        datetime_obj = datetime.datetime.strptime(date_may_2019, '%Y-%m-%d %H:%M:%S-%z')

        submission = QUICK_SUBMISSION_JSON

        # Make a submission dated 2019-05-25
        submission_id = Submission.populate(submission, datetime_obj)
        PortInstallation.populate(submission['active_ports'], submission_id)

        response = self.client.get(reverse('port_detail_stats'), data={
            'port_name': 'port-A1'
        })

        may_count = 0
        current_count = 0
        today = datetime.datetime.now()
        month = today.strftime("%m")
        year = today.strftime("%Y")
        for i in response.context['port_installations_by_month']:
            if i['month'] == datetime.datetime.strptime("2019-05-01 00:00:00-+0000", '%Y-%m-%d %H:%M:%S-%z'):
                may_count = i['num']
            elif i['month'] == datetime.datetime.strptime(year + "-" + month + "-01 00:00:00-+0000", '%Y-%m-%d %H:%M:%S-%z'):
                current_count = i['num']
        self.assertEquals(may_count, 1)
        self.assertEquals(current_count, 4)

    def test_validation(self):
        response1 = self.client.get(reverse('port_detail_stats'), data={
            'port_name': 'port-A1',
            'days': 91
        })

        response2 = self.client.get(reverse('port_detail_stats'), data={
            'port_name': 'port-A1',
            'days': "randomString"
        })

        response3 = self.client.get(reverse('port_detail_stats'), data={
            'port_name': 'port-A1'
        })

        self.assertEquals(response1.content, b"'91' is an invalid value. Allowed values are: [0, 7, 30, 90, 180, 365]")
        self.assertEquals(response2.content, b"Received 'randomString'. Expecting an integer.")
        self.assertIsInstance(response3.context['days'], int)
        self.assertIsInstance(response3.context['days_ago'], int)

        # ====== TESTS FOR INDIVIDUAL PORT STATS END ======

        # ====== TESTS FOR GENERAL STATS START ======
    def test_users_count(self):
        date_april_2019 = datetime.datetime.strptime("2019-04-25 10:10:10-+0000", '%Y-%m-%d %H:%M:%S-%z')
        date_april_2018 = datetime.datetime.strptime("2018-04-25 10:10:10-+0000", '%Y-%m-%d %H:%M:%S-%z')

        submission = QUICK_SUBMISSION_JSON

        # Make a submissions dated 2019-04-25 and 2019-04-2018
        for i in date_april_2018, date_april_2019:
            submission_id = Submission.populate(submission, i)
            PortInstallation.populate(submission['active_ports'], submission_id)

        response = self.client.get(reverse('stats_home'))

        april_2018_count = 0
        april_2019_count = 0
        for i in response.context['users_by_month']:
            if i['month'] == datetime.datetime.strptime("2018-04-01 00:00:00-+0000", '%Y-%m-%d %H:%M:%S-%z'):
                april_2018_count = i['num']
            if i['month'] == datetime.datetime.strptime("2019-04-01 00:00:00-+0000", '%Y-%m-%d %H:%M:%S-%z'):
                april_2019_count = i['num']

        self.assertEquals(april_2019_count, 1)
        self.assertEquals(april_2018_count, 1)

        self.assertEquals(response.context['total_submissions'], 8)
        self.assertEquals(response.context['unique_users'], 6)
        self.assertEquals(response.context['current_week'], 5)
        self.assertEquals(response.context['last_week'], 0)

    def test_validation_general_stats(self):
        response1 = self.client.get(reverse('stats_home'), data={
            'days': 91
        })

        response2 = self.client.get(reverse('stats_home'), data={
            'days': "randomString"
        })

        response3 = self.client.get(reverse('stats_home'), data={
            'days': 30
        })

        self.assertEquals(response1.content, b"'91' is an invalid value. Allowed values are: [0, 7, 30, 90, 180, 365]")
        self.assertEquals(response2.content, b"Received 'randomString'. Expecting an integer.")
        self.assertIsInstance(response3.context['days'], int)

    def test_macports_version_general_stats(self):
        response = self.client.get(reverse('stats_home'))

        count_2_5_1 = 0
        for i in response.context['macports_distribution']:
            if i['macports_version'] == '2.5.1':
                count_2_5_1 = i['num']

        self.assertEquals(count_2_5_1, 5)

    def test_os_version_and_xcode_version_general_stats(self):
        response = self.client.get(reverse('stats_home'))

        counter = 0
        for i in response.context['xcode_distribution']:
            if i['os_version'] == '10.14' and i['xcode_version'] == '10.3':
                self.assertEquals(i['num'], 2)
                counter += 1
            elif i['os_version'] == '10.14' and i['xcode_version'] == '10.2.1':
                self.assertEquals(i['num'], 1)
                counter += 1
            elif i['os_version'] == '10.13' and i['xcode_version'] == '10.2.1':
                self.assertEquals(i['num'], 1)
                counter += 1
            elif i['os_version'] == '10.12' and i['xcode_version'] == '10.2.1':
                self.assertEquals(i['num'], 1)
                counter += 1
        self.assertEquals(counter, 4)

        # ====== TESTS FOR GENERAL STATS END ======

        # ====== TESTS FOR PORT INSTALLATIONS START ======
    def test_validation_port_installations(self):
        response1 = self.client.get(reverse('stats_port_installations'), data={
            'first': 'total_count',
            'second': '-total_count'
        })
        byteresponse1 = b"'total_count' and '-total_count' refer to the same column."

        response2 = self.client.get(reverse('stats_port_installations'), data={
            'first': 'total_count',
            'second': '-req_count',
            'third': 'random_string'
        })
        byteresponse2 = b"random_string is an invalid column. Expecting: ['port', '-port', 'total_count', '-total_count', '-req_count', 'req_count']"

        self.assertEquals(response1.content, byteresponse1)
        self.assertEquals(response2.content, byteresponse2)
