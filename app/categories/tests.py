from django.test import TransactionTestCase, Client
from django.urls import reverse

from port_detail.models import Port
from config import TEST_PORTINDEX_JSON


class TestURLsCategories(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        Port.load(TEST_PORTINDEX_JSON)

    def test_category(self):
        response = self.client.get(reverse('category', kwargs={
            'cat': 'categoryA'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='categories/category.html')

    def test_category_not_found(self):
        response = self.client.get(reverse('category', kwargs={
            'cat': 'thisCategoryshouldRaiseError'
        }))

        self.assertTemplateUsed(response, template_name='categories/exceptions/category_not_found.html')

    def test_search_in_category(self):
        response = self.client.get(reverse('search_in_category'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='filtered_table.html')


class TestSearchInCategory(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        Port.load(TEST_PORTINDEX_JSON)

    def test_search_in_category(self):
        response = self.client.get(reverse('search_in_category'), data={
            'name': 'port-A3',
            'categories__name': 'categoryA',
        })

        self.assertEquals(response.context['ports'].count(), 1)
