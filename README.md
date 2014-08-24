# (work in progress)

# A sample Flask REST project

## Project Overview

Let's consider a contrived task that we want to accomplish with a rest service:  we have many hosts on the network
running services under the process management system supervisord (http://supervisord.org/).  Supervisor provides an XML
RPC interface for managing a single supervisor instance, but we would like a single API that we can use to inspect and
control any of our processes managed by with supervisord.  So we'll expose its functions through a REST-like web API
build with python-Flask.

## Instructions

To build docker images for the app and supervisor test nodes:

```bash
git clone <this repo> flasksample
cd flasksample
docker build -t flasksample .
cd docker/supervisornode
docker build -t supervisornode . 
```

To run the docker instances:

```bash
for i in $(seq 1 <num instances>); do
    docker run -d supervisornode
done
docker run --rm -t -i flasksample
```

To test the api (from the docker host):

```bash
API_ADDRESS=$(docker ps | awk '/flasksample/ { print $1 }' | xargs docker inspect | grep IPAddress | awk -F ':' '{print $2}'  | sed 's|[" ,]||g')
SUPERVISOR_ADDRESSES=$(docker ps | awk '/supervisornode/ { print $1 }' | xargs docker inspect | grep IPAddress | awk -F ':' '{print $2}'  | sed 's|[" ,]||g')
for s in $SUPERVISOR_ADDRESSES; do 
    curl -XPOST -H 'Content-Type: application/json' -d "{\"url\": \"http://$s:10000\"}" http://$API_ADDRESS:8000/supervisor/; echo
done;
curl -XGET http://$API_ADDRESS:8000/supervisor/0/status; echo
```

# TODO

 * mocking supervisor rpc interface, test coverage
