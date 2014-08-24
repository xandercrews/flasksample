# (work in progress)

# A sample Flask REST project

## Project Overview

Let's consider a contrived task that we want to accomplish with a rest service:  we have many hosts on the network
running services under the process management system supervisord (http://supervisord.org/).  Supervisor provides an XML
RPC interface for managing a single supervisor instance, but we would like a single API that we can use to inspect and
control any of our processes managed by with supervisord.  So we'll expose its functions through a REST-like web API
build with python-Flask.

# TODO

 * mocking supervisor rpc interface, test coverage
