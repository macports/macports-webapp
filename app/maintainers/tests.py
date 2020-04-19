from django.test import TransactionTestCase, Client
from django.urls import reverse

from port_detail.models import Port
from maintainers.models import Maintainer
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
        response = self.client.get(reverse('search_in_maintainer'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='filtered_table.html')


class TestSearchInMaintainer(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        Port.load(TEST_PORTINDEX_JSON)

    def test_search_in_maintainer(self):
        response = self.client.get(reverse('search_in_maintainer'), data={
            'name': 'port-A',
            'maintainers__name': 'user',
        })

        self.assertEquals(response.context['ports'].count(), 4)


class TestMaintainersQueryAndUpdate(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        Port.load(TEST_PORTINDEX_JSON)

    def test_unique_entries_created(self):
        self.assertEquals(Maintainer.objects.count(), 6, "Failed to create unique entities for maintainers")

    def test_fetch_using_github(self):
        response = self.client.get(reverse('maintainer_detail_github', kwargs={'github_handle': 'user'}))
        maintainers_returned = response.context['maintainers']
        num_of_ports = response.context['all_ports_num']
        self.assertEquals(maintainers_returned.count(), 3)
        self.assertEquals(num_of_ports, 5)

    def test_fetch_using_email(self):
        response = self.client.get(reverse('maintainer_detail_email', kwargs={'name': 'user', 'domain': 'email.com'}))
        maintainers_returned = response.context['maintainers']
        num_of_ports = response.context['all_ports_num']
        self.assertEquals(maintainers_returned.count(), 3)
        self.assertEquals(num_of_ports, 4)

    def test_maintainers_updated(self):
        updated_port = [{
            "name": "port-A1",
            "portdir": "categoryA/port-A1",
            "version": "1.0.0",
            "maintainers": [
                {
                    "email": {
                        "domain": "email.com",
                        "name": "new_user"
                    },
                    "github": "new_user"
                },
                {
                    "github": "user"
                }
            ]
        }]
        Port.update(updated_port)
        port = Port.objects.get(name="port-A1")
        self.assertEquals(port.maintainers.count(), 2)
        self.assertEquals(Maintainer.objects.all().count(), 7)
        self.assertEquals(Port.objects.get(name="port-A3-diff").maintainers.count(), 1)
