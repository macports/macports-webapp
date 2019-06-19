import os

from django.test import TestCase, Client
from django.urls import reverse

from ports.models import Port

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(BASE_DIR, 'tests', 'sample_data', 'portindex.json')


class TestURLs(TestCase):
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        ports = Port.Load().open_portindex_json(JSON_FILE)
        Port.Load().load_categories_table(ports)
        Port.Load().load_ports_and_maintainers_table(ports)
        Port.Load().load_dependencies_table(ports)

    def test_home(self):
        response = self.client.get(reverse('home'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='ports/index.html')

    def test_stats_submit(self):
        response = self.client.get(reverse('stats_submit'))

        self.assertEquals(response.status_code, 200)

    def test_stats_home(self):
        response = self.client.get(reverse('stats_home'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='ports/stats.html')

    def test_maintainer_detail_github(self):
        response = self.client.get(reverse('maintainer_detail_github', kwargs={
            'github_handle': 'user'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='ports/maintainerdetail.html')

    def test_maintainer_detail_email(self):
        response = self.client.get(reverse('maintainer_detail_email', kwargs={
            'name': 'user',
            'domain': 'email.com'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='ports/maintainerdetail.html')

    def test_port_index(self):
        response = self.client.get(reverse('port-index'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='ports/index.html')

    def test_ports_index(self):
        response = self.client.get(reverse('ports-index'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='ports/index.html')

    def test_ports_search(self):
        response = self.client.get(reverse('ports_search'))

        self.assertEquals(response.status_code, 200)

    def test_search_ports_in_maintainer(self):
        response = self.client.get(reverse('search_ports_in_maintainer'))

        self.assertEquals(response.status_code, 200)

    def test_search_ports_in_category(self):
        response = self.client.get(reverse('search_ports_in_category'))

        self.assertEquals(response.status_code, 200)

    def test_search_ports_in_variant(self):
        response = self.client.get(reverse('search_ports_in_variant'))

        self.assertEquals(response.status_code, 200)

    def test_trac_tickets(self):
        response = self.client.get(reverse('trac_tickets'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='ports/ajax-filters/tickets.html')

    def test_category_list(self):
        response = self.client.get(reverse('category_list', kwargs={
            'cat': 'categoryA'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='ports/categorylist.html')

    def test_variant_list(self):
        response = self.client.get(reverse('variant_list', kwargs={
            'variant': 'var'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='ports/variantlist.html')

    def test_all_builds_filter(self):
        response = self.client.get(reverse('all_builds_filter'), data={
        })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='ports/ajax-filters/builds_filtered_table.html')

    def test_all_builds(self):
        response = self.client.get(reverse('all_builds'), data={
        })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='ports/all_builds.html')

    def test_update_api(self):
        response = self.client.get(reverse('update_api'))

        self.assertEquals(response.status_code, 200)

    def test_portdetail(self):
        response = self.client.get(reverse('port_detail', kwargs={
            'name': 'port-A1'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='ports/portdetail.html')
