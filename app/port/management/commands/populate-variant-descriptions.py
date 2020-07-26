from django.core.management.base import BaseCommand

from parsing_scripts import populate_variant_descriptions


class Command(BaseCommand):

    help = "Populate variant descriptions for the ports"

    def handle(self, *args, **options):
        populate_variant_descriptions.populate_variant_descriptions_all_ports()
