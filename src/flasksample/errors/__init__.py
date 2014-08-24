from flask import jsonify


class ConfigurationParameterError(Exception):
    def __init__(self, param, msg, *args, **kwargs):
        super(ConfigurationParameterError, self).__init__(*args, **kwargs)
        self.param = param
        self.msg = msg

    def __str__(self):
        return 'configuration parameter \'%s\' is invalid, %s' % (self.param, self.msg)


class InitializationError(Exception):
    pass


# the serializable REST api error and companion flask error code classes
class FlaskErrorCode(object):
    def __init__(self, errorid, desc, http_status):
        self.errorid = http_status
        self.desc = desc
        self.http_status = http_status


class FlaskRESTError(Exception):
    ERROR_MALFORMED_REQUEST = FlaskErrorCode('ERROR_MALFORMED_REQUEST', 'malformed request', 400)
    NOT_FOUND_ERROR = FlaskErrorCode('NOT_FOUND_ERROR', 'object not found', 404)
    UNKNOWN_ERROR = FlaskErrorCode('UNKNOWN_ERROR', 'unknown error occurred', 503)
    ERROR_SUPERVISOR_TRANSPORT = FlaskErrorCode('ERROR_SUPERVISOR_TRANSPORT', 'supervisor transport failed', 503)

    def __init__(self, error_code, msg, http_status=None):
        assert isinstance(error_code, FlaskErrorCode)
        self.error_code = error_code
        self.msg = msg
        self.http_status = http_status if http_status is not None else self.error_code.http_status

    def to_response(self):
        response = jsonify(errorid=self.error_code.errorid, desc=self.error_code.desc, msg=self.msg)
        response.status_code = self.http_status
        return response


# top level exceptions for the service interface
class PersistenceError(Exception):
    pass
