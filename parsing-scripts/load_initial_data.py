import os, json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MacPorts.settings")

import django

django.setup()

from ports.models import Port, Category, Maintainer, Dependency

with open('portindex.json', "r") as file:
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

# Check if the maintainers are already in the database
    try:
        for maintainer in port['maintainers']:
            temp_maintainer = {}
            github_repeat = False
            email_repeat = False
            github_repeated_at = []
            email_repeated_at = []
            if temp_maintainers == []:
                new_maintainer = Maintainer()
                try:
                    new_maintainer.name = maintainer['email']['name']
                    new_maintainer.domain = maintainer['email']['domain']
                    temp_maintainer['name'] = maintainer['email']['name']
                    temp_maintainer['domain'] = maintainer['email']['domain']
                    email_provided = True
                except KeyError:
                    email_provided = False

                try:
                    new_maintainer.github = maintainer['github']
                    temp_maintainer['github'] = maintainer['github']
                    github_provided = True
                except KeyError:
                    github_provided = False
                new_maintainer.save()
                new_maintainer.ports.add(new_port)
                temp_maintainers.append(temp_maintainer)
                continue
            i = 0
            for check_maintainer in temp_maintainers:
                try:
                    if maintainer['github'] == check_maintainer['github']:
                        github_repeat = True
                        github_repeated_at.append(i)
                        github_provided = True
                except KeyError:
                    github_provided = False

                try:
                    if maintainer['email']['name'] == check_maintainer['name'] and maintainer['email']['domain'] == check_maintainer['domain']:
                        email_repeat = True
                        email_repeated_at.append(i)
                        email_provided = True
                except KeyError:
                    email_provided = False
                i = i + 1

            if github_repeat and email_repeat:
                if bool(set(email_repeated_at).intersection(github_repeated_at)):
                    repeated_maintainer = Maintainer.objects.filter(github=maintainer['github'], name=maintainer['email']['name'])[0]
                    repeated_maintainer.ports.add(new_port)
                    continue
                else:
                    print('Big exception.')
                    new_maintainer = Maintainer()
                    try:
                        new_maintainer.name = maintainer['email']['name']
                        new_maintainer.domain = maintainer['email']['domain']
                        temp_maintainer['name'] = maintainer['email']['name']
                        temp_maintainer['domain'] = maintainer['email']['domain']
                    except:
                        pass
                    try:
                        new_maintainer.domain = maintainer['github']
                        temp_maintainer['github'] = maintainer['github']
                    except:
                        pass
                    new_maintainer.save()
                    temp_maintainers.append(temp_maintainer)
                    new_maintainer.ports.add(new_port)
            elif github_repeat and not email_provided:
                repeated_maintainer = Maintainer.objects.filter(github=maintainer['github'])[0]
                repeated_maintainer.ports.add(new_port)
                continue
            elif email_repeat and not github_provided:
                repeated_maintainer = Maintainer.objects.filter(name=maintainer['email']['name'], domain=maintainer['email']['domain'])[0]
                repeated_maintainer.ports.add(new_port)
                continue
            else:
                new_maintainer = Maintainer()

                try:
                    new_maintainer.name = maintainer['email']['name']
                    new_maintainer.domain = maintainer['email']['domain']
                    temp_maintainer['name'] = maintainer['email']['name']
                    temp_maintainer['domain'] = maintainer['email']['domain']
                except KeyError:
                    pass
                try:
                    new_maintainer.github = maintainer['github']
                    temp_maintainer['github'] = maintainer['github']
                except KeyError:
                    pass
                new_maintainer.save()
                temp_maintainers.append(temp_maintainer)
                new_maintainer.ports.add(new_port)
    except KeyError:
        pass

