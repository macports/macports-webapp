import json

with open('portindex.json', "r") as file:
    data = json.load(file)

i = 0
maintainer_fixtures = []
temp_maintainers = []
for port in data:
    for maintainer in port['maintainers']:
        try:
            name = maintainer['email']['name']
            domain = maintainer['email']['domain']
            email_provided = True
        except KeyError:
            email_provided = False

        try:
            github = maintainer['github']
            github_provided = True
        except KeyError:
            github_provided = False

        maintainer_object = {}  # Define empty maintainer Object
        github_repeat = False
        email_repeat = False

        # If this is first entry, add to the list
        if temp_maintainers == []:  # Making the First Entry
            print('reached empty once')
            if github_provided:
                maintainer_object['github'] = github
            if email_provided:
                maintainer_object['name'] = name
                maintainer_object['domain'] = domain

        # If not first entry, check for uniqueness
        j = 0
        for check in temp_maintainers:
            if email_provided:
                try:
                    if check['name'] == name and check['domain'] == domain:
                        email_repeated_at = j
                        email_repeat = True
                except KeyError:
                    pass
            if github_provided:
                try:
                    if check['github'] == github:
                        github_repeat = True
                        github_repeated_at = j
                except KeyError:
                    pass
            j = j + 1
            if github_repeat and email_repeat:
                break

        # First Case, neither GitHub not email is repeated
        if github_repeat is False and email_repeat is False and temp_maintainers != []:
            if github_provided:
                maintainer_object['github'] = github
            if email_provided:
                maintainer_object['name'] = name
                maintainer_object['domain'] = domain

        # Second Case, both are repeated at the same place ( can be skipped )
        elif github_repeat and email_repeat and github_repeated_at == email_repeated_at:
            continue

        # Third Case, Github is repeated but not the provided email ( same github handle has different emails )
        elif github_repeat and email_repeat is False and email_provided:
            maintainer_object['github'] = github
            maintainer_object['inconsistency'] = True
            maintainer_object['name'] = name
            maintainer_object['domain'] = domain

        # Fourth Case, Email is repeated but not the provided GitHub handle ( create new entry )
        elif email_repeat and github_repeat is False and github_provided:
            maintainer_object['name'] = name
            maintainer_object['domain'] = domain
            maintainer_object['github'] = github
            maintainer_object['inconsistency'] = True

        # Fifth Case, Github is repeated and Email is not provided (skip)
        elif github_repeat and email_provided is False:
            continue

        # Sixth Case, Email is repeated and Github is not provided (skip)
        elif email_repeat and github_provided is False:
            continue

        if maintainer_object != {}:
            newdata = {
                'model': 'ports.Maintainer',
                'pk': i,
                'fields': maintainer_object
            }
            maintainer_fixtures.append(newdata)
            i = i + 1
            temp_maintainers.append(maintainer_object)

with open('../maintainer_fixtures.json', 'w') as newjson:
    json.dump(maintainer_fixtures, newjson, indent=4)
