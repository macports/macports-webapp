## Setting up the ports webapp

For testing and development purposes, the ports webapp can be deployed and populated locally. The main Django app is contained
inside the `app` directory in the root of the project.

###### Project structure
```
|-- app     (main django app)
|-- config
|-- docs
|-- .gitignore
|-- .gitmodules
|-- .travis.yml
|-- Dockerfile
|-- env.sample
|-- LICENSE
|-- README.md
```

As mentioned, the `app` directory is a standalone django app. However, the app has been Dockerised and all the pain of
setting up a local environment can be avoided when working with Docker. But in case you do not want to work with Docker,
we will also walk through the standard process of setting up the app.

## Getting the dependencies ready

The external dependencies of the app are: PostgreSQL, Solr and Memcached. The search page(/search/) is completely derived from
Solr. Memcached is optional, and can be avoided if you don't want to cache the results of stats and trac tickets.

If you are new to these technologies, you may use the instructions provided below, otherwise you are free to install and setup these
dependencies using your preferred mechanism.

### PostgreSQL
Either download and install Postgres.app from [here](https://postgresapp.com/downloads.html) or via MacPorts:
`sudo port install postgresql13 postgresql13-server`

After this, connect as root:
```bash
su - postgres
```

Create your user(replace username and password with your preferred credentials):
```bash
CREATE USER username PASSWORD 'password';
```

Create a new database;

```bash
CREATE DATABASE webapp;
```

Grant permissions to your user on this database.

```bash 
GRANT ALL PRIVILEGES ON DATABASE webapp TO username;
```

That's it for PostgreSQL, our database for the app is ready.

### Solr

To get the required version of Solr working we need [openjdk8](https://openjdk.java.net/install/). On a mac, you may use 
[MacPorts to install openjdk8](https://ports.macports.org/port/openjdk8/). New versions of openjdk may raise problems,
we recommend openjdk8.

Once opendjk8 has been installed, we can proceed to downloading and launching Solr. We would need 
[Solr 6.6.6](https://archive.apache.org/dist/lucene/solr/6.6.6/). The below steps are self explanatory:

```bash
curl -LO https://archive.apache.org/dist/lucene/solr/6.6.6/solr-6.6.6.tgz
mkdir solr
tar -C solr -xf solr-6.6.6.tgz --strip-components=1
cd solr
./bin/solr start                                    # start solr
./bin/solr create -c tester -n basic_config         # create core named 'tester'
```

By default this will create a core with a managed schema. This setup is dynamic but not useful for the app, later we will
configure solr to use a static schema, which we will generate with the help of `django-haystack`.

### Memcached (optional)

Setting up memcached is straightforward. On Linux:

```bash
wget http://memcached.org/latest
tar -zxvf memcached-1.x.x.tar.gz             # replace 1.x.x with the version that is downloaded
cd memcached-1.x.x
./configure && make && make test && sudo make install
```

Now you may start memcached by running `memcached -d` in the terminal.

On a mac, you may use [MacPorts to install memcached](https://ports.macports.org/port/memcached/summary).

---

We have the dependencies ready now and are ready to move forward to actually setting up the application.

## Setup using Docker

There are two options available:

- Build the docker image from source. (long but useful for development)
- Download an image from the Docker registry. (ready to go in one command)

### 1.a: Building the image from source

 - Clone the repository **(for development, it is recommended that you clone a fork of the repository)**.
    ```bash
    git clone https://github.com/macports/macports-webapp.git
    cd macports-webapp
    ```
 - Build the docker image
    ```bash
    docker build -t macports-webapp .
    ```
 - Once build finishes, the image is ready to run.
 
### 1.b: Downloading image from Docker registry

This is rather simple, but useless if your purpose is development as you won't be able to test your changes.

```bash
docker pull arjunsalyan/macports-webapp
```

### 2. Starting the container

After using any one of the methods described in (1.a) or (1.b), you have an image with you. We will start this image with
several environment variables that are needed to connect to PostgreSQL, Solr and memcached. A file `env.sample` has been
added in the repo for your convenience.

```bash
DB_NAME=                            (name of our database, webapp)
DB_USER=                            (username of the database user)
DB_PASSWORD=                        (password for your database user)
DB_HOST=                            (localhost)
DB_PORT=                            (default is 5432)
SECRET_KEY=                         (any string, but secret)
SOLR_URL=                           (http://127.0.0.1:8983/solr/tester)
SOLR_ADMIN_URL=                     (http://127.0.0.1:8983/solr/admin/cores)
EMAIL_HOST=                         (smtp host, optional)
EMAIL_PORT=                         (smtp port, optional)
EMAIL_HOST_USER=                    (smtp user, optional)
EMAIL_HOST_PASSWORD=                (smtp user password, optional)
```

On a mac, `host.docker.internal` should be used instead of "localhost" or "127.0.0.1".

Set values for the variables and save this as a file, let's name it `env`.

Environment variables are ready, we will also mount some volumes to our Docker container. Get the path to your solr 
directory, from the step where we installed Solr. Also, create a folder for the app to store some utility data 
(portindex, portindex.json etc.). We will mount both these directories as volumes to the docker container, call them `path/to/solr`
and `path/to/data`.

Start the image:

On Linux:
```bash 
docker run -d \
    -v /path/to/solr:/solr \
    -v /path/to/data:/code/app/data \
    --network="host" \
    --name=webapp-container \
    --env-file=env \
    macports-webapp
```

Instead of "macports-webapp" user "arjunsalyan/macports-webapp" as the image name if you pulled the image from
docker registry.

On Mac:
```bash
sudo docker run -d \
    -p 8080:8080 \
    -v /path/to/solr:/solr \
    -v /path/to/data:/code/app/data \ 
    --name=webapp-container \
    --env-file=env \ 
    macports-webapp
```

Open `127.0.0.1:8080` in the browser to test if the app has started, you won't have any ports though.

## Setup without Docker

This is the traditional python-django route that we will follow. Make sure PostgreSQL, SOLR and Memcached(optional) have
been setup as described above. Python3 is recommended.

Start by cloning the repository:
```bash
git clone https://github.com/macports/macports-webapp.git
cd macports-webapp
```

**NOTE**: It is recommended that you clone your fork for development.

Now, create a virtual environment and activate it.

```bash
python3 -m venv env
source env/bin/activate
```

This will create an `env` directory in the root of the project.

Install the requirements for our Django app:

```
pip install -r app/requirements.txt
```

Once all the dependencies are installed we can move to the most important step, that is connecting various services
to the django app. If you followed the setup with Docker, you already know that we do this by using environment variables.
To set the environment variables inside your virtual env, run the following commands:

```bash
export DB_NAME=                            (name of our database, webapp)
export DB_USER=                            (username of the database user)
export DB_PASSWORD=                        (password for your database user)
export DB_HOST=                            (localhost)
export DB_PORT=                            (default is 5432)
export SECRET_KEY=                         (any string, but secret)
export SOLR_URL=                           (http://127.0.0.1:8983/solr/tester)
export SOLR_ADMIN_URL=                     (http://127.0.0.1:8983/solr/admin/cores)
export EMAIL_HOST=                         (smtp host, optional)
export EMAIL_PORT=                         (smtp port, optional)
export EMAIL_HOST_USER=                    (smtp user, optional)
export EMAIL_HOST_PASSWORD=                (smtp user password, optional)
```

**NOTE**: Add the values to the keys as explained and then remove the command. Anything between the `()` is just for your
reference and should not be run with the command. A sample command would look like:

```bash
export DB_NAME=webapp
```

Setting up env variables every time is a tedious task and you might want to reduce the friction by following some really
good guides: https://help.pythonanywhere.com/pages/environment-variables-for-web-apps/

Once the database (and other services) have been connected, run the migrations. Before that let's cd into the main src 
directory for the project, that is `app`.

```bash
cd app
python3 manage.py migrate
python3 manage.py collectstatic
```

You may now run the server, but your app has no data, yet.

```bash
python3 manage.py runserver
```

## Initialising the Webapp

Now that you have the app running (using either of two routes above), it is time to add some data to the app. Some of these
commands take a long time in their first run.

Before proceeding make sure you are in the main django directory, i.e. `app`.

**For docker:**
```bash
docker exec -it webapp-container bash
cd code/app
```
**Without docker:**
```bash
cd app
mkdir data
```

##### Add ports data
```bash
python3 manage.py update-portinfo --type=full
```

**NOTE**: This will take a lot of time, you might want to start another terminal window for rest of the work and keep
this running.
In this command, three tasks take place:
- Fetching `macports-ports` and `macports-contrib` repositories
- Generating the portindex and converting it to `JSON`
- Adding the JSON to PostgreSQL database

##### Create superuser
```bash
python3 manage.py createsuperuser
```
After this enter, username and password according to your choice- remember the credentials.

##### Add a builder
- Login to django admin dashboard using your credentials: `/admin`
- Go to `BUILDHISTORY -> Builder -> Add builder`
- An example of a builder is
    ```bash
    Name of the builder as per buildbot = 10.15_x86_64
    Simplified builder name: 10.XX: = 10.15
    Name of the macOS version, e.g. Catalina: = Catalina
    ```
  
You may add more builders if you wish
  
##### Fetch some build history
```bash
python3 manage.py fetch-build-history &
```

**NOTE**: This command should be sent to background using `&` as the fetching can proceed in the background without any
 issues.
 
##### Run livecheck
```bash
port selfupdate && python3 manage.py run-full-livecheck &
```

**NOTE**: This is the most time consuming command. Livecheck can take 3-4 hours to finish for all ports and hence the command
should always be ran in background.

##### Add a solr schema and generate index
- Generate Solr schema:
    
    **Docker**:
    ```bash
    python3 manage.py build_solr_schema --configure-directory=/solr/server/solr/tester/conf
    ```
    **Without Docker**:
    ```bash
    pyton3 manage.py build_solr_schema --configure-directory=path/to/solr/server/solr/tester/conf
    ```
  
  This is because for Docker, we already the know path to Solr, but without Docker you should add path to Solr as per
  your machine.
  
- Reload Solr core:

    ```bash
    python3 manage.py build_solr_schema -r RELOAD_CORE
    ```
- Build Solr index:

    ```bash
    python3 manage.py rebuild_index --noinput
    ```
  
All needed data has been added.


## Keeping the data up-to-date

To update port information:
```bash 
python3 manage.py update-portinfo
```

To fetch new builds:
```bash
python3 manage.py fetch-build-history
```
**NOTE**: For all added builder, this will fetch all builds that have finished on the buildbot after the most recent 
build in your database.

To run livecheck again:
```bash
python3 manage.py run-full-livecheck
```

To update the Solr index:
```bash
python3 manage.py update_index
```

**IMPORTANT**: Updating the Solr index can be optimised by updating it only for those ports which have changed in past X
hours. For example, if you are trying to update the Solr schema exactly after running `update-portinfo`, then you may
limit the index to be updated for only those ports which have been update in the last hour (because the `update-portinfo`)
command ran just before it. Remember, that the update we are talking about is when the data was added in the database and
not when the port was actually modified on GitHub.

```bash
python3 manage.py update_index --age=1
```


### Setting up Crontabs

Two crontabs can keep the up-to-date in a production environment.


1. Run the following every 10 minutes:
    
    ```bash
    python3 manage.py update-portinfo
    python3 manage.py fetch-build-history
    python3 manage.py update_index --age=5
    ```
    
    The 5-hour window for updating the Solr index is to make sure no builds are missed, as builds might take some time to finish.
    
2. Run the following every two days
    ```bash
    python3 manage.py run-full-livecheck
    python3 manage.py update_index
    ```
