from django.test import TransactionTestCase, Client
from django.urls import reverse

from tests import setup


class TestURLsBuilds(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        setup.setup_test_data()

    def test_all_builds(self):
        response = self.client.get(reverse('all_builds'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='buildhistory/all_builds.html')
