FROM ubuntu:18.04

# Install required packages and remove the apt packages cache when done.

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
        git \
        python3 \
        python3-dev \
        python3-setuptools \
        python3-pip \
        nginx \
        cron \
        rsync \
        supervisor && \
    pip3 install -U pip setuptools && \
    rm -rf /var/lib/apt/lists/*

# install uwsgi now because it takes a little while
RUN pip3 install uwsgi

# setup all the configfiles
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY config/nginx.conf /etc/nginx/sites-available/default
COPY config/supervisor.conf /etc/supervisor/conf.d/

# COPY requirements.txt and RUN pip install BEFORE adding the rest of your code, this will cause Docker's caching mechanism
# to prevent re-installing (all your) dependencies when you made a change a line or two in your app.

COPY app/requirements.txt /code/app/
RUN pip3 install -r /code/app/requirements.txt

RUN touch /var/log/buildhistorycron.log
RUN touch /var/log/portinfocron.log

# Setup cron
COPY config/crons /etc/cron.d/crons
RUN chmod 0644 /etc/cron.d/crons

# add (the rest of) our code
COPY . /code/

EXPOSE 80
CMD ["/usr/bin/supervisord", "-n"]
