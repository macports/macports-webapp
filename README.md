# Introduction

### Goal

This is a web application that:
 1. Displays general information about all the ports.
 2. Fetches and displays build history of the ports.
 3. Collects and displays installation statistics (system configurations and installed ports) from users who opt-in by
    installing the port `mpstats`.
 4. Allows following ports and receiving notifications when a port gets updated.
    
It aims at being an all-one-place for users to find relevant ports and for maintainers to monitor their ports and
understand their user base. The app is running in production at [ports.macports.org](https://ports.macports.org).
 
More info at [docs/INFORMATION.md](docs/INTRODUCTION.md)

### Architecture

The web application is based on:
 - [Django Framework](https://www.djangoproject.com)
 - [PostgreSQL Database](https://www.postgresql.org)
 - [Solr](https://lucene.apache.org/solr/)
 - [Memcached](http://memcached.org)
 
The project has been packaged using:
 - [Docker](https://www.docker.com)
 - [NGINX](https://www.nginx.com)
 - [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/)
 - [Supervisor](http://supervisord.org)

___

### More information
 - [API](/docs/API_v1/ENDPOINTS.md)
 - [Collection of data](/docs/SOURCES.md)
 - [Deploying the app](/docs/DEPLOYMENT.md)