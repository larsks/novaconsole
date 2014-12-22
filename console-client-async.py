#!/usr/bin/env python

import os
import sys
import argparse
import websocket
import tty
import termios
import logging
import socket
import trollius as asyncio


class UserExit(Exception):
    '''Raised inside the event loop when someone enters the disconnect
    escape sequence.'''
    pass


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

        self.setup_loop()
        self.connect()

    def setup_loop(self):
        self.loop = asyncio.get_event_loop()

    def connect(self):
        self.ws = websocket.create_connection(
            args.url,
            header={
                'Sec-WebSocket-Protocol: binary',
            })

    def start_loop(self):
        self.exc = None

        self.loop.add_reader(sys.stdin, self.handle_stdin)
        self.loop.add_reader(self.ws, self.handle_websocket)
        self.start_of_line = False
        self.read_escape = False

        try:
            self.setup_tty()
            self.loop.run_forever()
        finally:
            self.restore_tty()
        
        if self.exc:
            raise self.exc

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


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--escape', '-e',
                   default='~')
    p.add_argument('--debug', '-d',
                   action='store_const',
                   const=logging.DEBUG,
                   dest='loglevel')
    p.add_argument('--verbose', '-v',
                   action='store_const',
                   const=logging.INFO,
                   dest='loglevel')
    p.add_argument('url')

    p.set_defaults(loglevel=logging.WARN)

    return p.parse_args()


def main():
    global args
    args = parse_args()

    logging.basicConfig(
        level=args.loglevel)

    client = Client(args.url, escape=args.escape)

    try:
        logging.warn('*** connected (type "%s." to disconnect)',
                     args.escape)
        client.start_loop()
    except socket.error:
        logging.warn('*** failed to connect to websocket')
    except websocket.WebSocketConnectionClosedException:
        logging.warn('*** remote closed connection')
    except UserExit:
        logging.warn('*** disconnected')

if __name__ == '__main__':
    main()


