import os
import subprocess
import sys
import io
import shutil

import django

from ports.models import LastPortIndexUpdate
from MacPorts import config
from MacPorts.settings import BASE_DIR

sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'MacPorts.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MacPorts.settings")

django.setup()


def clone_repo():
    os.chdir(config.DATA_DIR)
    if os.path.isdir(config.MACPORTS_PORTS_DIR):
        return
    else:
        subprocess.run([config.GIT, 'clone', config.MACPORTS_PORTS_URL])


def get_list_of_changed_ports(new_hash=False, old_hash=False):
    if os.path.isdir(config.MACPORTS_PORTS_DIR):
        print('{} directory found'.format(config.MACPORTS_PORTS))

        # cd into the repository
        os.chdir(config.MACPORTS_PORTS_DIR)

        # Check if the repository is healthy.
        try:
            remote = subprocess.run([config.GIT, 'config', '--get', 'remote.origin.url'],
                                    stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
            if remote == config.MACPORTS_PORTS_URL:
                print("The {} repo is healthy.".format(config.MACPORTS_PORTS))
            else:
                raise OSError

            # If old_hash is not provided by the user
            if old_hash is False:
                # If the database has old commit, use it for old_hash
                old_hash_object = LastPortIndexUpdate.objects.all().first()
                if old_hash_object is None:
                    # If database is empty, use the first commit
                    old_hash = subprocess.run([config.GIT, 'rev-list', 'HEAD', '|', 'tail', '-n', '1'], stdout=subprocess.PIPE).stdout.decode('utf-8')
                else:
                    old_hash = old_hash_object.git_commit_hash

            # Pull from macports-ports
            subprocess.call([config.GIT, 'pull'])

            # Get new hash if not provided
            if new_hash is False:
                new_hash = subprocess.run([config.GIT, 'rev-parse', 'HEAD'], stdout=subprocess.PIPE).stdout.decode('utf-8')

            # Generate the range of commits to find updated paths
            range = str(old_hash).strip() + "^.." + str(new_hash).strip()

            changed_paths = subprocess.run([config.GIT, 'diff', '--name-only', range], stdout=subprocess.PIPE).stdout.decode(
                'utf-8')
            s = io.StringIO(changed_paths)
            updated_ports = []
            for line in s:
                portname = line.split('/')[1]
                if portname not in updated_ports:
                    updated_ports.append(portname.lower())

            os.chdir(BASE_DIR)
            print(updated_ports)
            return updated_ports

        except OSError:
            os.chdir(config.DATA_DIR)
            print("{} repository has some error".format(config.MACPORTS_PORTS))
            print("Cleaning current tree and cloning new repo.")
            shutil.rmtree(config.MACPORTS_PORTS_DIR)
            clone_repo()
            return get_list_of_changed_ports(new_hash, old_hash)
    else:
        print('{} directory not found. Cloning into'.format(config.MACPORTS_PORTS))
        clone_repo()
        return get_list_of_changed_ports(new_hash, old_hash)
