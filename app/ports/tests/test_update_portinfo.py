import os

from django.test import TransactionTestCase
from django.core.management import call_command

from ports.models import Port
from MacPorts.config import TEST_PORTINDEX_JSON


class TestUpdatePortinfo(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        Port.load(TEST_PORTINDEX_JSON)

    def test_updates(self):
        call_command('update-portinfo', '3c6f37828d091670e7b9a2676757b2e468ee3d52', 'cb7086953124c73ffb616e955653176e3c4be02c')
        self.assertEquals(Port.objects.count(), 14)

    def test_deleted(self):
        Port.mark_deleted({
            'categoryA/port-A1': {
                'port-A1': True
            }
        })

        port_status = Port.objects.get(name='port-A1-subport').active
        for port in Port.objects.all():
            print(port.name)
        self.assertEquals(port_status, False)

    def test_added_back(self):
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
