from django.core.management.base import BaseCommand, CommandError

from parsing_scripts import git_update
from port.models import Port, LastPortIndexUpdate


class Command(BaseCommand):
    help = "Updates the ports table by getting list of updated ports using git."

    def add_arguments(self, parser):
        parser.add_argument('--type',
                            type=str,
                            default="update",
                            help="Specify the type of operation, update or full.")

    def handle(self, *args, **options):
        type_of_run = options['type']

        if type_of_run == 'full':
            git_update.refresh_portindex_json()
            data = git_update.get_portindex_json()
            if data is None:
                raise CommandError("Failed to parse portindex.json")
            Port.add_or_update(data['ports'])
            Port.mark_deleted_full_run(data['ports'])
            LastPortIndexUpdate.update_or_create_first_object(data['info']['commit'])
            return

        # It is an incremental update
        # An incremental update is only possible when the database has a
        # history of the commit till which it is up to date
        old_commit_object = LastPortIndexUpdate.objects.all().first()
        if old_commit_object is None:
            raise CommandError("Failed to run incremental update. No old commit found, cannot generate range of commits.")

        updated_portdirs = git_update.get_updated_portdirs()

        # fetch the latest version of PortIndex.json and open the file
        data = git_update.get_portindex_json()
        if data is None:
            raise CommandError("Failed to parse portindex.json")

        # Generate a dictionary containing all the portdirs and initialise their values
        # with empty sets. The set would contain the ports under that portdir.
        dict_of_portdirs_with_ports = {}
        for portdir in updated_portdirs:
            dict_of_portdirs_with_ports[portdir] = set()

        # Using the received set of updated portdirs, find corresponding JSON objects for all ports under
        # that portdir.
        ports_to_be_updated_json = []
        for port in data['ports']:
            portdir = port['portdir'].lower()
            portname = port['name'].lower()
            if portdir in updated_portdirs:
                ports_to_be_updated_json.append(port)
                dict_of_portdirs_with_ports[portdir].add(portname)

        # Mark deleted ports
        Port.mark_deleted(dict_of_portdirs_with_ports)

        # Run updates
        Port.add_or_update(ports_to_be_updated_json)

        # Write the commit hash into database
        LastPortIndexUpdate.update_or_create_first_object(data['info']['commit'])
