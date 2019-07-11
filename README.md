# Running the App
The repository contains Docker configuration which can be used out of the box, however, the app can be run without using
the docker container. Both way are discussed below:

## 1. Run inside Docker Container
It is the recommended way, the Docker Image of the app is pre-configured to run the `migrations` and `collectstatic`.
However, the `load` command to populate the database and the crons need to be run manually.

The image can be built locally or can be pulled from Docker Hub:

```
docker pull arjunsalyan/macports-webapp
```
or build the image
```
docker build -t macports-webapp .
```

After the image has been build or pulled, run it using an an env file that contains environment variables. Create a file
`env` in the root of the project and supply the following information.

**env**: *(Contains environment variables)*
```
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
SECRET_KEY=
```

Now run the image:
```
docker run -d -p 80:80 --env-file=env macports-webapp
```

To start the cron jobs:

```
docker exec <container-id> supervisorctl start cron
```
All other commands supported by the app can be run using:
```
docker exec <container-id> [command]
```
where example of [command] may be: `python3 /code/app/manage.py load`.

## 2. Run Without Docker
The `/app` directory is a standalone Django-app which can be run normally like any other django application.
### Setup the Database
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
### Make Migrations
 - Make migrations
 ```
 python manage.py makemigrations
 ```
 - Run the migrations
 ```
 python manage.py migrate
 ```
 
### Populate Initial Data in the Database
 - Put the file `portindex.json` or `<filename>` in the root of the project. To generate this file, you need to run `portindex2json.tcl`.
 - Run `python manage.py load <filename>` to populate the Ports, Categories and Maintainers tables. If you do not supply `<filename>`, the default `portindex.json` will be used.
 - Run `python manage.py fetch-build-history` to fetch few recent builds from the buildbot.

### Start the Server
Start the server after running collectstatic
```
python manage.py collectstatic
```
```
python manage.py runserver
```

### Updating the Database
- Put the new json file in the root of the project.
- Run `python manage.py update <filename>` to update the database.

If you do not supply `<filename>` then the default `portindex.json` will be used. This command supports both differential and full updates, depending upon the nature of the JSON file provided to it.