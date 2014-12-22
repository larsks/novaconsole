import argparse
import logging
import os

import keystoneclient.v2_0.client as ksclient
import novaclient.v1_1.client as novaclient
from novaclient.exceptions import *


def add_openstack_args(p):
    '''Add options for OpenStack authentication to
    an ArgumentParser.'''

    g = p.add_argument_group('Openstack authentication options')
    g.add_argument('--os-username',
                   default=os.environ.get('OS_USERNAME'))
    g.add_argument('--os-password',
                   default=os.environ.get('OS_PASSWORD'))
    g.add_argument('--os-tenant-name',
                   default=os.environ.get('OS_TENANT_NAME'))
    g.add_argument('--os-tenant-id',
                   default=os.environ.get('OS_TENANT_ID'))
    g.add_argument('--os-region-name',
                   default=os.environ.get('OS_REGION_NAME'))
    g.add_argument('--os-auth-url',
                   default=os.environ.get('OS_AUTH_URL'))

    return p


class OpenstackClient(object):
    def __init__(self, args):
        self.log = logging.getLogger('openstack-client')

        self.log.debug('authenticating to keystone @ %s',
                       args.os_auth_url)
        self.keystone = ksclient.Client(
            username=args.os_username,
            password=args.os_password,
            tenant_name=args.os_tenant_name,
            tenant_id=args.os_tenant_id,
            auth_url=args.os_auth_url)

        self.log.debug('getting nova client')
        self.nova = novaclient.Client(
            None,
            None,
            None,
            auth_url=self.keystone.auth_url,
            tenant_id=self.keystone.tenant_id,
            auth_token=self.keystone.auth_token)

    def server(self, name_or_uuid):
        self.log.debug('looking for server: %s', name_or_uuid)
        try:
            return self.nova.servers.get(name_or_uuid)
        except NotFound:
            for server in self.nova.servers.list(detailed=False):
                if server.name == name_or_uuid:
                    return server

        raise KeyError(name_or_uuid)


