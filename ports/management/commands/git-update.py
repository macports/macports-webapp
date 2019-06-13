from django.core.management.base import BaseCommand, CommandError

from parsing_scripts import git_update


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
        git_update.clone_repo()
        git_update.get_list_of_changed_ports(options['new'], options['old'])

