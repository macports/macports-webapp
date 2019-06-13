import os
import subprocess
import sys
import io

import django

from ports.models import Commit

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'MacPorts.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MacPorts.settings")

django.setup()


def clone_repo():
    if os.path.isdir('macports-ports'):
        return
    else:
        os.system("git clone https://github.com/macports/macports-ports.git")


def get_list_of_changed_ports(new_hash=False, old_hash=False):
    if os.path.isdir('macports-ports'):

        # cd to the macports-ports directory
        REPO_DIR = os.path.join(BASE_DIR, 'macports-ports')
        os.chdir(REPO_DIR)

        # If old_hash is not provided by the user
        if old_hash is False:
            try:
                # Try to fetch the most recent hash from database
                old_hash_object = Commit.objects.all().order_by('-updated_at').first()
                old_hash = old_hash_object.hash
            except AttributeError:
                # If database is empty, use the current HEAD
                old_hash = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE).stdout.decode('utf-8')

        # Pull from macports-ports
        os.system('git pull &> /dev/null')

        # Get new hash
        if new_hash is False:
            new_hash = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE).stdout.decode('utf-8')

        # find the range of commits to loop over
        range = str(old_hash).strip() + "^.." + str(new_hash).strip()

        changed_paths = subprocess.run(['git', 'diff', '--name-only', range], stdout=subprocess.PIPE).stdout.decode('utf-8')
        s = io.StringIO(changed_paths)
        updated_ports = []
        for line in s:
            portname = line.split('/')[1]
            if portname not in updated_ports:
                updated_ports.append(portname)

        # Add the new hash to the database
        Commit.objects.create(hash=new_hash)
        os.chdir(BASE_DIR)
        return updated_ports
    else:
        clone_repo()
        get_list_of_changed_ports()
