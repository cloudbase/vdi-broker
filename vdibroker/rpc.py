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

from oslo_config import cfg
import oslo_messaging as messaging

from vdibroker import context
import vdibroker.exception

rpc_opts = [
    cfg.StrOpt('messaging_transport_url',
               default="rabbit://guest:guest@127.0.0.1:5672/",
               help='Messaging transport url'),
]

CONF = cfg.CONF
CONF.register_opts(rpc_opts)

ALLOWED_EXMODS = [
    vdibroker.exception.__name__,
]


class RequestContextSerializer(messaging.Serializer):

    def __init__(self, base):
        self._base = base

    def serialize_entity(self, ctxt, entity):
        if not self._base:
            return entity
        return self._base.serialize_entity(ctxt, entity)

    def deserialize_entity(self, ctxt, entity):
        if not self._base:
            return entity
        return self._base.deserialize_entity(ctxt, entity)

    def serialize_context(self, ctxt):
        return ctxt.to_dict()

    def deserialize_context(self, ctxt):
        return context.RequestContext.from_dict(ctxt)


def _get_transport():
    return messaging.get_transport(cfg.CONF, CONF.messaging_transport_url,
                                   allowed_remote_exmods=ALLOWED_EXMODS)


def get_client(target, serializer=None):
    serializer = RequestContextSerializer(serializer)
    return messaging.RPCClient(_get_transport(), target, serializer=serializer)


def get_server(target, endpoints, serializer=None):
    serializer = RequestContextSerializer(serializer)
    return messaging.get_rpc_server(_get_transport(), target, endpoints,
                                    executor='eventlet',
                                    serializer=serializer)
