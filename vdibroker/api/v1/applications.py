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

from webob import exc

from oslo_log import log as logging

from vdibroker.api import wsgi as api_wsgi
from vdibroker.api.v1.views import application_view
from vdibroker import exception
from vdibroker.applications import api

LOG = logging.getLogger(__name__)


class ApplicationController(api_wsgi.Controller):
    def __init__(self):
        self._application_api = api.API()
        super(ApplicationController, self).__init__()

    def show(self, req, id):
        application = self._application_api.get_application(
            req.environ["vdibroker.context"], id)
        if not application:
            raise exc.HTTPNotFound()

        return application_view.single(req, application)

    def index(self, req):
        return application_view.collection(
            req, self._application_api.get_applications(
                req.environ['vdibroker.context']))

    def _validate_create_body(self, body):
        try:
            application = body["application"]
            name = application["name"]
            description = application.get("description")
            application_type = application["type"]
            image_data = application["image_data"]
            image_data["image_id"]
            image_data["flavor_name"]
            image_data["network_id"]
            image_data["fip_pool_name"]
            image_data["sec_group_id"]
            pool_size = application["pool_size"]
            return name, description, application_type, image_data, pool_size
        except Exception as ex:
            LOG.exception(ex)
            if hasattr(ex, "message"):
                msg = ex.message
            else:
                msg = str(ex)
            raise exception.InvalidInput(msg)

    def create(self, req, body):
        (name, description, application_type,
         image_data, pool_size) = self._validate_create_body(body)
        return application_view.single(req, self._application_api.create(
            req.environ['vdibroker.context'], name, description,
            application_type, image_data, pool_size))

    def delete(self, req, id):
        try:
            self._application_api.delete(req.environ['vdibroker.context'], id)
            raise exc.HTTPNoContent()
        except exception.NotFound as ex:
            raise exc.HTTPNotFound(explanation=ex.msg)


def create_resource():
    return api_wsgi.Resource(ApplicationController())
