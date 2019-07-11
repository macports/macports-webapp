#!/bin/bash

cd /code/app

python3 manage.py makemigrations

python3 manage.py migrate

python3 manage.py collectstatic
