# Sl_Gestion_Stock

an updated version of the original gestion stock app

# Docker commands

## Build

`docker build -t gestion:alpha .`

## running container

docker run -p 8000:80 --name gestionApp -d gestion:alpha

## attaching shell

docker container exec -it gestionApp bash
