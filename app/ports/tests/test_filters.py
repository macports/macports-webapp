import os

from django.test import TransactionTestCase
from django.urls import reverse

from ports.models import Port
from MacPorts.config import TEST_PORTINDEX_JSON


class TestDependencies(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        Port.load(TEST_PORTINDEX_JSON)

    def test_search(self):
        response1 = self.client.get(reverse('ports_search'), data={
            'search_by': 'name',
            'name': 'port',
            'search_text': 'port'
        })

        response2 = self.client.get(reverse('ports_search'), data={
            'search_by': 'description',
            'description': 'categoryA',
            'search_text': 'categoryA'
        })

        response3 = self.client.get(reverse('ports_search'), data={
            'search_by': 'name',
            'name': 'port-A5',
            'search_text': 'port-A5'
        })

        self.assertEquals(response1.context['ports'].count(), 8)
        self.assertEquals(response2.context['ports'].count(), 6)
        self.assertEquals(response3.context['ports'].count(), 1)

    def test_search_in_category(self):
        response = self.client.get(reverse('search_ports_in_category'), data={
            'name': 'port-A3',
            'categories__name': 'categoryA',
        })

        self.assertEquals(response.context['ports'].count(), 1)

    def test_search_in_maintainer(self):
        response = self.client.get(reverse('search_ports_in_maintainer'), data={
            'name': 'port-A',
            'maintainers__name': 'user',
        })

        self.assertEquals(response.context['ports'].count(), 4)

