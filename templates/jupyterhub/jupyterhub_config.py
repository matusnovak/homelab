from jupyterhub.auth import Authenticator, LocalAuthenticator
from ldapauthenticator import LDAPAuthenticator
import os


class LocalLDAPCreateUsers(LocalAuthenticator, LDAPAuthenticator):
    """Create local user accounts based on LDAP authentication"""
    pass


# Grant admin users permission to access single-user servers.
#
#  Users should be properly informed if this is enabled.
c.JupyterHub.admin_access = False

# Allow named single-user servers per user
c.JupyterHub.allow_named_servers = False

# Class for authenticating users.
c.JupyterHub.authenticator_class = LocalLDAPCreateUsers

# The base URL of the entire application
#c.JupyterHub.base_url = '/'

# Whether to shutdown the proxy when the Hub shuts down.
c.JupyterHub.cleanup_proxy = True

# Whether to shutdown single-user servers when the Hub shuts down.
c.JupyterHub.cleanup_servers = True

# The public facing ip of the whole application (the proxy)
c.JupyterHub.ip = '0.0.0.0'

# The public facing port of the proxy
c.JupyterHub.port = 8000

# Purge and reset the database.
#c.JupyterHub.reset_db = False
c.JupyterHub.reset_db = True

# The URL the single-user server should start in.
c.Spawner.default_url = '/lab'

# Whitelist of environment variables for the single-user server to inherit from
#  the JupyterHub process.
c.Spawner.env_keep = [
    'PATH',
    'PYTHONPATH',
    'CONDA_ROOT',
    'CONDA_DEFAULT_ENV',
    'VIRTUAL_ENV',
    'LANG',
    'LC_ALL',
    'JAVA_HOME',
    'M2_HOME',
]

# Path to the notebook directory for the single-user server.
c.Spawner.notebook_dir = '~'

LocalLDAPCreateUsers.server_address = 'openldap'
LocalLDAPCreateUsers.server_port = 389
LocalLDAPCreateUsers.lookup_dn = True
LocalLDAPCreateUsers.use_ssl = False
LocalLDAPCreateUsers.lookup_dn_user_dn_attribute = 'cn'
LocalLDAPCreateUsers.lookup_dn_search_filter = '(&({login_attr}={login})(memberOf=cn=jupyterhub,ou=groups,${DOMAIN_COMPONENT}))'
LocalLDAPCreateUsers.lookup_dn_search_user = 'cn=admin,${DOMAIN_COMPONENT}'
LocalLDAPCreateUsers.lookup_dn_search_password = '${ADMIN_PASSWORD}'
LocalLDAPCreateUsers.bind_dn_template = 'cn={username},ou=users,${DOMAIN_COMPONENT}'
LocalLDAPCreateUsers.allowed_groups = []
LocalLDAPCreateUsers.user_search_base = 'ou=users,${DOMAIN_COMPONENT}'
LocalLDAPCreateUsers.user_attribute = 'uid'
LocalLDAPCreateUsers.create_system_users = True
LocalLDAPCreateUsers.use_lookup_dn_username = False
