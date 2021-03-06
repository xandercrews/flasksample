import functools


from flask import Flask, Request, Response, jsonify, request


from .conf import EnhancedConfig
from .errors import ConfigurationParameterError, InitializationError, FlaskRESTError

from .services.errors import ObjectNotFound, SupervisorTransportError, SupervisorNotFound, SupervisorProcessNotFound

from .services.persistence import InMemorySupervisorPersistence
from .services.supervisortransport import SupervisorXMLRPCTransport


app = Flask('flasksample')


def initialize_config(cfg):
    assert isinstance(cfg, EnhancedConfig)

    persistencetype = cfg.getByPath('persistence.type', None)

    if persistencetype is None:
        raise ConfigurationParameterError('persistence.type', msg='missing persistence type')
    elif persistencetype not in ('memory',):
        raise ConfigurationParameterError('persistence.type', msg='invalid persistence type- must be \'memory\'')

    supervisortransport = cfg.getByPath('supervisortransport.type', None)

    if supervisortransport is None:
        raise ConfigurationParameterError('supervisortransport.type', msg='missing supervisor transport type')
    elif supervisortransport not in ('xmlrpc',):
        raise ConfigurationParameterError('supervisortransport.type', msg='invalid supervisor transport type- must be \'xmlrpc\'')

    with app.app_context():
        app.config.update(cfg)


def initialize_services():
    with app.app_context():
        persistencetype = app.config['persistence']['type']
        if persistencetype == 'memory':
            persistence = InMemorySupervisorPersistence()
        else:
            raise InitializationError('no persistence service initialized')

        supervisortransporttype = app.config['supervisortransport']['type']
        if supervisortransporttype == 'xmlrpc':
            supervisortransport = SupervisorXMLRPCTransport(persistence)
        else:
            raise InitializationError('no supervisor transport service initialized')

        app.services = {
            'persistence':  persistence,
            'supervisortransport':supervisortransport
        }


@functools.wraps(Request.on_json_loading_failed)
def handle_json_load_failed(e):
    raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'could not load request json- %s' % str(e))


# error handlers
@app.errorhandler(SupervisorNotFound)
def handle_supervisornotfound(e):
    return FlaskRESTError(FlaskRESTError.NOT_FOUND_ERROR, 'supervisor not found').to_response()


@app.errorhandler(SupervisorProcessNotFound)
def handle_supervisorprocessnotfound(e):
    return FlaskRESTError(FlaskRESTError.NOT_FOUND_ERROR, 'process not found').to_response()


@app.errorhandler(SupervisorTransportError)
def handle_supervisortransporterror(e):
    return FlaskRESTError(FlaskRESTError.ERROR_SUPERVISOR_TRANSPORT, str(e)).to_response()


@app.errorhandler(FlaskRESTError)
def handle_flaskerror(e):
    return e.to_response()


@app.errorhandler(Exception)
def handle_unknown_error(e):
    app.logger.exception('uncaught exception in request handler- %s' % str(e))
    flaskerror = FlaskRESTError(FlaskRESTError.UNKNOWN_ERROR, 'unhandled exception, see log for details')
    return flaskerror.to_response()


# application routes
@app.route('/supervisor/', methods=['GET', ])
def list_supervisors():
    '''
    :return: a map of supervisor instances and their IDs
    '''
    persistence = app.services['persistence']
    superlist = persistence.list_supervisors()
    return jsonify(**superlist)


@app.route('/supervisor/', methods=['POST', ])
def add_supervisor():
    '''
    add a new supervisor instance

    :return: the id of the new supervisor instance
    '''
    persistence = app.services['persistence']

    supervisor_json = request.get_json()

    if supervisor_json is None and request.headers.get('content-type') != 'application/json':
        raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'bad content type')

    if supervisor_json is None:
        raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'empty request')


    if 'url' not in supervisor_json:
        raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'url missing in supervisor add request')

    for k in supervisor_json.keys():
        if k != 'url':
            raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'unexpected key in supervisor add request')

    if not isinstance(supervisor_json['url'], basestring):
        raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'supervisor url is in unexpected format')

    newid = persistence.register_supervisor(supervisor_json['url'])

    id_response = {
        'id': newid,
    }

    return jsonify(**id_response)


@app.route('/supervisor/<supervisorid>/', methods=['GET', ])
def get_supervisor(supervisorid):
    '''
    gets a single supervisor record

    :param supervisorid: the id of the supervisor process, as returned by the listings above
    :return: the supervisor
    '''

    try:
        supervisorid = int(supervisorid)
    except ValueError:
        raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'supervisor id invalid- integer expected')

    persistence = app.services['persistence']

    try:
        s = persistence.get_supervisor(supervisorid)
    except ObjectNotFound:
        raise FlaskRESTError(FlaskRESTError.NOT_FOUND_ERROR, 'supervisor id not found')

    return jsonify(**s)


