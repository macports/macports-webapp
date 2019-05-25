from django.test import TestCase
from ports.models import Maintainer, Port, Category, Dependency

from parsing_scripts import load_initial_data


class TestMaintainers(TestCase):
    def test_unique_entries_created(self):
        ports = load_initial_data.open_portindex_json("ports/tests/testindex.json")
        load_initial_data.load_categories_table(ports)
        load_initial_data.load_ports_and_maintainers_table(ports)
        self.assertEquals(Maintainer.objects.count(), 5, "Failed to create unique entities for maintainers")



