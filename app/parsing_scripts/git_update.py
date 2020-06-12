import os
import subprocess
import sys
import io
import shutil
import json

import django

from port.models import LastPortIndexUpdate
import config
from settings import BASE_DIR

sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'MacPorts.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MacPorts.settings")

django.setup()


def rebuild_repo(directory, url, name):
    # remove the existing repo directory, if available
    if os.path.isdir(directory):
        shutil.rmtree(url)

    # cd into the data directory
    os.chdir(config.DATA_DIR)

    # clone the repo
    subprocess.run([config.GIT, 'clone', '--quiet', url, name])


def refresh_portindex_json():
    # check if the contrib repo is available
    if not os.path.isdir(config.MACPORTS_CONTRIB_DIR):
        rebuild_repo(config.MACPORTS_CONTRIB_DIR, config.MACPORTS_CONTRIB_URL, config.MACPORTS_CONTRIB)

    # check if the ports repo is available
    if not os.path.isdir(config.MACPORTS_PORTS_DIR):
        rebuild_repo(config.MACPORTS_PORTS_DIR, config.MACPORTS_PORTS_URL, config.MACPORTS_PORTS)

    # cd into ports directory
    os.chdir(config.MACPORTS_PORTS_DIR)

    # update the ports repo
    subprocess.call([config.GIT, 'pull', '--quiet'])
    latest_commit = subprocess.run([config.GIT, 'rev-parse', 'HEAD'], stdout=subprocess.PIPE).stdout.decode('utf-8')

    # update/generate the portindex
    subprocess.run(['portindex'])

    # update/generate portindex.json
    portindexjson = subprocess.run([config.TCLSH, config.PORTINDEX2JSON, config.LOCAL_PORTINDEX, '--info', 'commit={}'.format(latest_commit)], stdout=subprocess.PIPE).stdout.decode('utf-8')
    portindexjson = json.loads(portindexjson)
    with open(config.LOCAL_PORTINDEX_JSON, 'w') as file:
        json.dump(portindexjson, file)

    # match the latest commit from the repo and the portindex.json match
    if latest_commit != portindexjson.get('info', {}).get('commit'):
        # if they don't match, we should abort the operation
        raise KeyError

    return latest_commit


def get_old_commit():
    # first search in database
    old_commit_obj = LastPortIndexUpdate.objects.all().first()
    if old_commit_obj is None:
        old_commit = None
    else:
        old_commit = old_commit_obj.git_commit_hash

    return old_commit


def get_updated_portdirs():
    # update portindex.json and get new commit
    new_commit = refresh_portindex_json()
    old_commit = get_old_commit()

    # cd into the ports repository
    os.chdir(config.MACPORTS_PORTS_DIR)

    # generate the range of commits to find updated paths
    range_commits = str(old_commit).strip() + "^.." + str(new_commit).strip()

    changed_paths = subprocess.run([config.GIT, 'diff', '--name-only', range_commits], stdout=subprocess.PIPE).stdout.decode('utf-8')
    s = io.StringIO(changed_paths)
    updated_ports_dir = set()

    # loop over all the paths and find portdirs to update
    for line in s:
        sections = line.split('/')
        if len(sections) < 2:
            # ignore updates in the root directory
            continue
        portdir = sections[0].lower() + '/' + sections[1].lower()
        updated_ports_dir.add(portdir)

    os.chdir(BASE_DIR)
    return updated_ports_dir


def get_portindex_json():
    if os.path.isfile(config.LOCAL_PORTINDEX_JSON):
        with open(config.LOCAL_PORTINDEX_JSON, "r", encoding='utf-8') as file:
            data = json.load(file)
        return data
    else:
        return {}
