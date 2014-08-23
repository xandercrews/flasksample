import logging
logger = logging.getLogger(__name__)


from gevent.wsgi import WSGIHandler, WSGIServer


class LoggingWSGIHandler(WSGIHandler):
    '''
    fix up the wsgi handler so it uses python standard logging instead of writing to file handle
    '''
    def log_request(self):
        logargs = {
            'client': (self.client_address[0] if isinstance(self.client_address, tuple) else self.client_address) or '-',
            'requestline': getattr(self, 'requestline', ''), 'statuscode': getattr(self, 'status', '000'),
            'len': self.response_length or '-',
            'responsetime': '%.6fs' % (self.time_finish - self.time_start) if self.time_finish else '-',
        }

        logmsg = 'client: %(client)s request: %(requestline)s statuscode: %(statuscode)s len: %(len)d responsetime: %(responsetime)s' % logargs
        logger.info(logmsg)

    def log_error(self, msg, *args):
        logger.error(msg)


class LoggingWSGIServer(WSGIServer):
    handler_class = LoggingWSGIHandler

    def __init__(self, listener, application=None, backlog=None, spawn='default', environ=None, **ssl_args):
        super(LoggingWSGIServer, self).__init__(listener, application, backlog, spawn, None, None, environ, **ssl_args)