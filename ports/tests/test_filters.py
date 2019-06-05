from django.test import TestCase, Client
from django.urls import reverse

from parsing_scripts import load_initial_data, update


class TestDependencies(TestCase):
    def setUp(self):
        ports = load_initial_data.open_portindex_json("ports/tests/sample_data/portindex.json")
        load_initial_data.load_categories_table(ports)
        load_initial_data.load_ports_and_maintainers_table(ports)
        load_initial_data.load_dependencies_table(ports)

    def test_search(self):
        client = Client()
        response1 = client.post(reverse('ports_search'), data={
            'search_by': 'name',
            'name': 'port',
            'search_text': 'port'
        })

        response2 = client.post(reverse('ports_search'), data={
            'search_by': 'description',
            'description': 'categoryA',
            'search_text': 'categoryA'
        })

        response3 = client.post(reverse('ports_search'), data={
            'search_by': 'name',
            'name': 'port-A5',
            'search_text': 'port-A5'
        })

        self.assertEquals(response1.context['results'].count(), 7)
        self.assertEquals(response2.context['results'].count(), 5)
        self.assertEquals(response3.context['results'].count(), 1)

    def test_search_in_category(self):
        client = Client()

        response = client.post(reverse('search_ports_in_category'), data={
            'name': 'port-A3',
            'categories__name': 'categoryA',
        })

        self.assertEquals(response.context['ports'].count(), 1)

    def test_search_in_maintainer(self):
        client = Client()

        response = client.post(reverse('search_ports_in_maintainer'), data={
            'name': 'port-A',
            'maintainers__name': 'user',
        })

        self.assertEquals(response.context['ports'].count(), 3)

