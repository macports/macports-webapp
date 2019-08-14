from django.core.management.base import BaseCommand, CommandError

from ports.models import Port, LastPortIndexUpdate, BuildHistory, Builder


class Command(BaseCommand):

    help = "Populates the database with Initial data after fetching portindex.json from rsync"

    def handle(self, *args, **options):
        if Port.objects.count() or Builder.objects.count() > 0:
            raise CommandError("The database is not empty. Command cannot run.")

        # Fetch the latest version of PortIndex.json and open the file
        data = Port.PortIndexUpdateHandler().sync_and_open_file()

        if not data:
            return

        # Start populating
        Port.load(data['ports'])

        # Write the commit hash into database
        last_commit = LastPortIndexUpdate.objects.all().first()
        if last_commit is None:
            LastPortIndexUpdate.objects.create(git_commit_hash=data['info']['commit'])
        else:
            last_commit.git_commit_hash = data['info']['commit']
            last_commit.save()

        # Load the builders
        BuildHistory.populate_builders()

        print("Initial Data Loaded Successfully.")
