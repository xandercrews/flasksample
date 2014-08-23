class ObjectNotFound(Exception):
    def __init__(self, name, msg, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.name = name
        self.msg = msg

    def __str__(self):
        return 'object \'%s\' not found, %s' % (self.name, self.msg)
