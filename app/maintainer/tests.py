from django.test import TransactionTestCase, Client
from django.urls import reverse

from tests import setup


class TestURLsMaintainers(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        setup.setup_test_data()

    def test_maintainer_url(self):
        response = self.client.get(reverse('maintainer', kwargs={
            'm': 'user'
        }))

        self.assertRedirects(response, '/search/?selected_facets=maintainers_exact:user')
