#!/bin/bash

cd /code/app

python3 manage.py makemigrations --noinput

python3 manage.py migrate --noinput

python3 manage.py collectstatic --noinput
