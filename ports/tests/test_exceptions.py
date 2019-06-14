import os

from django.test import TestCase, Client
from django.urls import reverse

from parsing_scripts import load_initial_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(BASE_DIR, 'tests', 'sample_data', 'portindex.json')


class TestExceptions(TestCase):
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        ports = load_initial_data.open_portindex_json(JSON_FILE)
        load_initial_data.load_categories_table(ports)
        load_initial_data.load_ports_and_maintainers_table(ports)

    def test_400(self):
        response = self.client.get('/testingA404')

        self.assertEquals(response.status_code, 404)
        self.assertTemplateUsed(response, template_name='404.html')

    def test_port_not_found(self):
        response_summary = self.client.get(reverse('port_detail_summary'), data={
            'portname': 'Port.DoesNotExist'
        })

        response_builds = self.client.get(reverse('port_detail_builds'), data={
            'portname': 'Port.DoesNotExist'
        })

        self.assertTemplateUsed(response_summary, template_name='ports/exceptions/port_not_found.html')
        self.assertTemplateUsed(response_builds, template_name='ports/exceptions/port_not_found.html')

    def test_category_not_found(self):
        response = self.client.get(reverse('category_list', kwargs={
            'cat': 'thisCategoryshouldRaiseError'
        }))

        self.assertTemplateUsed(response, template_name='ports/exceptions/category_not_found.html')
