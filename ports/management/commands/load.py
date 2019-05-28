from django.core.management.base import BaseCommand, CommandError
from parsing_scripts import load_initial_data

class Command(BaseCommand):

    help = "Populates the database with Initial data from portindex.json file"

    def handle(self, *args, **options):
        ports = load_initial_data.open_portindex_json("portindex.json")
        load_initial_data.load_categories_table(ports)
        load_initial_data.load_ports_and_maintainers_table(ports)
