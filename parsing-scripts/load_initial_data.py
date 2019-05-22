import os, json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MacPorts.settings")

import django

django.setup()

from ports.models import Port, Category, Maintainer
from django.core.exceptions import ObjectDoesNotExist

with open('/portindex.json', "r") as file:
    ports = json.load(file)

# Add All the Categories to the Database using bulk_create
categories = set()
for port in ports:
    try:
        for category in port['categories']:
            categories.add(Category(name=category))
    except KeyError:
        pass
batch = list(categories)
Category.objects.bulk_create(batch)

temp_maintainers = []  #This is used to compare maintainers without querying the database
for port in ports:

    # Add Ports to the Database One-by-One
    new_port = Port()
    try:
        new_port.portdir = port['portdir']
    except KeyError:
        pass
    try:
        new_port.variants = port['variants']
    except KeyError:
        pass
    try:
        new_port.description = port['description']
    except KeyError:
        pass
    try:
        new_port.homepage = port['homepage']
    except KeyError:
        pass
    try:
        new_port.epoch = port['epoch']
    except KeyError:
        pass
    try:
        new_port.platforms = port['platforms']
    except KeyError:
        pass
    try:
        new_port.long_description = port['long_description']
    except KeyError:
        pass
    try:
        new_port.version = port['version']
    except KeyError:
        pass
    try:
        new_port.revision = port['revision']
    except KeyError:
        pass
    try:
        new_port.closedmaintainer = port['closedmaintainer']
    except KeyError:
        pass
    try:
        new_port.name = port['name']
    except KeyError:
        pass
    try:
        new_port.license = port['license']
    except KeyError:
        pass
    try:
        new_port.installs_libs = port['installs_lib']
    except KeyError:
        pass
    try:
        new_port.replaced_by = port['replaced_by']
    except KeyError:
        pass
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

