from django.test import TransactionTestCase, Client
from django.urls import reverse

from tests import setup
from variant.models import Variant
from port.models import Port


class TestURLsCategories(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        setup.setup_test_data()

    def test_variant_url(self):
        response = self.client.get(reverse('variant', kwargs={
            'v': 'universal'
        }))

        self.assertRedirects(response, '/search/?selected_facets=variants_exact:universal')

    def test_old_url_redirect(self):
        response = self.client.get(reverse('variant_old', kwargs={
            'v': 'universal'
        }))

        self.assertRedirects(response, reverse('variant', kwargs={
            'v': 'universal'
        }), status_code=302, target_status_code=302)


class TestVariantsAddUpdate(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        setup.setup_test_data()

    def test_added(self):
        self.assertEqual(Variant.objects.all().count(), 8)

    def test_removed(self):
        Port.add_or_update([{
            "portdir": "categoryA\/port-A1",
            "platforms": "darwin",
            "name": "port-A1",
            "categories": ["categoryA"],
            "version": "1.0.0",
            "revision": "0"
        }])

        self.assertEqual(Port.objects.get(name='port-A1').variants.all().count(), 0)
        self.assertEqual(Variant.objects.all().count(), 7)

        Port.add_or_update([{
            "portdir": "categoryA\/port-A1",
            "platforms": "darwin",
            "name": "port-A1",
            "categories": ["categoryA"],
            "version": "1.0.0",
            "revision": "0",
            "vinfo": [
                {"variant": "universal"},
                {"variant": "gcc"}
            ]
        }])

        self.assertEqual(Port.objects.get(name='port-A1').variants.all().count(), 2)
        self.assertEqual(Variant.objects.all().count(), 9)

    def test_different_case(self):
        Port.add_or_update([{
            "portdir": "categoryA\/port-A1",
            "platforms": "darwin",
            "name": "port-A1",
            "categories": ["categoryA"],
            "version": "1.0.0",
            "revision": "0",
            "vinfo": [
                {"variant": "UNIVERSAL"}
            ]
        }])

        self.assertEqual(Port.objects.get(name='port-A1').variants.all().count(), 1)
        self.assertEqual(Variant.objects.all().count(), 8)


