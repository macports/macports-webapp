import os
import subprocess
import sys
import io
import shutil

import django

from ports.models import LastPortIndexUpdate
from MacPorts.config import MACPORTS_PORTS_DIR, MACPORTS_PORTS_URL, MACPORTS_PORTS, DATA_DIR, GIT
from MacPorts.settings import BASE_DIR

sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'MacPorts.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MacPorts.settings")

django.setup()


def clone_repo():
    os.chdir(DATA_DIR)
    if os.path.isdir(MACPORTS_PORTS_DIR):
        return
    else:
        subprocess.run([GIT, 'clone', '--quiet', MACPORTS_PORTS_URL, MACPORTS_PORTS])


def get_list_of_changed_ports(new_commit=None, old_commit=None):
    # Check if the repository clone is available
    if not os.path.isdir(MACPORTS_PORTS_DIR):
        print('{} directory not found. Cloning into'.format(MACPORTS_PORTS))
        clone_repo()

    print('{} directory found'.format(MACPORTS_PORTS))

    # cd into the repository
    os.chdir(MACPORTS_PORTS_DIR)

    # Check if the repository is healthy.
    try:
        remote = subprocess.run([GIT, 'config', '--get', 'remote.origin.url'],
                                stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
        if remote == MACPORTS_PORTS_URL:
            print("The {} repo is healthy.".format(MACPORTS_PORTS))
        else:
            raise OSError

        # If old_hash is not provided by the user
        if old_commit is None:
            # If the database has old commit, use it for old_hash
            old_commit_object = LastPortIndexUpdate.objects.all().first()
            if old_commit_object is None:
                # If database is empty, use the first commit
                old_commit = subprocess.run([GIT, 'rev-list', 'HEAD', '|', 'tail', '-n', '1'],
                                          stdout=subprocess.PIPE).stdout.decode('utf-8')
            else:
                old_commit = old_commit_object.git_commit_hash

        # Pull from macports-ports
        subprocess.call([GIT, 'pull', '--quiet'])

        # Get new hash if not provided
        if new_commit is None:
            new_commit = subprocess.run([GIT, 'rev-parse', 'HEAD'], stdout=subprocess.PIPE).stdout.decode('utf-8')

        # Generate the range of commits to find updated paths
        range = str(old_commit).strip() + "^.." + str(new_commit).strip()

        changed_paths = subprocess.run([GIT, 'diff', '--name-only', range], stdout=subprocess.PIPE).stdout.decode(
            'utf-8')
        s = io.StringIO(changed_paths)
        updated_ports_dir = set()
        for line in s:
            sections = line.split('/')
            if len(sections) < 2:
                # ignore updates in the root directory
                continue
            portdir = sections[0].lower() + '/' + sections[1].lower()
            if portdir not in updated_ports_dir:
                updated_ports_dir.add(portdir)
        os.chdir(BASE_DIR)
        print(updated_ports_dir)
        return updated_ports_dir

    except OSError:
        os.chdir(DATA_DIR)
        print("{} repository has some error".format(MACPORTS_PORTS))
        print("Cleaning current tree and cloning new repo.")
        shutil.rmtree(MACPORTS_PORTS_DIR)
        clone_repo()
        return get_list_of_changed_ports(new_commit, old_commit)
