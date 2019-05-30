from django.test import TestCase, Client
from django.urls import reverse
from ports.models import Maintainer
from parsing_scripts import load_initial_data


class TestMaintainers(TestCase):
    def setUp(self):
        ports = load_initial_data.open_portindex_json("ports/tests/sample_data/portindex.json")
        load_initial_data.load_categories_table(ports)
        load_initial_data.load_ports_and_maintainers_table(ports)

    def test_unique_entries_created(self):
        self.assertEquals(Maintainer.objects.count(), 6, "Failed to create unique entities for maintainers")

    def test_fetch_using_github(self):
        client = Client()
        response = client.get(reverse('maintainer_detail_github', kwargs={'github_handle': 'user'}))
        maintainers_returned = response.context['maintainers']
        is_github = response.context['github']
        num_of_ports = response.context['all_ports_num']
        self.assertEquals(maintainers_returned.count(), 3)
        self.assertTrue(is_github)
        self.assertEquals(num_of_ports, 4)

    def test_fetch_using_email(self):
        client = Client()
        response = client.get(reverse('maintainer_detail_email', kwargs={'name': 'user', 'domain': 'email.com'}))
        maintainers_returned = response.context['maintainers']
        is_github = response.context['github']
        num_of_ports = response.context['all_ports_num']
        self.assertEquals(maintainers_returned.count(), 3)
        self.assertFalse(is_github)
        self.assertEquals(num_of_ports, 3)
