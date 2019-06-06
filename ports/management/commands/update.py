from django.core.management.base import BaseCommand, CommandError

from parsing_scripts import update


class Command(BaseCommand):

    help = "Populates the database with Initial data from portindex.json file"

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='?', type=str, default='portindex.json')

    def handle(self, *args, **options):
        try:
            ports = update.open_portindex_json(options['path'])
            update.full_update_ports(ports)
            update.full_update_dependencies(ports)
        except FileNotFoundError:
            raise CommandError('"{}" not found. Make sure "{}" is a valid JSON file and is in the root of the project'.format(
                options['path'], options['path']
            ))
