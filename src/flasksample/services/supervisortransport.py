import xmlrpclib

from . import SupervisorTransportService, SupervisorPersistenceServiceInterface


class SupervisorCtl(object):
    def __init__(self, url):
        self.server = xmlrpclib.ServerProxy(url)


class SupervisorXMLRPCTransport(SupervisorTransportService):
    def __init__(self, supervisorpersistence):
        assert isinstance(supervisorpersistence, SupervisorPersistenceServiceInterface)
        self.supervisorpersistence =  supervisorpersistence

    def get_status(self, supervisorid):
        url = self.supervisorpersistence.get_supervisor()
        s = SupervisorCtl(url)

    def get_processes(self, supervisorid):
        pass

    def start_process(self, supervisorid, name):
        pass

    def stop_process(self, supervisorid, name):
        pass

    def start_all_processes(self, supervisorid):
        pass

    def stop_all_processes(self, supervisorid):
        pass

    def get_process_stdout(self, supervisorid, name):
        pass

    def get_process_stderr(self, supervisorid, name):
        pass
