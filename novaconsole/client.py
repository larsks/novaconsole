import sys
import termios
import tty
import logging
import socket

from novaconsole.exc import *

try:
    import trollius as asyncio
except ImportError:
    logging.fatal('This package requires "trollius", the asyncio port '
                  'for Python 2.x.')
    logging.fatal('See https://pypi.python.org/pypi/trollius for '
                  'additional information.')
    sys.exit()

try:
    import websocket
except ImportError:
    logging.fatal('This package requires the "websocket" module.')
    logging.fatal('See http://pypi.python.org/pypi/websocket-client for '
                  'more information.')
    sys.exit()

def graceful_exit(f):
    def _(self, *args, **kwargs):
        try:
            f(self, *args, **kwargs)
        except Exception as exc:
            self.exc = exc
            self.loop.stop()

    return _


class Client (object):
    def __init__(self, url, escape='~'):
        self.url = url
        self.escape = escape

        self.setup_logging()
        self.setup_loop()
        self.connect()

    def setup_logging(self):
        self.log = logging.getLogger('console-client')

    def setup_loop(self):
        self.loop = asyncio.get_event_loop()

    def connect(self):
        self.log.info('connecting to url: %s', self.url)
        try:
            self.ws = websocket.create_connection(
                self.url,
                header={
                    'Sec-WebSocket-Protocol: binary',
                })
        except socket.error as e:
            raise ConnectionFailed(e)

    def start_loop(self):
        self.exc = None

        self.loop.add_reader(sys.stdin, self.handle_stdin)
        self.loop.add_reader(self.ws, self.handle_websocket)
        self.start_of_line = False
        self.read_escape = False

        try:
            self.setup_tty()
            self.loop.run_forever()

            if self.exc:
                raise self.exc
        except socket.error as e:
            raise ConnectionFailed(e)
        except websocket.WebSocketConnectionClosedException as e:
            raise Disconnected(e)
        except TypeError:
            pass
        except:
            raise
        finally:
            self.restore_tty()
        

    def setup_tty(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin)

    def restore_tty(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN,
                          self.old_settings)

    @graceful_exit
    def handle_stdin(self):
        data = sys.stdin.read(1)

        if self.start_of_line and data == self.escape:
            self.read_escape = True
            return

        if self.read_escape and data == '.':
            raise UserExit()
        elif self.read_escape:
            self.read_escape = False
            self.ws.send(self.escape)

        self.ws.send(data)

        if data == '\r':
            self.start_of_line = True
        else:
            self.start_of_line = False

    @graceful_exit
    def handle_websocket(self):
        data = self.ws.recv()
        sys.stdout.write(data)
        sys.stdout.flush()



