from django.core.management.base import BaseCommand, CommandError

from ports.models import Port


class Command(BaseCommand):

    help = "Populates the database with Initial data from portindex.json file"

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='?', type=str, default='portindex.json')

    def handle(self, *args, **options):
        try:
            ports = Port.Load().open_portindex_json(options['path'])
            Port.Load().load_categories_table(ports)
            Port.Load().load_ports_and_maintainers_table(ports)
            Port.Load().load_dependencies_table(ports)
        except FileNotFoundError:
            raise CommandError('"{}" not found. Make sure "{}" is a valid JSON file and is in the root of the project'.format(
                options['path'], options['path']
            ))
