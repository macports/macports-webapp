import subprocess
import json

from django.core.management.base import BaseCommand, CommandError

from ports.models import Port, Commit

RSYNC = "rsync://rsync.macports.org/macports//trunk/dports/PortIndex_darwin_16_i386/PortIndex.json"
JSON_FILE = "portindex.json"


class Command(BaseCommand):

    help = "Populates the database with Initial data after fetching portindex.json from rsync"

    def handle(self, *args, **options):
        # Fetch from rsync
        subprocess.call(['/usr/bin/rsync', RSYNC, JSON_FILE])

        # Open the file
        with open(JSON_FILE, "r", encoding='utf-8') as file:
            data = json.load(file)

        Port.load(data['ports'])
        Commit.objects.create(hash=data['info']['commit'])
