#!/usr/bin/env python

from __future__ import absolute_import

import os
import sys
import argparse
import logging

from novaconsole import openstack
from novaconsole.client import Client
from novaconsole.exc import *


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--url',
                   action='store_true')
    p.add_argument('--escape', '-e',
                   default='~')

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

    p.add_argument('target')

    p.set_defaults(loglevel=logging.WARN)

    return p.parse_args()


def main():
    args = parse_args()

    logging.basicConfig(
        level=args.loglevel)

    if args.url:
        console_url = args.target
    else:
        osclient = openstack.OpenstackClient(args)
        try:
            server = osclient.server(args.target)
        except KeyError:
            logging.error('unable to find server "%s"', args.target)
            sys.exit(1)

        data = server.get_serial_console('serial')
        console_url = data['console']['url']

    try:
        console = Client(console_url, escape=args.escape)

        logging.warn('*** connected (type "%s." to disconnect)',
                     args.escape)
        console.start_loop()
    except ConnectionFailed:
        logging.warn('*** failed to connect to websocket')
    except Disconnected:
        logging.warn('*** remote closed connection')
    except UserExit:
        logging.warn('*** disconnected')

if __name__ == '__main__':
    main()
