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
        new_port.description = port.get('description')
        new_port.homepage = port.get('homepage')
        new_port.epoch = port.get('epoch')
        new_port.platforms = port.get('platforms')
        new_port.long_description = port.get('long_description')
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
                try:
                    name = maintainer['email']['name'].lower()
                    domain = maintainer['email']['domain'].lower()
                    email_provided = True
                except KeyError:
                    name = None
                    domain = None
                    email_provided = False

                try:
                    github = maintainer['github'].lower()
                    github_provided = True
                except KeyError:
                    github = None
                    github_provided = False

                # Check if the maintainer already exists in Database:
                if email_provided is True and github_provided is True:
                    try:
                        db_maintainer = Maintainer.objects.get(name=name, domain=domain, github=github)
                        db_maintainer.ports.add(new_port)
                        continue
                    except ObjectDoesNotExist:
                        pass
                elif email_provided is False and github_provided is True:
                    try:
                        db_maintainer = Maintainer.objects.get(name__isnull=True, github=github)
                        db_maintainer.ports.add(new_port)
                        continue
                    except ObjectDoesNotExist:
                        pass
                elif email_provided is True and github_provided is False:
                    try:
                        db_maintainer = Maintainer.objects.get(name=name, domain=domain, github__isnull=True)
                        db_maintainer.ports.add(new_port)
                        continue
                    except ObjectDoesNotExist:
                        pass

                # If the maintainer was not found in the database already, then only this code will run:
                new_maintainer = Maintainer()
                new_maintainer.name = name
                new_maintainer.domain = domain
                new_maintainer.github = github
                new_maintainer.save()
                new_maintainer.ports.add(new_port)
        except KeyError:
            pass


def load():
    ports = open_portindex_json()
    load_categories_table(ports)
    load_ports_and_maintainers_table(ports)
    return
