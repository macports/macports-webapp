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
 
## Generate Fixtures
 - Required files and parsing scripts can be found in the directory "sample-data".
 - Run portindex2fixtures.py so to generate django fixtures from PortIndex.JSON, new file **port_fixtures.json"** will be saved in the root of the project.
 - Run **parse_build_history.py** to receive a few latest logs from buildbot and save into the database.
 
## Populate the database with fixtures
 - You will now have two files in the root containing fixtures for the Categories and Ports Tables.
 - The files are ***categories.json*** and ***port_fixtures.json***

Populate the database by following commands:
```
python manage.py loaddata categories.json
python manage.py loaddata port_fixtures.json
```

## Start the Server
Start the server after running collectstatic
```
python manage.py collectstatic
```
```
python manage.py runserver
```
 
 
 


 
