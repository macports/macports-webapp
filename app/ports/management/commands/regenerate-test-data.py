import os

from django.core.management.base import BaseCommand

from config import TEST_SAMPLE_DATA, PORTINDEX2JSON, TEST_PORTINDEX_JSON, TCLSH

os.chdir(TEST_SAMPLE_DATA)


class Command(BaseCommand):

    help = "Regenerates portindex.json in ports/tests/sample_data for testing."

    def handle(self, *args, **options):
        os.system("portindex")
        os.system("{} {} portindex > {}".format(TCLSH, PORTINDEX2JSON, TEST_PORTINDEX_JSON))
