

class ParameterError(Exception):

    def __init__(self, msg):
        super(ParameterError, self).__init__(msg)
        self.msg = msg
