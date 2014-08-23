import datetime
import logging


class UTC(datetime.tzinfo):
    def utcoffset(self, date_time):
        return None

    def tzname(self, date_time):
        return "UTC"

    def fromutc(self, date_time):
        return date_time

    def dst(self, date_time):
        return 0


class ISO8601Formatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self.created_timezone = kwargs.pop('created_timezone', UTC())
        # TODO created time converter like formatTime has
        super(ISO8601Formatter, self).__init__(*args, **kwargs)

    def format(self, record):
        if hasattr(record, 'created'):
            record.isocreated = datetime.datetime.fromtimestamp(record.created, self.created_timezone).isoformat()
            if len(record.isocreated) < 28:
                record.isocreated += 'Z'

        return super(ISO8601Formatter, self).format(record)

    @classmethod
    def factory(cls, *args, **kwargs):
        return ISO8601Formatter(*args, **kwargs)
