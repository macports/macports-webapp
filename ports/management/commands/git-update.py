from django.core.management.base import BaseCommand, CommandError

from parsing_scripts import git_update


class Command(BaseCommand):
    help = "Populates the database with Initial data from portindex.json file"

    def handle(self, *args, **options):
        git_update.clone_repo()
        git_update.get_list_of_changed_ports()

