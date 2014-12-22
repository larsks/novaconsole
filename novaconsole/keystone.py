import keystoneclient.v2_0.client as ksclient

def get_keystone_client(os_username=None,
                        os_password=None,
                        os_tenant_name=None,
                        os_tenant_id=None,
                        os_auth_url=None
                        ):

    return ksclient.Client(username=os_username, 
                           password=os_password,
                           tenant_name=os_tenant_name,
                           tenant_id=os_tenant_id,
                           auth_url=os_auth_url)
     


