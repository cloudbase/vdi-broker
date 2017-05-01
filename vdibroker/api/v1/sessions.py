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
from vdibroker.api.v1.views import session_view
from vdibroker import exception
from vdibroker.sessions import api

LOG = logging.getLogger(__name__)


class SessionController(api_wsgi.Controller):
    def __init__(self):
        self._session_api = api.API()
        super(SessionController, self).__init__()

    def show(self, req, application_id, id):
        session = self._session_api.get_session(
            req.environ["vdibroker.context"], id)
        if not session:
            raise exc.HTTPNotFound()

        return session_view.single(req, session)

    def index(self, req, application_id):
        return session_view.collection(
            req, self._session_api.get_sessions(
                req.environ['vdibroker.context'], application_id))

    def create(self, req, application_id):
        return session_view.single(req, self._session_api.create(
            req.environ['vdibroker.context'], application_id))

    def delete(self, req, application_id, id):
        try:
            self._session_api.delete(
                req.environ['vdibroker.context'], id)
            raise exc.HTTPNoContent()
        except exception.NotFound as ex:
            raise exc.HTTPNotFound(explanation=ex.msg)


def create_resource():
    return api_wsgi.Resource(SessionController())
