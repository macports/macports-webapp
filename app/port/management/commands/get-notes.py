from django.core.management.base import BaseCommand

from parsing_scripts import get_notes


class Command(BaseCommand):

    help = "Fetches notes using the 'port notes' command and saves in database"

    def handle(self, *args, **options):
        get_notes.get_notes_all_ports()
