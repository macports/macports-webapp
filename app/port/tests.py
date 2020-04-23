from django.test import TransactionTestCase, Client
from django.urls import reverse
from django.core.management import call_command

from port.models import Port, Dependency
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
        self.assertTemplateUsed(response, template_name='port/port_detail_parent.html')

    def test_port_not_found(self):
        response = self.client.get(reverse('port_detail', kwargs={
            'name': 'testingA404.'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port/exceptions/port_not_found.html')

    def test_port_detail_tabbed(self):
        response = self.client.get(reverse('port_detail_tabbed', kwargs={
            'name': 'port-A1',
            'slug': 'summary'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port/port_detail_parent.html')

    def test_port_detail_summary(self):
        response = self.client.get('/port/ajax-call/summary/?port_name=port-A1')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port/port_detail_summary.html')

    def test_port_detail_stats(self):
        response = self.client.get('/port/ajax-call/stats/?port_name=port-A1')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port/port_detail_stats.html')

    def test_port_detail_builds(self):
        response = self.client.get('/port/ajax-call/builds/?port_name=port-A1')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port/port_detail_builds.html')


class TestDependencies(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        Port.load(TEST_PORTINDEX_JSON)

    def test_rows_created(self):
        self.assertEquals(Dependency.objects.all().count(), 6)

    def test_dependencies_fetched(self):
        response = self.client.get(reverse('port_detail_summary_ajax'), data={'port_name': 'port-A1'})
        dependencies = response.context['dependencies']
        self.assertEquals(dependencies.get(type='lib').dependencies.all().count(), 2)
        total_dependencies = []
        for d_type in dependencies:
            for dependency in d_type.dependencies.all():
                total_dependencies.append(dependency)
        self.assertEquals(len(total_dependencies), 3)

    def test_updates(self):
        updated_port = [{
            "name": "port-A5",
            "version": "1.0.0",
            "portdir": "categoryA/port-A5",
            "depends_extract": ["bin:port-C1:port-C1"],
            "depends_run": ["port:port-A1"],
        }]
        Port.update(updated_port)
        dependencies = Dependency.objects.filter(port_name__name__iexact='port-A5')
        self.assertEquals(dependencies.get(type='run').dependencies.all().count(), 1)
        self.assertEquals(dependencies.get(type='run').dependencies.all().first().name, 'port-A1')
        self.assertEquals(dependencies.count(), 2)


class TestPortsSearch(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        Port.load(TEST_PORTINDEX_JSON)

    def test_ports_search(self):
        response1 = self.client.get(reverse('ports_search'), data={
            'search_by': 'name',
            'name': 'port',
            'search_text': 'port'
        })

        response2 = self.client.get(reverse('ports_search'), data={
            'search_by': 'description',
            'description': 'categoryA',
            'search_text': 'categoryA'
        })

        response3 = self.client.get(reverse('ports_search'), data={
            'search_by': 'name',
            'name': 'port-A5',
            'search_text': 'port-A5'
        })

        self.assertEquals(response1.context['ports'].count(), 8)
        self.assertEquals(response2.context['ports'].count(), 6)
        self.assertEquals(response3.context['ports'].count(), 1)


class TestPortsQueryAndUpdate(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        Port.load(TEST_PORTINDEX_JSON)

    def test_updates(self):
        call_command('update-portinfo', '3c6f37828d091670e7b9a2676757b2e468ee3d52', 'cb7086953124c73ffb616e955653176e3c4be02c')
        try:
            port1 = Port.objects.get(name='youtube-dl')
            port2 = Port.objects.get(name='py-yapf')
            update_success = True
        except Port.DoesNotExist:
            update_success = False
        self.assertEquals(update_success, True)

    def test_deleted(self):
        Port.mark_deleted({
            'categoryA/port-A1': {
                'port-A1'
            }
        })

        port_status_subport = Port.objects.get(name='port-A1-subport').active
        port_status_mainport = Port.objects.get(name='port-A1').active
        self.assertEquals(port_status_mainport, True)
        self.assertEquals(port_status_subport, False)

    def test_moved(self):
        Port.update([
            {
                "variants": ["universal"],
                "portdir": "categoryA/port-A1",
                "depends_fetch": ["bin:port-A4:port-A4"],
                "description": "This is port A1 of categoryA",
                "homepage": "http:\/\/portA1.website\/",
                "epoch": "0",
                "platforms": "darwin",
                "name": "port-A2-subport",
                "depends_lib": ["lib:pq:port-A2", "port:port-A3-diff"],
                "long_description": "Just a test port written to test something.",
                "license": "MIT",
                "maintainers": [{
                    "email": {
                        "domain": "email.com",
                        "name": "user"
                    },
                    "github": "user"
                }],
                "categories": ["categoryA"],
                "version": "1.0.0",
                "revision": "0"
            },
            {
                "variants": ["universal"],
                "portdir": "categoryA/port-A1",
                "depends_fetch": ["bin:port-A4:port-A4"],
                "description": "This is port A1 of categoryA",
                "homepage": "http:\/\/portA1.website\/",
                "epoch": "0",
                "platforms": "darwin",
                "name": "port-A3-subport",
                "depends_lib": ["lib:pq:port-A2", "port:port-A3-diff"],
                "long_description": "Just a test port written to test something.",
                "license": "MIT",
                "maintainers": [{
                    "email": {
                        "domain": "email.com",
                        "name": "user"
                    },
                    "github": "user"
                }],
                "categories": ["categoryA"],
                "version": "1.0.0",
                "revision": "0"
            }
        ])

        port_status_subport1 = Port.objects.get(name='port-A1-subport').active
        port_status_subport2 = Port.objects.get(name='port-A2-subport').active
        port_status_subport3 = Port.objects.get(name='port-A3-subport').active
        self.assertEquals(port_status_subport1, True)
        self.assertEquals(port_status_subport2, True)
        self.assertEquals(port_status_subport3, True)

        # Entire categoryA/port-A1 portdir is removed, but the subports move to other directory
        # All ports under category/port-A1 would be deleted.
        Port.mark_deleted({
            'categoryA/port-A1': {}
        })

        port_status_subport1 = Port.objects.get(name='port-A1-subport').active
        port_status_subport2 = Port.objects.get(name='port-A2-subport').active
        port_status_subport3 = Port.objects.get(name='port-A3-subport').active
        self.assertEquals(port_status_subport1, False)
        self.assertEquals(port_status_subport2, False)
        self.assertEquals(port_status_subport3, False)

        # The moved ports would be found at the new location and will be appended to the list of JSON objects
        Port.update([
            {
                "variants": ["universal"],
                "portdir": "categoryTemp/newPorts",
                "depends_fetch": ["bin:port-A4:port-A4"],
                "description": "This is port A1 of categoryA",
                "homepage": "http:\/\/portA1.website\/",
                "epoch": "0",
                "platforms": "darwin",
                "name": "port-A2-subport",
                "depends_lib": ["lib:pq:port-A2", "port:port-A3-diff"],
                "long_description": "Just a test port written to test something.",
                "license": "MIT",
                "maintainers": [{
                    "email": {
                        "domain": "email.com",
                        "name": "user"
                    },
                    "github": "user"
                }],
                "categories": ["categoryA"],
                "version": "1.0.0",
                "revision": "0"
            },
            {
                "variants": ["universal"],
                "portdir": "categoryTemp/newPorts",
                "depends_fetch": ["bin:port-A4:port-A4"],
                "description": "This is port A1 of categoryA",
                "homepage": "http:\/\/portA1.website\/",
                "epoch": "0",
                "platforms": "darwin",
                "name": "port-A3-subport",
                "depends_lib": ["lib:pq:port-A2", "port:port-A3-diff"],
                "long_description": "Just a test port written to test something.",
                "license": "MIT",
                "maintainers": [{
                    "email": {
                        "domain": "email.com",
                        "name": "user"
                    },
                    "github": "user"
                }],
                "categories": ["categoryA"],
                "version": "1.0.0",
                "revision": "0"
            }
        ])

        port_status_subport2 = Port.objects.get(name='port-A2-subport').active
        port_status_subport3 = Port.objects.get(name='port-A3-subport').active
        self.assertEquals(port_status_subport2, True)
        self.assertEquals(port_status_subport3, True)

    def test_added_back(self):
        Port.mark_deleted({
            'categoryA/port-A1': {
                'port-A1'
            }
        })
        Port.update([
            {
                "variants": ["universal"],
                "portdir": "categoryA\/port-A1",
                "depends_fetch": ["bin:port-A4:port-A4"],
                "description": "This is port A1 of categoryA",
                "homepage": "http:\/\/portA1.website\/",
                "epoch": "0",
                "platforms": "darwin",
                "name": "port-A1-subport",
                "depends_lib": ["lib:pq:port-A2", "port:port-A3-diff"],
                "long_description": "Just a test port written to test something.",
                "license": "MIT",
                "maintainers": [{
                    "email": {
                        "domain": "email.com",
                        "name": "user"
                    },
                    "github": "user"
                }],
                "categories": ["categoryA"],
                "version": "1.0.0",
                "revision": "0"
            }
        ])
        port_status = Port.objects.get(name='port-A1-subport').active
        self.assertEquals(port_status, True)
