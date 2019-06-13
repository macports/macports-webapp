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


def get_list_of_changed_ports():
    if os.path.isdir('macports-ports'):

        # cd to the macports-ports directory
        REPO_DIR = os.path.join(BASE_DIR, 'macports-ports')
        os.chdir(REPO_DIR)

        old_hash = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE).stdout.decode('utf-8')


        #Check if database also is at old_hash:
        # old_hash_in_database = Commit.objects.all().order_by('-updated_at').first()
        # if old_hash_in_database.hash == old_hash:
        #    print("Database and old hash are at same level.")
        # else:
        #     print("Database and the old hash are not at same commit.")


        # Pull from macports-ports
        os.system('git pull')

        # Get new hash
        new_hash = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE).stdout.decode('utf-8')

        # find the range of commits to loop over
        range = str(old_hash).strip() + "..." + str(new_hash).strip()

        changed_paths = subprocess.run(['git', 'diff', '--name-only', range], stdout=subprocess.PIPE).stdout.decode('utf-8')
        s = io.StringIO(changed_paths)
        updated_ports = []
        for line in s:
            portname = line.split('/')[1]
            if portname not in updated_ports:
                updated_ports.append(portname)

        print(updated_ports)

        # Add the new hash to the database
        Commit.objects.create(hash=new_hash)
    else:
        clone_repo()
        get_list_of_changed_ports()
