from django.test import TransactionTestCase, Client
from django.urls import reverse

from port_detail.models import Port
from config import TEST_PORTINDEX_JSON


class TestURLsMaintainers(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        Port.load(TEST_PORTINDEX_JSON)

    def test_maintainer_github(self):
        response = self.client.get(reverse('maintainer_detail_github', kwargs={
            'github_handle': 'user'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='maintainers/maintainerdetail.html')

    def test_maintainer_email(self):
        response = self.client.get(reverse('maintainer_detail_email', kwargs={
            'name': 'user',
            'domain': 'email.com'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='maintainers/maintainerdetail.html')

    def test_maintainer_filter(self):
        response = self.client.get(reverse('maintainers_filter'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='ports/ajax-filters/filtered_table.html')
