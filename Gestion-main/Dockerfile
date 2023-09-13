# pull the official base image
FROM ubuntu:20.04

RUN DEBIAN_FRONTEND=noninteractive  apt-get update
RUN DEBIAN_FRONTEND=noninteractive  apt-get -y dist-upgrade
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata.
RUN DEBIAN_FRONTEND=noninteractive  apt-get -yq install postgresql net-tools nginx python3-pip libpq-dev

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip 
COPY ./requirements.txt /usr/src/app
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app

COPY ./configs/gestion /etc/nginx/sites-available
RUN ln -s /etc/nginx/sites-available/gestion /etc/nginx/sites-enabled
RUN service nginx restart

EXPOSE 80

CMD ["gunicorn" ,"--bind","0.0.0.0:8000","gestionStock.wsgi"]