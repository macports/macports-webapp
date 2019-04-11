import json

with open('portindex.json', "r") as file:
    data = json.load(file)

i = 0
maintainer_fixtures = []
temp_maintainers = []
for port in data:
    for maintainer in port['maintainers']:
        maintainer_object = {}
        repeat = False
        try:
            if temp_maintainers == []:
                maintainer_object['github'] = maintainer['github']
            else:
                for test in temp_maintainers:
                    if maintainer['github'] == test['github']:
                        repeat = True
                        break
            if temp_maintainers != [] and repeat is False:
                maintainer_object['github'] = maintainer['github']
        except:
            pass

        try:
            if temp_maintainers == []:
                maintainer_object['name'] = maintainer['email']['name']
                maintainer_object['domain'] = maintainer['email']['domain']
            else:
                for test in temp_maintainers:
                    if maintainer['email']['name'] == test['name'] and maintainer['email']['domain'] == test['domain']:
                        repeat = True
                        break
            if temp_maintainers != [] and repeat is False:
                maintainer_object['name'] = maintainer['email']['name']
                maintainer_object['domain'] = maintainer['email']['domain']

        except:
            pass


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
