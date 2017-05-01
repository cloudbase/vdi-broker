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

import platform

from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging
from oslo_service import service
from oslo_service import wsgi

from vdibroker import rpc
from vdibroker import utils

service_opts = [
    cfg.StrOpt('api_listen',
               default="0.0.0.0",
               help='IP address on which the VDI broker API listens'),
    cfg.PortOpt('api_listen_port',
                default=9449,
                help='Port on which the VDI broker API listens'),
    cfg.IntOpt('api_workers',
               help='Number of workers for the VDI broker API service. '
                    'The default is equal to the number of CPUs available.'),
    cfg.IntOpt('messaging_workers',
               help='Number of workers for the messaging service. '
                    'The default is equal to the number of CPUs available.'),
]

CONF = cfg.CONF
CONF.register_opts(service_opts)
LOG = logging.getLogger(__name__)


class WSGIService(service.ServiceBase):
    def __init__(self, name):
        self._host = CONF.api_listen
        self._port = CONF.api_listen_port

        if platform.system() == "Windows":
            self._workers = 1
        else:
            self._workers = (
                CONF.api_workers or processutils.get_worker_count())

        self._loader = wsgi.Loader(CONF)
        self._app = self._loader.load_app(name)

        self._server = wsgi.Server(CONF,
                                   name,
                                   self._app,
                                   host=self._host,
                                   port=self._port)

    def get_workers_count(self):
        return self._workers

    def start(self):
        self._server.start()

    def stop(self):
        self._server.stop()

    def wait(self):
        self._server.wait()

    def reset(self):
        self._server.reset()


class MessagingService(service.ServiceBase):
    def __init__(self, topic, endpoints, version):
        target = messaging.Target(topic=topic,
                                  server=utils.get_hostname(),
                                  version=version)
        self._server = rpc.get_server(target, endpoints)

        self._workers = (CONF.messaging_workers or
                         processutils.get_worker_count())

    def get_workers_count(self):
        return self._workers

    def start(self):
        self._server.start()

    def stop(self):
        self._server.stop()

    def wait(self):
        pass

    def reset(self):
        self._server.reset()

