import os
import json
import sys

import django

from ports.models import Port, Maintainer, Category, Dependency, Variant

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'MacPorts.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MacPorts.settings")

django.setup()


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

        new_port.description = port.get('description', '')
        new_port.homepage = port.get('homepage', '')
        new_port.epoch = port.get('epoch', 0)
        new_port.platforms = port.get('platforms')
        new_port.long_description = port.get('long_description', '')
        new_port.revision = port.get('revision', 0)
        new_port.closedmaintainer = port.get('closedmaintainer', False)
        new_port.license = port.get('license', '')
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

        try:
            for variant in port['variants']:
                variant_object = Variant()
                variant_object.port = new_port
                variant_object.variant = variant
                variant_object.save()
        except KeyError:
            pass


def load_dependencies_table(ports):

    def load_depends(list_of_dependencies, type_of_dependency, port):
        dependency = Dependency()
        dependencies = []
        dependency.type = type_of_dependency
        dependency.port_name = port
        for depends in list_of_dependencies:
            try:
                dependencies.append(Port.objects.get(name__iexact=depends.rsplit(':', 1)[-1]))
            except Port.DoesNotExist:
                print("Failed to append {} as a dependency to {}. Not Found.".format(depends.rsplit(':', 1)[-1],
                                                                                     port.name))
        dependency.save()
        dependency.dependencies.add(*dependencies)

    for port in ports:
        try:
            port_object = Port.objects.get(name__iexact=port['name'])
            for dependency_type in ["lib", "extract", "run", "patch", "build", "test", "fetch"]:
                key = "depends_" + dependency_type
                if key in port:
                    load_depends(port[key], dependency_type, port_object)

        except Port.DoesNotExist:
            print("Failed to update dependencies for {}. Port not found in database.".format(port['name']))


def load():
    ports = open_portindex_json()
    load_categories_table(ports)
    load_ports_and_maintainers_table(ports)
    return
