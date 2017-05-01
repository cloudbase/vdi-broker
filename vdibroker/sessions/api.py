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

from vdibroker.conductor.rpc import client as rpc_client


class API(object):
    def __init__(self):
        self._rpc_client = rpc_client.ConductorClient()

    def create(self, ctxt, application_id):
        return self._rpc_client.create_remote_session(
            ctxt, application_id)

    def delete(self, ctxt, session_id):
        return self._rpc_client.delete_remote_session(ctxt, session_id)

    def get_sessions(self, ctxt, application_id):
        return self._rpc_client.get_remote_sessions(ctxt, application_id)

    def get_session(self, ctxt, session_id):
        return self._rpc_client.get_remote_session(ctxt, session_id)
