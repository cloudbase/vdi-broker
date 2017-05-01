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


import oslo_messaging as messaging

from vdibroker import rpc

VERSION = "1.0"


class ConductorClient(object):
    def __init__(self):
        target = messaging.Target(topic='vdibroker_conductor', version=VERSION)
        self._client = rpc.get_client(target)

    def create_application(self, ctxt, name, description, application_type,
                           image_id, pool_size):
        return self._client.call(
            ctxt, 'create_application',
            name=name,
            application_type=application_type,
            description=description,
            image_id=image_id,
            pool_size=pool_size)

    def get_applications(self, ctxt):
        return self._client.call(
            ctxt, 'get_applications')

    def get_application(self, ctxt, application_id):
        return self._client.call(
            ctxt, 'get_application', application_id=application_id)

    def delete_application(self, ctxt, application_id):
        return self._client.call(
            ctxt, 'delete_application', application_id=application_id)

    def create_remote_session(self, ctxt, application_id):
        return self._client.call(
            ctxt, 'create_remote_session',
            application_id=application_id)

    def get_remote_sessions(self, ctxt, application_id):
        return self._client.call(
            ctxt, 'get_remote_sessions',
            application_id=application_id)

    def get_remote_session(self, ctxt, session_id):
        return self._client.call(
            ctxt, 'get_remote_session', session_id=session_id)

    def delete_remote_session(self, ctxt, session_id):
        return self._client.call(
            ctxt, 'delete_remote_session', session_id=session_id)
