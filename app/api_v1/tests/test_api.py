import json

from django.test import TestCase, Client
from django.urls import reverse

from ports.models import Port, Builder, BuildHistory
from MacPorts.config import TEST_PORTINDEX_JSON


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
        self.assertEquals(response2.json()[0]['name'], 'port-A1')
