from flask import Flask, Response

app = Flask('flaskboilerplate')

@app.route('/')
def index():
    app.logger.debug('in index')
    return Response('')

@app.route('/noop')
def noop():
    return Response('')
