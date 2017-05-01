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

from oslo_log import log as logging

from vdibroker import api
from vdibroker.api.v1 import applications
from vdibroker.api.v1 import sessions

LOG = logging.getLogger(__name__)


class ExtensionManager(object):
    def get_resources(self):
        return []

    def get_controller_extensions(self):
        return []


class APIRouter(api.APIRouter):
    ExtensionManager = ExtensionManager

    def _setup_routes(self, mapper, ext_mgr):
        mapper.redirect("", "/")

        self.resources['applications'] = applications.create_resource()
        mapper.resource('application', 'applications',
                        controller=self.resources['applications'])

        self.resources['sessions'] = \
            sessions.create_resource()
        mapper.resource('session', 'applications/{application_id}/sessions',
                        controller=self.resources['sessions'])
