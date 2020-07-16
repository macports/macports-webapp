from django.test import TransactionTestCase, Client
from django.urls import reverse

from port.models import Port, Dependency
from tests import setup


class TestURLsPortDetail(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        setup.setup_test_data()

    def test_port_detail(self):
        response = self.client.get(reverse('port_detail', kwargs={
            'name': 'port-A1'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port/port_basic.html')

    def test_port_summary(self):
        response = self.client.get(reverse('port_details', kwargs={
            'name': 'port-A1'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port/port_details.html')

    def test_port_not_found(self):
        response = self.client.get(reverse('port_detail', kwargs={
            'name': 'testingA404.'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port/exceptions/port_not_found.html')

    def test_port_detail_stats(self):
        response = self.client.get(reverse('port_stats', kwargs={
            'name': 'port-A1'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port/port_stats.html')

    def test_port_detail_builds(self):
        response = self.client.get(reverse('port_builds', kwargs={
            'name': 'port-A1'
        }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='port/port_builds.html')


class TestDependencies(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
        setup.setup_test_data()

    def test_rows_created(self):
        self.assertEquals(Dependency.objects.all().count(), 6)

    def test_updates(self):
        updated_port = [{
            "name": "port-A5",
            "version": "1.0.0",
            "portdir": "categoryA/port-A5",
            "depends_extract": ["bin:port-C1:port-C1"],
            "depends_run": ["port:port-A1"],
        }]
        Port.add_or_update(updated_port)
        dependencies = Dependency.objects.filter(port_name__name__iexact='port-A5')
        self.assertEquals(dependencies.get(type='run').dependencies.all().count(), 1)
        self.assertEquals(dependencies.get(type='run').dependencies.all().first().name, 'port-A1')
        self.assertEquals(dependencies.count(), 2)


class TestPortsQueryAndUpdate(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        setup.setup_test_data()

    def test_deleted(self):
        # mark_deleted function expects everything to be in lower case
        Port.mark_deleted({
            'categorya/port-a1': {
                'port-a1'
            }
        })

        port_status_subport = Port.objects.get(name='port-A1-subport').active
        port_status_mainport = Port.objects.get(name='port-A1').active
        self.assertEquals(port_status_mainport, True)
        self.assertEquals(port_status_subport, False)

    def test_moved(self):
        Port.add_or_update([
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
        Port.add_or_update([
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
        Port.add_or_update([
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
