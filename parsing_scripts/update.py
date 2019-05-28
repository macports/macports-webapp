import os, json, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'MacPorts.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MacPorts.settings")

import django

django.setup()

from ports.models import Port, Maintainer, Category, Dependency


def open_portindex_json(path='portindex.json'):
    with open(path, "r") as file:
        ports = json.load(file)
    return ports


def full_update_ports(ports):

    Maintainer.objects.all().delete()

    for port in ports:
        port_object, port_created = Port.objects.get_or_create(name=port['name'])

        port_object.portdir=port['portdir']
        port_object.version=port['version']
        port_object.variants=port.get('variants', '')
        port_object.description=port.get('description', '')
        port_object.homepage=port.get('homepage', '')
        port_object.epoch=port.get('epoch', 0)
        port_object.platforms=port.get('platforms', '')
        port_object.long_description=port.get('long_description', '')
        port_object.revision=port.get('revision', 0)
        port_object.closedmaintainer=port.get('closedmaintainer', False)
        port_object.license=port.get('license')
        port_object.installs_libs=port.get('installs_lib')
        port_object.replaced_by=port.get('replaced_by')
        port_object.save()

        try:
            port_object.categories.clear()
            for category in port['categories']:
                category_object, category_created = Category.objects.get_or_create(name=category)
                port.categories.add(category_object)
        except KeyError:
            pass

        try:
            port_object.maintainers.clear()
            for maintainer in port['maintainers']:
                name = maintainer.get('email', {}).get('name', '')
                domain = maintainer.get('email', {}).get('domain', '')
                github = maintainer.get('github', '')

                maintainer_object, created = Maintainer.objects.get_or_create(
                    name=name,
                    domain=domain,
                    github=github
                )

                maintainer_object.ports.add(port_object)
        except KeyError:
            pass
