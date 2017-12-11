#!/bin/bash

# This starts a screen session with tabs for the local server, celery server.

screen -dmS "server" -t "server"
screen -r "server" -X screen -t "celery"
screen -r "server" -X screen -t "redis"

screen -r "server" -p server -X stuff $'source ./bin/start-webapp.sh'
screen -r "server" -p celery -X stuff $'source ./bin/start-celery.sh'
screen -r "server" -p redis -X stuff $'redis-server'
