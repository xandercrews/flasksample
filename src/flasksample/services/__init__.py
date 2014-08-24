import abc


class ServiceInterface(object):
    def __init__(self, persistenceservice, supervisorservice):
        assert isinstance(persistenceservice, SupervisorPersistenceServiceInterface)
        self.persistenceservice = persistenceservice

        assert isinstance(supervisorservice, SupervisorTransportService)
        self.supervisorservice = supervisorservice


class SupervisorPersistenceServiceInterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def register_supervisor(self, url):
        pass

    @abc.abstractmethod
    def unregister_supervisor(self, supervisorid):
        pass

    @abc.abstractmethod
    def list_supervisors(self):
        pass

    @abc.abstractmethod
    def get_supervisor(self, supervisorid):
        pass


class SupervisorTransportService(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_all_process_info(self, supervisorid):
        pass

    @abc.abstractmethod
    def start_all_processes(self, supervisorid):
        pass

    @abc.abstractmethod
    def stop_all_processes(self, supervisorid):
        pass

    @abc.abstractmethod
    def start_process(self, supervisorid, name):
        pass

    @abc.abstractmethod
    def stop_process(self, supervisorid, name):
        pass

    @abc.abstractmethod
    def get_process_stdout(self, supervisorid, name):
        pass

    @abc.abstractmethod
    def get_process_stderr(self, supervisorid, name):
        pass
