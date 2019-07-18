# Introduction

### Goal

This is a web application that:
 1. Displays general information about all the ports.
 2. Fetches and displays build history of the ports.
 3. Collects and displays installation statistics (system configurations and installed ports) from users who opt-in by
    installing the port `mpstats-gsoc`.
    
It aims at being an all-one-place for users to find relevant ports and for maintainers to monitor their ports and
understand their user base.
 
More info at [docs/1-INFORMATION.md](docs/1-INTRODUCTION.md)

### Architecture

The web application is based on the [Django Framework](http://djangoproject.com) utilising a PostgreSQL database.

The app is supposed to be deployed in a docker container with nginx and uWSGI serving the content.

**Demo**: [AWS EC2](http://ec2-52-34-234-111.us-west-2.compute.amazonaws.com) (running a docker container)
 
This web application has been implemented during the [Google Summer of Code 2019](https://summerofcode.withgoogle.com) 
mentored by the [MacPorts](https://www.macports.org) organisation.

**Student**: [Arjun Salyan](https://github.com/arjunsalyan) <br>
**Mentors**: [Mojca Miklavec](https://github.com/mojca), [Umesh Singla](https://github.com/umeshksingla) <br>

___

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

After the image has been built or pulled, run it using an an env file that contains environment variables. Create a file
`env` in the root of the project and supply the information as shown in the format below. A sample `env` file is
supplied in the root of the repository: `env.sample`, you may rename it to `env` and insert the values to the variables.

**env**: *(Contains environment variables)*

```
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT= [default:'5432']
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

## 2. Run Without Docker
The `/app` directory is a standalone Django-app which can be run normally like any other django application.

### Setup the Database
For security reasons, we discourage writing the database credentials into the `app/MacPorts/settings.py` file. It is
recommended that you setup environment variables to connect to the app. The app requires following environment variables:

```
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
SECRET_KEY=
```

The variables are self explanatory. Use them to connect to your database.

If you do not want to supply environment variables then you may directly supply these credentials in the settings file:
`app/MacPorts/settings.py` (not recommended).

### Make Migrations
 - Make migrations
 
 ```
 python3 manage.py makemigrations
 
 ```
 - Run the migrations
 
 ```
 python3 manage.py migrate
 ```
 
### Populate Initial Data in the Database
 - Put the file `portindex.json` or `<filename>` in the root of the project. To generate this file, you need to run `portindex2json.tcl`.
 - Run `python3 manage.py load <filename>` to populate the Ports, Categories and Maintainers tables. If you do not supply `<filename>`, the default `portindex.json` will be used.
 - Run `python3 manage.py fetch-build-history` to fetch few recent builds from the buildbot.

### Start the Server
Start the server after running collectstatic

```
python3 manage.py collectstatic
```
```
python3 manage.py runserver
```

### Updating the Database
- Put the new json file in the root of the project.
- Run `python3 manage.py update <filename>` to update the database.

If you do not supply `<filename>` then the default `portindex.json` will be used. This command supports both differential and full updates, depending upon the nature of the JSON file provided to it.