from django.core.management.base import BaseCommand, CommandError

from ports.models import BuildHistory


class Command(BaseCommand):

    help = "Populates the database with Initial data from portindex.json file"

    def handle(self, *args, **options):
        BuildHistory.Populate().fetch()
