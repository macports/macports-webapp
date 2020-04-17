from django.test import TransactionTestCase
from django.core.management import call_command

from ports.models import Port
from config import TEST_PORTINDEX_JSON


class TestUpdatePortinfo(TransactionTestCase):
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
