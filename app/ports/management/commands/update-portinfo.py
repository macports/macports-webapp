from django.core.management.base import BaseCommand, CommandError

from parsing_scripts import git_update
from ports.models import Port, LastPortIndexUpdate


class Command(BaseCommand):
    help = "Populates the database with Initial data from portindex.json file"

    def add_arguments(self, parser):
        parser.add_argument('new_commit',
                            nargs='?',
                            default=None,
                            help="Define a commit till which the update should be processed")
        parser.add_argument('old_commit',
                            nargs='?',
                            default=None,
                            help="Not recommended. Helps you provide a commit from which update should start")

    def handle(self, *args, **options):
        # Fetch the latest version of PortIndex.json and open the file
        data = Port.PortIndexUpdateHandler().sync_and_open_file()

        # If new commit argument is not provided, use the commit-hash from JSON file:
        if options['new_commit'] is None:
            new_commit = data['info']['commit']
        # If argument is provided
        else:
            new_commit = options['new_commit']

        # If old commit argument is not provided, use the commit from the database
        if options['old_commit'] is None:
            try:
                old_commit_object = LastPortIndexUpdate.objects.all().first()
                old_commit = old_commit_object.git_commit_hash
            except AttributeError:
                return 1  # The command should not proceed if no old commit could be located.
        else:
            old_commit = options['old_commit']

        updated_portdirs = git_update.get_list_of_changed_ports(new_commit, old_commit)

        # Using the received list of port names, find related JSON objects
        ports_to_be_updated_json = []
        found_ports_tree = {}
        for port in data['ports']:
            portdir = port['portdir'].lower()
            portname = port['name'].lower()
            if portdir in updated_portdirs:
                ports_to_be_updated_json.append(port)
                if found_ports_tree.get(portdir) is None:
                    found_ports_tree[portdir] = {}
                found_ports_tree[portdir][portname] = True

        # Mark deleted ports
        Port.mark_deleted(found_ports_tree)

        # Run updates
        Port.update(ports_to_be_updated_json)

        # Write the commit hash into database
        LastPortIndexUpdate.update_or_create_first_object(data['info']['commit'])
