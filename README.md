## Setup the Database
Enter your database credentials in MacPorts/settings.py

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'DATABASE NAME',
        'USER': 'USER NAME',
        'PASSWORD': 'PASSWORD',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
## Make Migrations
 - Make migrations
 ```
 python manage.py makemigrations
 ```
 - Run the migrations
 ```
 python manage.py migrate
 ```
 
## Populate Initial Data in the Database
 - Put the file `portindex.json` or `<filename>` in the root of the project. To generate this file, you need to run `portindex2json.tcl`.
 - Run `python manage.py load <filename>` to populate the Ports, Categories and Maintainers tables. If you do not supply `<filename>`, the default `portindex.json` will be used.
 - Run `python manage.py load-dependencies <filename>` to load the Dependencies table. This command should be ran only after the ports table has been completely populated from the `load` (previous) command.
 - Run `python manage.py fetch-build-history` to fetch few recent builds from the buildbot.

## Start the Server
Start the server after running collectstatic
```
python manage.py collectstatic
```
```
python manage.py runserver
```

## Updating the Database
- Put the new json file in the root of the project.
- Run `python manage.py update <filename>` to update the database.

If you do not supply `<filename>` then the default `portindex.json` will be used. This command supports both differential and full updates, depending upon the nature of the JSON file provided to it.