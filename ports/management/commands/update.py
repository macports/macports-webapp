from django.core.management.base import BaseCommand, CommandError
from parsing_scripts import update


class Command(BaseCommand):

    help = "Populates the database with Initial data from portindex.json file"

    def handle(self, *args, **options):
        ports = update.open_portindex_json("portindex.json")
        update.full_update_ports(ports)
        update.full_update_dependencies(ports)
