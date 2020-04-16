from django.test import TransactionTestCase, Client
from django.urls import reverse

from port_detail.models import Port
from config import TEST_PORTINDEX_JSON


class TestURLsBuilds(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        Port.load(TEST_PORTINDEX_JSON)

    def test_all_builds(self):
        response = self.client.get(reverse('all_builds'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='builds/all_builds.html')

    def test_all_builds_filter(self):
        response = self.client.get(reverse('all_builds_filter'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='builds/builds_filtered_table.html')
