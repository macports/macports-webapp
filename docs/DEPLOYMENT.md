## Setting up the ports webapp

For testing and development purposes, the ports webapp should be deployed locally. The main Django app is contained
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
setting up a local environment can be avoided working with Docker. However, we will also walk through the standard process.

## Getting the dependencies ready

The the external dependencies of the app are: PostgreSQL, Solr and Memcached. The search page(/search/) is completely derived from
Solr. Memcached is optional, and can be avoided if you don't want to cache the results of stats and trac tickets.

If you are new to these technologies, you may use the instructions provided below, otherwise you are free to install and setup these
dependencies by your preferred mechanism.

### PostgreSQL

Download and install `Postgres.app` from [here](https://postgresapp.com/downloads.html).

After this, connect as root:
```bash
su - postgres
```

Create your user(replace username and password with your preferred credentials):
```bash
CREATE USER username PASSWORD 'passowrd';
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

### 3. Setting up initial data

- Migrations are automatically applied to the database by the docker image.
- To populate the database with ports, run:
    ```bash
    docker exec webapp-container python3 /code/app/manage.py update-portinfo --type=full
    ```
  This will take quite a while, as first we build a `Portindex` and then push the data to database.
  You may run the command in background by adding `&` at the end of the command.
- Create a superuser
    ```bash
    docker exec webapp-container python3 /code/app/manage.py createsuperuser
    ```
  and then enter username and password.
- Login to the app, (127.0.0.1:8080/admin) using the credentials of the superuser. Once in the admin dashboard, add one or
   more builders. You may see available builders from [ports.macports.org/all_builds](https://ports.macports.org/all_builds/)
- Fetch some history
    ```bash 
     docker exec webapp-container python3 /code/app/manage.py fetch-build-history &
    ```
  Notice the `&` used to push the command to background.
  
That's it.