import os, json, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'MacPorts.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MacPorts.settings")

import django

django.setup()

from ports.models import Port, Maintainer, Category
from django.core.exceptions import ObjectDoesNotExist


def open_portindex_json(path='portindex.json'):
    with open(path, "r") as file:
        ports = json.load(file)
    return ports


# Add All the Categories to the Database using bulk_create
def load_categories_table(ports):
    categories = set()
    for port in ports:
        try:
            for category in port['categories']:
                categories.add(Category(name=category))
        except KeyError:
            pass
    batch = list(categories)
    Category.objects.bulk_create(batch)
    return


def load_ports_and_maintainers_table(ports):
    for port in ports:

        # Add Ports to the Database One-by-One
        new_port = Port()
        try:
            new_port.name = port['name']
            new_port.portdir = port['portdir']
            new_port.version = port['version']
        except KeyError:
            continue

        new_port.variants = port.get('variants')
        new_port.description = port.get('description', '')
        new_port.homepage = port.get('homepage', '')
        new_port.epoch = port.get('epoch', 0)
        new_port.platforms = port.get('platforms')
        new_port.long_description = port.get('long_description', '')
        new_port.revision = port.get('revision', 0)
        new_port.closedmaintainer = port.get('closedmaintainer')
        new_port.license = port.get('license')
        new_port.installs_libs = port.get('installs_lib')
        new_port.replaced_by = port.get('replaced_by')
        new_port.save()

        try:
            new_port.categories.add(*port['categories'])
        except KeyError:
            pass

        try:
            for maintainer in port['maintainers']:
                name = maintainer.get('email', {}).get('name', '')
                domain = maintainer.get('email', {}).get('domain', '')
                github = maintainer.get('github', '')

                maintainer_object, created = Maintainer.objects.get_or_create(
                    name=name,
                    domain=domain,
                    github=github
                )

                maintainer_object.ports.add(new_port)
        except KeyError:
            pass


def load():
    ports = open_portindex_json()
    load_categories_table(ports)
    load_ports_and_maintainers_table(ports)
    return
