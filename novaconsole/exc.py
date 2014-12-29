class NovaConsoleException(Exception):
    'base for all novaconsole generated exceptions'
    def __init__(self, wrapped=None):
        self.wrapped = wrapped

    def __str__(self):
        return '%s: %s' % (
            self.__doc__,
            self.wrapped if str(self.wrapped) else 'an unknown error occurred')

class UserExit(NovaConsoleException):
    'user requested disconnect'


class Disconnected(NovaConsoleException):
    'remote host closed connection'


class ConnectionFailed(NovaConsoleException):
    'failed to connect to remote host'
