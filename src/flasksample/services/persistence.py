from . import SupervisorPersistenceServiceInterface

from .errors import ObjectNotFound


import logging
logger = logging.getLogger(__name__)


class InMemorySupervisorPersistence(SupervisorPersistenceServiceInterface):
    def __init__(self):
        self.nextsupervisor = 0
        self.supervisormap = {}

    def unregister_supervisor(self, supervisorid):
        assert isinstance(supervisorid, int)
        logger.info('unregistering supervisor instance \'%d\'' % supervisorid)
        if supervisorid not in self.supervisormap:
            raise ObjectNotFound(supervisorid, 'no supervisor with this id')
        else:
            del self.supervisormap[supervisorid]

    def get_supervisor(self, supervisorid):
        logger.debug('getting supervisor instance \'%d\'' % supervisorid)
        if supervisorid not in self.supervisormap:
            ObjectNotFound(supervisorid, 'no supervisor with this id')
        else:
            return {
                'id': supervisorid,
                'url': self.supervisormap[supervisorid],
            }

    def register_supervisor(self, url):
        currentid = self.nextsupervisor

        logger.info('registering supervisor instance with id \'%d\'' % currentid)
        self.supervisormap[currentid] = url

        self.nextsupervisor += 1

        return currentid

    def list_supervisors(self):
        logger.debug('listing supervisors')
        return {str(k):v for k,v in self.supervisormap.items()}


