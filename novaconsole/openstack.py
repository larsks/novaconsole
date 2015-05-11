from __future__ import absolute_import

import logging
import os

import keystoneclient.v2_0.client as ksclient
import novaclient.client as nova
import novaclient.exceptions as nexc
import keystoneclient.exceptions as kexc


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


class OpenstackClient(object):
    '''This is a convenience wrapper for using the OpenStack python client
    modules.'''

    def __init__(self, args):
        '''`args` is an `argparse.ArgumentParser` object that has the options
        created by the `add_openstack_args` function, above.'''

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
        self.nova = nova.Client(
            '1.1',
            None,
            None,
            None,
            auth_url=self.keystone.auth_url,
            tenant_id=self.keystone.tenant_id,
            auth_token=self.keystone.auth_token)

    def server(self, name_or_uuid):
        '''Look up a server by name or UUID.'''

        self.log.debug('looking for server: %s', name_or_uuid)
        try:
            return self.nova.servers.get(name_or_uuid)
        except nexc.NotFound:
            for server in self.nova.servers.list(detailed=False):
                if server.name == name_or_uuid:
                    return server

            raise
