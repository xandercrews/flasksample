FROM debian:wheezy
MAINTAINER nobody

RUN apt-get update &&\
    apt-get install -y python python-pip vim supervisor

RUN pip install flask

ADD dieafter10.py /docker/
ADD httpapp.py /docker/
ADD supervisor.conf /docker/

RUN chmod ugo+rx /docker/*.py

CMD [ "/usr/bin/supervisord", "-c", "/docker/supervisor.conf" ]

EXPOSE 10000 10001
