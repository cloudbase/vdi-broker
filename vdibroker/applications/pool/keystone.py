# Copyright 2017 Cloudbase Solutions, SRL.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from keystoneauth1 import exceptions as ks_exceptions
from keystoneauth1 import loading
from keystoneauth1 import session as ks_session
from keystoneclient.v3 import client as kc_v3
from oslo_config import cfg
from oslo_log import log as logging

from vdibroker import exception

opts = [
    cfg.BoolOpt('allow_untrusted',
                default=False,
                help='Allow untrusted SSL/TLS certificates.'),
]

CONF = cfg.CONF
CONF.register_opts(opts, 'keystone')

LOG = logging.getLogger(__name__)

TRUSTEE_CONF_GROUP = 'trustee'
loading.register_auth_conf_options(CONF, TRUSTEE_CONF_GROUP, )


def _get_trusts_auth_plugin(trust_id=None):
    return loading.load_auth_from_conf_options(
        CONF, TRUSTEE_CONF_GROUP, trust_id=trust_id)


def create_trust(ctxt):
    LOG.debug("Creating Keystone trust")

    trusts_auth_plugin = _get_trusts_auth_plugin()

    loader = loading.get_plugin_loader("v3token")
    auth = loader.load_from_options(
        auth_url=trusts_auth_plugin.auth_url,
        token=ctxt.auth_token,
        project_name=ctxt.project_name,
        project_domain_name=ctxt.project_domain)
    session = ks_session.Session(
        auth=auth, verify=not CONF.keystone.allow_untrusted)

    try:
        trustee_user_id = trusts_auth_plugin.get_user_id(session)
    except ks_exceptions.Unauthorized as ex:
        LOG.exception(ex)
        raise exception.NotAuthorized("Trustee authentication failed")

    trustor_user_id = ctxt.user
    trustor_proj_id = ctxt.tenant
    roles = ctxt.roles

    LOG.debug("Granting Keystone trust. Trustor: %(trustor_user_id)s, trustee:"
              " %(trustee_user_id)s, project: %(trustor_proj_id)s, roles:"
              " %(roles)s",
              {"trustor_user_id": trustor_user_id,
               "trustee_user_id": trustee_user_id,
               "trustor_proj_id": trustor_proj_id,
               "roles": roles})

    # Trusts are not supported before Keystone v3
    client = kc_v3.Client(session=session)
    trust = client.trusts.create(trustor_user=trustor_user_id,
                                 trustee_user=trustee_user_id,
                                 project=trustor_proj_id,
                                 impersonation=True,
                                 role_names=roles)
    LOG.debug("Trust id: %s" % trust.id)
    return trust.id


def delete_trust(trust_id):
    LOG.debug("Deleting trust id: %s", trust_id)

    auth = _get_trusts_auth_plugin(trust_id)
    session = ks_session.Session(
        auth=auth, verify=not CONF.keystone.allow_untrusted)
    client = kc_v3.Client(session=session)
    try:
        client.trusts.delete(trust_id)
    except ks_exceptions.NotFound:
        LOG.debug("Trust id not found: %s", trust_id)


def create_keystone_session(trust_id):
    verify = not CONF.keystone.allow_untrusted
    auth = _get_trusts_auth_plugin(trust_id)
    return ks_session.Session(auth=auth, verify=verify)
