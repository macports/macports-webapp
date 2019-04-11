import json

with open('portindex.json', "r") as file:
    data = json.load(file)

i = 0
port_fixtures = []
for port in data:
    maintainers = []
    one_maintainer = []
    for maintainer in port['maintainers']:
        try:
            one_maintainer.append(maintainer['email']['name'])
            one_maintainer.append(maintainer['email']['domain'])
        except:
            continue
        maintainers.append(one_maintainer)
        one_maintainer = []
    port['maintainers'] = maintainers


    newdata = {
        'model': 'ports.Port',
        'pk': i,
        'fields': port
    }
    port_fixtures.append(newdata)
    i = i + 1

with open('../port_fixtures.json', 'w') as newjson:
    json.dump(port_fixtures, newjson, indent=4)
