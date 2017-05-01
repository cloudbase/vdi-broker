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

    def create(self, ctxt, name, description, application_type,
               image_id, pool_size):
        return self._rpc_client.create_application(
            ctxt, name, description, application_type, image_id, pool_size)

    def delete(self, ctxt, application_id):
        return self._rpc_client.delete_application(ctxt, application_id)

    def get_applications(self, ctxt):
        return self._rpc_client.get_applications(ctxt)

    def get_application(self, ctxt, application_id):
        return self._rpc_client.get_application(ctxt, application_id)
