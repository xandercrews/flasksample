#!/usr/bin/env python2

from flask import Flask, Response

app = Flask('httpapp')

@app.route('/loadavg')
def loadavg():
    r = open('/proc/loadavg').read().strip()
    return Response(r)

@app.route('/uptime')
def uptime():
    r = open('/proc/uptime').read().strip()
    return Response(r)

@app.route('/stat')
def uptime():
    r = open('/proc/stat').read().strip()
    return Response(r)

@app.route('/meminfo')
def uptime():
    r = open('/proc/meminfo').read().strip()
    return Response(r)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10001)
