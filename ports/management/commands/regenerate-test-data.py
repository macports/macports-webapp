import os

from django.core.management.base import BaseCommand

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKING_DIR = os.path.join(BASE_DIR, "..", "tests", "sample_data")
os.chdir(WORKING_DIR)


class Command(BaseCommand):

    help = "Regenerates portindex.json in ports/tests/sample_data for testing."

    def handle(self, *args, **options):
        os.system("portindex")
        os.system("tclsh portindex2json.tcl portindex > portindex.json")
