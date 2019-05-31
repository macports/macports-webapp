import os, json, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'MacPorts.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MacPorts.settings")

import django

django.setup()

from ports.models import Port, Maintainer, Category, Dependency, Variant


def open_portindex_json(path='portindex.json'):
    with open(path, "r") as file:
        ports = json.load(file)
    return ports


def full_update_ports(ports):

    for port in ports:
        port_object, port_created = Port.objects.get_or_create(name=port['name'])

        port_object.portdir = port['portdir']
        port_object.version = port['version']
        port_object.description = port.get('description', '')
        port_object.homepage = port.get('homepage', '')
        port_object.epoch = port.get('epoch', 0)
        port_object.platforms = port.get('platforms', '')
        port_object.long_description = port.get('long_description', '')
        port_object.revision = port.get('revision', 0)
        port_object.closedmaintainer = port.get('closedmaintainer', False)
        port_object.license = port.get('license')
        port_object.installs_libs = port.get('installs_lib')
        port_object.replaced_by = port.get('replaced_by')
        port_object.save()

        try:
            port_object.categories.clear()
            for category in port['categories']:
                category_object, category_created = Category.objects.get_or_create(name=category)
                port_object.categories.add(category_object)
        except KeyError:
            pass

        try:
            variant_objects = Variant.objects.filter(port_id=port_object.id)

            for variant_object in variant_objects:
                if variant_object not in port['variants']:
                    variant_object.delete()

            for variant in port['variants']:
                v_obj, created = Variant.objects.get_or_create(port_id=port_object.id, variant=variant)
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


def full_update_dependencies(ports):

    for port in ports:
        try:
            all_dependency_objects = Dependency.objects.filter(port_name__name__iexact=port['name'])
            port_object = Port.objects.get(name=port['name'])

            # Delete the dependency types from database that no longer exist in
            for dependency_object in all_dependency_objects:
                key = "depends_" + dependency_object.type
                if key not in port:
                    dependency_object.delete()

            for dependency_type in ["lib", "extract", "run", "patch", "build", "test", "patch", "fetch"]:
                key = "depends_" + dependency_type
                if key in port:
                    obj, created = Dependency.objects.get_or_create(port_name_id=port_object.id, type=dependency_type)
                    obj.type = dependency_type
                    obj.port_name = port_object
                    obj.dependencies.clear()
                    dependencies = []

                    for depends in port[key]:
                        try:
                            dependencies.append(Port.objects.get(name__iexact=depends.rsplit(':', 1)[-1]))
                        except Port.DoesNotExist:
                            print("Failed to append {} as a dependency to {}. Not Found.".format(depends.rsplit(':', 1)[-1],
                                                                                                 port.name))
                    obj.save()
                    obj.dependencies.add(*dependencies)

        except Port.DoesNotExist:
            print("Failed to update depencies for {}. Port does not exist in the database.".format(port['name']))
