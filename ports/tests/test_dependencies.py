from django.test import TestCase, Client
from django.urls import reverse

from ports.models import Dependency
from parsing_scripts import load_initial_data, update


class TestDependencies(TestCase):
    def setUp(self):
        ports = load_initial_data.open_portindex_json("ports/tests/sample_data/portindex.json")
        load_initial_data.load_categories_table(ports)
        load_initial_data.load_ports_and_maintainers_table(ports)
        load_initial_data.load_dependencies_table(ports)

    def test_rows_created(self):
        self.assertEquals(Dependency.objects.all().count(), 4)

    def test_dependencies_fetched(self):
        client = Client()
        response = client.get(reverse('port_detail_summary'), data={'portname': 'port-A1'})
        dependencies = response.context['dependencies']
        self.assertEquals(dependencies.get(type='lib').dependencies.all().count(), 2)
        total_dependencies = []
        for type in dependencies:
            for dependency in type.dependencies.all():
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
        update.full_update_ports(updated_port)
        update.full_update_dependencies(updated_port)
        dependencies = Dependency.objects.filter(port_name__name__iexact='port-A5')
        self.assertEquals(dependencies.get(type='run').dependencies.all().count(), 1)
        self.assertEquals(dependencies.get(type='run').dependencies.all().first().name, 'port-A1')
        self.assertEquals(dependencies.count(), 2)
