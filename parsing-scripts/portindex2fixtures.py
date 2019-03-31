import json

with open('portindex.json', "r") as file:
    data = json.load(file)

i = 0
port_fixtures = []
for port in data:
    try:
        categories_list = port['categories'].split(' ')
        port['categories'] = categories_list
    except:
        port['categories'] = ["nocategory"]

    newdata = {
        'model': 'ports.Port',
        'pk': i,
        'fields': port
    }
    port_fixtures.append(newdata)
    i = i + 1

with open('../port_fixtures.json', 'w') as newjson:
    json.dump(port_fixtures, newjson, indent=4)
