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


import functools

from oslo_concurrency import lockutils
from oslo_log import log as logging

from vdibroker.applications.pool import manager as pool_manager
from vdibroker.db import api as db_api
from vdibroker.db.sqlalchemy import models
from vdibroker import constants
from vdibroker import exception

VERSION = "1.0"

LOG = logging.getLogger(__name__)


def application_synchronized(func):
    @functools.wraps(func)
    def wrapper(self, ctxt, application_id, *args, **kwargs):
        @lockutils.synchronized(application_id)
        def inner():
            return func(self, ctxt, application_id, *args, **kwargs)
        return inner()
    return wrapper


def remote_session_synchronized(func):
    @functools.wraps(func)
    def wrapper(self, ctxt, session_id, *args, **kwargs):
        @lockutils.synchronized(session_id)
        def inner():
            return func(self, ctxt, session_id, *args, **kwargs)
        return inner()
    return wrapper


class ConductorServerEndpoint(object):
    def create_application(self, ctxt, name, description, application_type,
                           image_data, pool_size):
        application = models.Application()
        application.name = name
        application.description = description
        application.type = application_type
        application.image_data = image_data
        application.instances_data = []
        application.pool_size = pool_size

        db_api.add_application(ctxt, application)
        LOG.info("Application created: %s", application.id)

        pool_manager.start_pool_manager(ctxt, application.id)

        return self.get_application(ctxt, application.id)

    def get_applications(self, ctxt):
        return db_api.get_applications(ctxt)

    @application_synchronized
    def get_application(self, ctxt, application_id):
        return self._get_application(ctxt, application_id)

    def _get_application(self, ctxt, application_id):
        application = db_api.get_application(ctxt, application_id)
        if not application:
            raise exception.NotFound("Application not found")
        return application

    @application_synchronized
    def delete_application(self, ctxt, application_id):
        pool_manager.stop_pool_manager(ctxt, application_id)
        db_api.delete_application(ctxt, application_id)

    @application_synchronized
    def add_application_instances_data(self, ctxt, application_id,
                                       instances_data):
        application = self._get_application(ctxt, application_id)
        application.instances_data.extend(instances_data)
        db_api.update_application(ctxt, application)

    @application_synchronized
    def create_remote_session(self, ctxt, application_id):
        application = self._get_application(ctxt, application_id)

        if not application.instances_data:
            raise exception.ApplicationInstanceUnavailable()

        instance_id, floating_ip = application.instances_data.pop(0)

        remote_session = models.RemoteSession()
        remote_session.application_id = application_id
        remote_session.instance_id = instance_id
        remote_session.connection_data = {
            "host": floating_ip, "port": constants.RDP_PORT}

        db_api.add_remote_session(ctxt, remote_session)
        LOG.info("Remote session created: %s", remote_session.id)
        db_api.update_application(ctxt, application)
        return self.get_remote_session(ctxt, remote_session.id)

    def get_remote_sessions(self, ctxt, application_id):
        return db_api.get_remote_sessions(ctxt, application_id)

    @remote_session_synchronized
    def get_remote_session(self, ctxt, session_id):
        session = db_api.get_remote_session(ctxt, session_id)
        if not session:
            raise exception.NotFound("Remote session not found")
        return session

    @remote_session_synchronized
    def delete_remote_session(self, ctxt, session_id):
        db_api.delete_remote_session(ctxt, session_id)
