import json, datetime

from django.test import TestCase, Client
from django.urls import reverse

from ports.models import Port, Builder, BuildHistory, Submission, PortInstallation
from MacPorts.config import TEST_PORTINDEX_JSON, TEST_SUBMISSIONS


class TestAPIv1(TestCase):
    @classmethod
    def setUpTestData(cls):
        Port.load(TEST_PORTINDEX_JSON)

    def test_api_port_info(self):
        response1 = self.client.get(reverse('api_port_info', kwargs={
            'name': 'port-A1'
        }))

        response2 = self.client.get(reverse('api_port_info', kwargs={
            'name': 'port-does-not-exist'
        }))

        response3 = self.client.get(reverse('api_port_info', kwargs={
            'name': 'port-B1'
        }), data={
            'fields': 'version,name,invalidfield'
        })

        self.assertEquals(response1.json()['name'], 'port-A1')
        self.assertEquals(response1.json()['maintainers'][0]['name'], 'user')
        self.assertEquals(response2.json()['status_code'], 404)
        self.assertEquals(response3.json()['name'], 'port-B1')
        self.assertEquals(response3.json().get('invalidfield'), None)
        self.assertEquals(response3.json().get('maintainers'), None)

    def test_api_port_build_history(self):
        Builder.objects.create(name='10.14_x86_64')
        BuildHistory.populate()

        obj = BuildHistory.objects.first()
        obj.port_name = 'port-A1'
        obj.save()

        response1 = self.client.get(reverse('api_port_builds', kwargs={
            'name': 'port-A1'
        }), data={
            'count': 1
        })

        response2 = self.client.get(reverse('api_port_health', kwargs={
            'name': 'port-A1'
        }))

        self.assertEquals(len(response1.json()), 1)
        self.assertEquals(response1.json()[0]['port_name'], 'port-A1')
        self.assertEquals(len(response2.json()), 1)
        self.assertEquals(response2.json()[0]['port_name'], 'port-A1')

    def test_api_port_stats(self):
        with open(TEST_SUBMISSIONS, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

        for i in data:
            submission_id = Submission.populate(i, datetime.datetime.now(tz=datetime.timezone.utc))
            PortInstallation.populate(i['active_ports'], submission_id)

        response1 = self.client.get(reverse('api_port_stats', kwargs={
            'name': 'port-A1'
        }))
        response2 = self.client.get(reverse('api_port_stats', kwargs={
            'name': 'port-C1'
        }))
        response3 = self.client.get(reverse('api_port_stats', kwargs={
            'name': 'port-C1'
        }), data={
            'criteria': 'xcode_version'
        })

        self.assertEquals(response1.json['total_count', 4])
        self.assertEquals(response1.json['req_count', 2])

        counter = 0
        for i in response2.json()['port_version']:
            if i['version'] == '1.0':
                self.assertEquals(i['num'], 1)
                counter += 1
            elif i['version'] == '1.2':
                self.assertEquals(i['num'], 2)
                counter += 1
        self.assertEquals(counter, 2)

        self.assertEquals(response3.json().get('total_count'), None)
        self.assertEquals(len(response3.json()['xcode_versions']), 2)
