import os
import subprocess
import sys
import io
import shutil

import django

from ports.models import LastPortIndexUpdate
import MacPorts.config as config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'MacPorts.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MacPorts.settings")

django.setup()


def clone_repo():
    if os.path.isdir(config.REPO):
        return
    else:
        os.system("git clone %s" % config.REPO_URL)


def get_list_of_changed_ports(new_hash=False, old_hash=False, root=BASE_DIR):
    os.chdir(root)

    if os.path.isdir(config.REPO):
        print('{} directory found'.format(config.REPO))

        # cd into the macports-ports directory
        REPO_DIR = os.path.join(root, config.REPO)
        os.chdir(REPO_DIR)

        # Check if the repository is healthy.
        try:
            remote = subprocess.run(['git', 'config', '--get', 'remote.origin.url'],
                                    stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
            if remote == config.REPO_URL:
                print("The {} repo is healthy.".format(config.REPO))
            else:
                raise OSError

            # If old_hash is not provided by the user
            if old_hash is False:

                # If the database has old commit, use it for old_hash
                if LastPortIndexUpdate.objects.count() > 0:
                    old_hash_object = LastPortIndexUpdate.objects.all().first()
                    old_hash = old_hash_object.git_commit_hash
                else:
                    # If database is empty, use the first commit
                    old_hash = subprocess.run(['git', 'rev-list', 'HEAD', '|', 'tail', '-n', '1'], stdout=subprocess.PIPE).stdout.decode(
                            'utf-8')

            # Pull from macports-ports
            subprocess.call(['git', 'pull'])

            # Get new hash if not provided
            if new_hash is False:
                new_hash = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE).stdout.decode('utf-8')

            # Generate the range of commits to find updated paths
            range = str(old_hash).strip() + "^.." + str(new_hash).strip()

            changed_paths = subprocess.run(['git', 'diff', '--name-only', range], stdout=subprocess.PIPE).stdout.decode(
                'utf-8')
            s = io.StringIO(changed_paths)
            updated_ports = []
            for line in s:
                portname = line.split('/')[1]
                if portname not in updated_ports:
                    updated_ports.append(portname.lower())

            os.chdir(BASE_DIR)
            return updated_ports

        except OSError:
            os.chdir(root)
            print("{} repository has some error".format(config.REPO))
            print("Cleaning current tree and cloning new repo.")
            shutil.rmtree(config.REPO)
            clone_repo()
            return get_list_of_changed_ports(new_hash, old_hash, root)
    else:
        print('{} directory not found. Cloning into'.format(config.REPO))
        clone_repo()
        return get_list_of_changed_ports(new_hash, old_hash, root)
