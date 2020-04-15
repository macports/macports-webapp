from django.test import TransactionTestCase, Client
from django.urls import reverse

from port_detail.models import Port
from MacPorts.config import TEST_PORTINDEX_JSON


class TestURLsStats(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        Port.load(TEST_PORTINDEX_JSON)

    def test_stats(self):
        response = self.client.get(reverse('stats'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='stats/stats.html')

    def test_port_installations(self):
        response = self.client.get(reverse('stats_port_installations'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='stats/stats_port_installations.html')

    def test_port_installations_filter(self):
        response = self.client.get(reverse('stats_port_installations_filter'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='stats/port_installations_table.html')

    def test_stats_faq(self):
        response = self.client.get(reverse('stats_faq'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='stats/stats_faq.html')
