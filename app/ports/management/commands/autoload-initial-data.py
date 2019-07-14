from django.core.management.base import BaseCommand, CommandError

from ports.models import Port, LastPortIndexUpdate


class Command(BaseCommand):

    help = "Populates the database with Initial data after fetching portindex.json from rsync"

    def handle(self, *args, **options):
        if not Port.objects.count() > 0:
            # Fetch from rsync
            Port.RsyncHandler().sync()
            # Open the file
            data = Port.RsyncHandler().open_file()

            # Start populating
            Port.load(data['ports'])

            # Write the commit hash into database
            last_commit = LastPortIndexUpdate.objects.all().first()
            if last_commit is None:
                LastPortIndexUpdate.objects.create(git_commit_hash=data['info']['commit'])
            else:
                last_commit.git_commit_hash = data['info']['commit']
                last_commit.save()

            print("Initial Data Loaded Successfully.")
        else:
            print("The database is not empty. Command cannot run.")
