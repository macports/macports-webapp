import os

from django.test import TestCase, Client
from django.urls import reverse

from ports.models import Port

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(BASE_DIR, 'tests', 'sample_data', 'portindex.json')


class TestDependencies(TestCase):
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        ports = Port.Load().open_portindex_json(JSON_FILE)
        Port.Load().load_categories_table(ports)
        Port.Load().load_ports_and_maintainers_table(ports)
        Port.Load().load_dependencies_table(ports)

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

        self.assertEquals(response1.context['ports'].count(), 7)
        self.assertEquals(response2.context['ports'].count(), 5)
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

        self.assertEquals(response.context['ports'].count(), 3)

