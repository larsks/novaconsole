class UserExit(Exception):
    '''Raised inside the event loop when someone enters the disconnect
    escape sequence.'''
    pass

class Disconnected(Exception):
    pass

class ConnectionFailed(Exception):
    pass
