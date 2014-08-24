import xmlrpclib
import supervisor.xmlrpc

from . import SupervisorTransportService, SupervisorPersistenceServiceInterface
from .errors import SupervisorNotFound, SupervisorTransportError, SupervisorProcessNotFound


import logging
logger = logging.getLogger(__name__)


def trap_xmlrpc_fault(f):
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except xmlrpclib.Fault, e:
            if e.faultCode ==  supervisor.xmlrpc.Faults.BAD_NAME:
                raise SupervisorProcessNotFound('process not found')
            else:
                raise SupervisorTransportError('%s: %s' % (e.faultCode, e.faultString,))
    return wrapped


class SupervisorXMLRPCTransport(SupervisorTransportService):
    def __init__(self, supervisorpersistence):
        assert isinstance(supervisorpersistence, SupervisorPersistenceServiceInterface)
        self.supervisorpersistence =  supervisorpersistence

    def _get_supervisor_url(self, supervisorid):
        supervisorinfo = self.supervisorpersistence.get_supervisor(supervisorid)
        if supervisorinfo is None:
            raise SupervisorNotFound('supervisor id not found')
        if 'url' not in supervisorinfo:
            raise SupervisorNotFound('url missing')
        url = supervisorinfo['url']
        return xmlrpclib.ServerProxy(url)

    @trap_xmlrpc_fault
    def get_all_process_info(self, supervisorid):
        s = self._get_supervisor_url(supervisorid)
        procinfo = s.supervisor.getAllProcessInfo()

        try:
            return {v['name']: v for v in procinfo}
        except Exception, e:
            logger.exception('failed to format supervisor processes- %s' % str(e))
            raise SupervisorTransportError('error formatting process status')

    @trap_xmlrpc_fault
    def start_process(self, supervisorid, name):
        s = self._get_supervisor_url(supervisorid)
        return s.supervisor.startProcess(name)

    @trap_xmlrpc_fault
    def stop_process(self, supervisorid, name):
        s = self._get_supervisor_url(supervisorid)
        return s.supervisor.stopProcess(name)

    @trap_xmlrpc_fault
    def start_all_processes(self, supervisorid):
        s = self._get_supervisor_url(supervisorid)
        return s.supervisor.startAllProcesses()

    @trap_xmlrpc_fault
    def stop_all_processes(self, supervisorid):
        s = self._get_supervisor_url(supervisorid)
        return s.supervisor.stopAllProcesses()

    @trap_xmlrpc_fault
    def get_process_stdout(self, supervisorid, name):
        s = self._get_supervisor_url(supervisorid)
        return s.supervisor.readProcessStdoutLog(name, 0, 1024*1024)

    @trap_xmlrpc_fault
    def get_process_stderr(self, supervisorid, name):
        s = self._get_supervisor_url(supervisorid)
        return s.supervisor.readProcessStderrLog(name, 0, 1024*1024)
