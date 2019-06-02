from django.core.management.base import BaseCommand, CommandError

from parsing_scripts import parse_build_history


class Command(BaseCommand):

    help = "Populates the database with Initial data from portindex.json file"

    def handle(self, *args, **options):
        parse_build_history.fetch()
