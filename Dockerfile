FROM debian:wheezy
MAINTAINER nobody

ADD src /src
ADD docker /docker

RUN apt-get update &&\
    apt-get install -y python python-dev python-setuptools build-essential vim
    
RUN cd /src && python setup.py develop

CMD [ "/usr/local/bin/flasksample", "-c", "/docker/flasksample.conf" ]

EXPOSE 8000
