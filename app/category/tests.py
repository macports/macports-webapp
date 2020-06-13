from django.test import TransactionTestCase, Client
from django.urls import reverse

from tests import setup


class TestURLsCategories(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        setup.setup_test_data()

    def test_category_url(self):
        response = self.client.get(reverse('category', kwargs={
            'cat': 'categoryA'
        }))

        self.assertRedirects(response, '/search/?selected_facets=categories_exact:categoryA')
