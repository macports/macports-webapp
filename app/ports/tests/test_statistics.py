import os
import json
import datetime

from django.test import TestCase, Client
from django.urls import reverse

from ports.models import UUID, PortInstallation, Submission, Port
from MacPorts.config import TEST_SUBMISSIONS, TEST_PORTINDEX_JSON


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

    # ====== TESTS FOR INDIVIDUAL PORT STATS ======
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
