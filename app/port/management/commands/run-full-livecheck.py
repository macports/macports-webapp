from django.core.management.base import BaseCommand

from parsing_scripts import run_livecheck


class Command(BaseCommand):

    help = "Runs livecheck command over all the ports"

    def handle(self, *args, **options):
        run_livecheck.run_livecheck_all()
