#!/bin/sh

python manage.py migrate
gunicorn -c ./deployment/gunicorn_conf.py smorgasbord.wsgi:application