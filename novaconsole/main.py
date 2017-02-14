#!/usr/bin/env python

from __future__ import absolute_import

import os
import sys
import argparse
import logging

from novaconsole import openstack
from novaconsole.client import Client
from novaconsole.exc import *

LOG = logging.getLogger('novaconsole')

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--url',
                   action='store_true',
                   help='Target specifies a websocket url '
                   'rather than nova server name.  Using this '
                   'option does not require authentication.')
    p.add_argument('--escape', '-e',
                   default='~',
                   help='Character used to start escape sequences when '
                   'connected. Defaults to "~".')
    p.add_argument('--close-wait', '-w',
                   default=0.5,
                   type=float,
                   help='How long to wait for remote output when reading '
                   'from a pipe.')
    p.add_argument('--no-subprotocols', '-N', action='store_true',
                   help='Disable explicit subprotocol request.')

    g = p.add_argument_group('Logging options')
    g.add_argument('--debug', '-d',
                   action='store_const',
                   const=logging.DEBUG,
                   dest='loglevel')
    g.add_argument('--verbose', '-v',
                   action='store_const',
                   const=logging.INFO,
                   dest='loglevel')

    openstack.add_openstack_args(p)

    p.add_argument('target',
                   help='A server name, uuid, or (with --url) '
                   'a websocket url')

    p.set_defaults(loglevel=logging.WARN)

    return p.parse_args()


def main():
    args = parse_args()

    logging.basicConfig(
        level=args.loglevel)

    if args.url or args.target.startswith('ws://'):
        console_url = args.target
    else:
        try:
            osclient = openstack.OpenstackClient(args)
            server = osclient.server(args.target)
            data = server.get_serial_console('serial')
        except openstack.kexc.ClientException as exc:
            LOG.error('failed to authenticate to keystone: %s', exc)
            sys.exit(1)
        except openstack.nexc.ClientException as exc:
            LOG.error('failed to connect to serial console: %s', exc)
            sys.exit(1)

        console_url = data['console']['url']

    try:
        subprotocols = [] if args.no_subprotocols else None
        console = Client(console_url,
                         escape=args.escape,
                         subprotocols=subprotocols,
                         close_wait=args.close_wait)

        console.start_loop()
    except NovaConsoleException as e:
        LOG.error(e)

if __name__ == '__main__':
    main()
