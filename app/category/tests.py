from django.test import TransactionTestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient

from tests import setup
from category.models import Category
from port.models import Port


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


class TestCategoryAPI(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = APIClient()
        setup.setup_test_data()

    def test_list_view(self):
        response = self.client.get(reverse('category-list'), format='json')

        response = response.data

        # pagination occurs after 50 objects, but we have only 3 categories
        self.assertEqual(len(response['results']), 3)

        for category in response['results']:
            if category['name'] == 'categoryA':
                self.assertEqual(category['ports_count'], 6)

            if category['name'] == 'categoryB':
                self.assertEqual(category['ports_count'], 2)

            if category['name'] == 'categoryC':
                self.assertEqual(category['ports_count'], 1)

    def test_detail_view(self):
        # for Category model, name field is the primary key
        response = self.client.get(reverse('category-detail', kwargs={'pk': 'categoryA'}), format='json')

        response = response.data

        # pagination occurs after 50 objects, but we have only 3 categories
        self.assertEqual(response['name'], 'categoryA')
        self.assertEqual(response['ports_count'], 6)
        s = set()
        for port in response['ports']:
            s.add(port)

        self.assertEqual(s, {'port-A1', 'port-A1-subport', 'port-A2', 'port-A3-diff', 'port-A4', 'port-A5'})


class TestCategoryLoadUpdate(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        setup.setup_test_data()

    def test_loaded(self):
        self.assertEqual(Category.objects.all().count(), 3)
        self.assertEqual(Category.objects.get(name='categoryA').name, 'categoryA')
        self.assertEqual(Category.objects.get(name__iexact='CATEGORYA').name, 'categoryA')

    def test_invalid_case(self):

        # try to update a port with the category in upper case

        Port.add_or_update([
            {
                "portdir": "categoryA\/port-A1",
                "platforms": "darwin",
                "name": "port-A1-subport",
                "categories": ["CATEGORYA"],
                "version": "1.0.0",
            }
        ])

        self.assertEqual(Category.objects.all().count(), 3)
        self.assertEqual(Category.objects.get(name='categoryA').name, 'categoryA')
        self.assertEqual(Category.objects.get(name__iexact='CATEGORYA').name, 'categoryA')

    def test_relations(self):
        t_port = 'port-A1'
        t_category = 'categoryA'
        # try to add a category and then remove it from a port

        Port.add_or_update([
            {
                "portdir": "categoryA\/port-A1",
                "platforms": "darwin",
                "name": "port-A1",
                "categories": ["categoryNEW"],
                "version": "1.0.0",
            }
        ])

        self.assertEqual(Category.objects.all().count(), 4)
        # we must get just one object for categoryNEW
        self.assertEqual(Port.objects.get(categories__name='categoryNEW').name, t_port)

        # check relations of categoryA now
        broken = False
        ports = Category.objects.get(name=t_category).ports.all()
        for port in ports:
            if port.name == 'port-A1':
                broken = True

        self.assertEqual(broken, False)

        # now add the category back again
        Port.add_or_update([
            {
                "portdir": "categoryA\/port-A1",
                "platforms": "darwin",
                "name": "port-A1",
                "categories": ["categoryNEW", t_category],
                "version": "1.0.0",
            }
        ])

        self.assertEqual(Category.objects.all().count(), 4)
        self.assertEqual(Port.objects.get(categories__name='categoryNEW').name, t_port)

        # check relations of categoryA now
        broken = True
        ports = Category.objects.get(name=t_category).ports.all()
        for port in ports:
            if port.name == 'port-A1':
                broken = False

        self.assertEqual(broken, False)