@app.route('/supervisor/<supervisorid>/', methods=['DELETE', ])
def delete_supervisor(supervisorid):
    '''
    deletes a supervisor record by id

    :param supervisorid: the id of the supervisor process, as returned by the listings above
    :return: None
    '''
    try:
        supervisorid = int(supervisorid)
    except ValueError:
        raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'supervisor id invalid- integer expected')

    persistence = app.services['persistence']

    try:
        persistence.unregister_supervisor(supervisorid)
    except ObjectNotFound:
        raise FlaskRESTError(FlaskRESTError.NOT_FOUND_ERROR, 'supervisor id not found')

    return Response(status=200)


@app.route('/supervisor/<supervisorid>/status', methods=['GET',])
def supervisor_status(supervisorid):
    '''
    returns the result of the supervisor 'status' call insta

    :param supervisorid: the id of the supervisor process, as returned by the listings above
    :return: a json document about the status of processes
    '''
    try:
        supervisorid = int(supervisorid)
    except ValueError:
        raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'supervisor id invalid- integer expected')

    supervisortransport = app.services['supervisortransport']

    status = supervisortransport.get_all_process_info(supervisorid)
    return jsonify(**status)


@app.route('/supervisor/<supervisorid>/startall', methods=['POST',])
def supervisor_startall(supervisorid):
    '''
    start all processes by supervisor

    :param supervisorid: the id of the supervisor process, as returned by the listings above
    :return: empty response
    '''
    try:
        supervisorid = int(supervisorid)
    except ValueError:
        raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'supervisor id invalid- integer expected')

    supervisortransport = app.services['supervisortransport']
    supervisortransport.start_all_processes(supervisorid)
    return Response(status=200)


@app.route('/supervisor/<supervisorid>/stopall', methods=['POST',])
def supervisor_stopall(supervisorid):
    '''
    stop all processes by supervisor

    :param supervisorid: the id of the supervisor process, as returned by the listings above
    :return: empty response
    '''
    try:
        supervisorid = int(supervisorid)
    except ValueError:
        raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'supervisor id invalid- integer expected')

    supervisortransport = app.services['supervisortransport']
    supervisortransport.stop_all_processes(supervisorid)
    return Response(status=200)


@app.route('/supervisor/<supervisorid>/<processname>/start', methods=['POST',])
def supervisor_start_process(supervisorid, processname):
    '''
    start a process by supervisor id and process name

    :param supervisorid: the id of the supervisor process, as returned by the listings above
    :param processname: the process name as obtained by the status command
    :return: empty response
    '''
    try:
        supervisorid = int(supervisorid)
    except ValueError:
        raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'supervisor id invalid- integer expected')

    supervisortransport = app.services['supervisortransport']
    supervisortransport.start_process(supervisorid, processname)
    return Response(status=200)


@app.route('/supervisor/<supervisorid>/<processname>/stop', methods=['POST',])
def supervisor_stop_process(supervisorid, processname):
    '''
    stop a process by supervisor id and process name

    :param supervisorid: the id of the supervisor process, as returned by the listings above
    :param processname: the process name as obtained by the status command
    :return: empty response
    '''
    try:
        supervisorid = int(supervisorid)
    except ValueError:
        raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'supervisor id invalid- integer expected')

    supervisortransport = app.services['supervisortransport']
    supervisortransport.stop_process(supervisorid, processname)
    return Response(status=200)


@app.route('/supervisor/<supervisorid>/<processname>/stdout', methods=['GET',])
def supervisor_process_stdout(supervisorid, processname):
    '''
    get the stdout of a process

    :param supervisorid: the id of the supervisor process, as returned by the listings above
    :param processname: the process name as obtained by the status command
    :return:
    '''
    try:
        supervisorid = int(supervisorid)
    except ValueError:
        raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'supervisor id invalid- integer expected')

    supervisortransport = app.services['supervisortransport']

    response = { 'stdout': supervisortransport.get_process_stdout(supervisorid, processname) }

    return jsonify(**response)


@app.route('/supervisor/<supervisorid>/<processname>/stderr', methods=['GET',])
def supervisor_process_stderr(supervisorid, processname):
    '''
    get the stderr output of a process

    :param supervisorid: the id of the supervisor process, as returned by the listings above
    :param processname: the process name as obtained by the status command
    :return:
    '''
    try:
        supervisorid = int(supervisorid)
    except ValueError:
        raise FlaskRESTError(FlaskRESTError.ERROR_MALFORMED_REQUEST, 'supervisor id invalid- integer expected')

    supervisortransport = app.services['supervisortransport']

    response = { 'stderr': supervisortransport.get_process_stderr(supervisorid, processname) }

    return jsonify(**response)

@app.route('/noop')
def noop():
    return Response('')