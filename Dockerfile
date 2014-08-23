FROM debian:wheezy
MAINTAINER nobody

ADD src /src
ADD docker /docker

RUN apt-get update &&\
    apt-get install -y python python-dev python-setuptools build-essential
    
RUN cd /src && python setup.py develop

CMD [ "/usr/local/bin/flaskboilerplate", "-c", "/docker/flaskboilerplate.conf" ]

EXPOSE 8000
