from django.core.management.base import BaseCommand

from buildhistory.models import BuildHistory


class Command(BaseCommand):

    help = "Fetches the build history from the Buildbot for each builder"

    def handle(self, *args, **options):
        BuildHistory.populate()
