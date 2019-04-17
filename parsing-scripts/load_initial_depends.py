import os, json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MacPorts.settings")

import django

django.setup()

from ports.models import Dependency, Port


def load_depends(list_of_dependencies, type_of_dependency, port):
    dependency = Dependency()
    dependencies = []
    dependency.type = type_of_dependency
    dependency.port_name = port
    for depends in list_of_dependencies:
        dependencies.append(Port.objects.get(name__exact=depends.rsplit(':', 1)[-1]))
    dependency.save()
    dependency.dependencies.add(*dependencies)


with open('portindex.json', "r") as file:
    ports = json.load(file)

i = 0
fixtures = []
for port in ports:
    iport = Port.objects.get(name__iexact=port['name'])
    # Update Dependencies for the port
    try:
        load_depends(port['depends_lib'], "lib", iport)
    except KeyError:
        pass

    try:
        load_depends(port['depends_extract'], "extract", iport)
    except KeyError:
        pass

    try:
        load_depends(port['depends_run'], "run", iport)
    except KeyError:
        pass

    try:
        load_depends(port['depends_patch'], "patch", iport)
    except KeyError:
        pass

    try:
        load_depends(port['depends_build'], "build", iport)
    except KeyError:
        pass

    try:
        load_depends(port['depends_test'], "test", iport)
    except KeyError:
        pass

    try:
        load_depends(port['depends_patch'], "patch", iport)
    except KeyError:
        pass

    try:
        load_depends(port['depends_fetch'], "fetch", iport)
    except KeyError:
        pass
