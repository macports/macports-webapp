from django.core.management.base import BaseCommand, CommandError

from parsing_scripts import git_update
from ports.models import Port, LastPortIndexUpdate


class Command(BaseCommand):
    help = "Populates the database with Initial data from portindex.json file"

    def add_arguments(self, parser):
        parser.add_argument('new',
                            nargs='?',
                            default=False,
                            help="Define a commit till which the update should be processed")
        parser.add_argument('old',
                            nargs='?',
                            default=False,
                            help="Not recommended. Helps you provide a commit from which update should start")

    def handle(self, *args, **options):
        # Fetch from rsync
        Port.RsyncHandler().sync()

        # Open the file
        data = Port.RsyncHandler().open_file()

        # If no argument is provided, use the commit-hash from JSON file:
        if options['new'] is False:
            new_hash = data['info']['commit']
        # If argument is provided
        else:
            new_hash = options['new']

        # Using the range of commits, find the list of ports which have been updated
        # options['old'] will be false if no argument is provided
        updated_portdirs = git_update.get_list_of_changed_ports(new_hash, options['old'])

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
        if LastPortIndexUpdate.objects.count() > 0:
            last_commit = LastPortIndexUpdate.objects.all().first()
            last_commit.git_commit_hash = data['info']['commit']
            last_commit.save()
        else:
            LastPortIndexUpdate.objects.create(git_commit_hash=data['info']['commit'])
