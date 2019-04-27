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
 - Put the file `portindex.json` in the root of the **project**. To generate this file, you need to run `portindex2json.tcl`.
 - Run `parsing-scripts/load_initial_data.py` to populate the Ports, Categories and Maintainers tables.
 - Run `parsing-scipts/load_initial_depends.py` to load the Dependencies table.
 - Run `parsing-scripts/parse_build_history.py` to fetch few recent builds from the buildbot.

## Start the Server
Start the server after running collectstatic
```
python manage.py collectstatic
```
```
python manage.py runserver
```
 
 
 


 
