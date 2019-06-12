from django.test import TestCase, Client
from django.urls import reverse

from parsing_scripts import load_initial_data, update


class TestExceptions(TestCase):
    def setUp(self):
        ports = load_initial_data.open_portindex_json("ports/tests/sample_data/portindex.json")
        load_initial_data.load_categories_table(ports)
        load_initial_data.load_ports_and_maintainers_table(ports)
        self.client = Client()

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
