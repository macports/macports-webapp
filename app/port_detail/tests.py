from django.test import TransactionTestCase, Client
from django.urls import reverse

from port_detail.models import Port
from config import TEST_PORTINDEX_JSON


class TestURLsPortDetail(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        Port.load(TEST_PORTINDEX_JSON)

    def test_port_detail(self):
        response = self.client.get(reverse('port_detail', kwargs={
            'name': 'port-A1'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port_detail/port_detail_parent.html')

    def test_port_detail_tabbed(self):
        response = self.client.get(reverse('port_detail_tabbed', kwargs={
            'name': 'port-A1',
            'slug': 'summary'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port_detail/port_detail_parent.html')

    def test_port_detail_summary(self):
        response = self.client.get('/port/ajax-call/summary/?port_name=port-A1')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port_detail/port_detail_summary.html')

    def test_port_detail_stats(self):
        response = self.client.get('/port/ajax-call/stats/?port_name=port-A1')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port_detail/port_detail_stats.html')

    def test_port_detail_builds(self):
        response = self.client.get('/port/ajax-call/builds/?port_name=port-A1')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port_detail/port_detail_builds.html')
