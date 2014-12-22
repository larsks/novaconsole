class NovaConsoleException(Exception):
    'base for all novaconsole generated exceptions'
    def __str__(self):
        return self.__doc__


class UserExit(NovaConsoleException):
    'user requested disconnect'


class Disconnected(NovaConsoleException):
    'remote host closed connection'


class ConnectionFailed(NovaConsoleException):
    'failed to connect to remote host'
