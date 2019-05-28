from django.core.management.base import BaseCommand, CommandError
from parsing_scripts import load_initial_data


class Command(BaseCommand):

    help = "Populates dependencies for ports"

    def handle(self, *args, **options):
        ports = load_initial_data.open_portindex_json("portindex.json")
        load_initial_data.load_dependencies_table(ports)
