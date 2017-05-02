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

import socket
import time

from oslo_config import cfg
from oslo_log import log as logging

from vdibroker import exception

CONF = cfg.CONF
logging.register_options(CONF)

LOG = logging.getLogger(__name__)


def setup_logging():
    logging.setup(CONF, 'vdibroker')


def get_hostname():
    return socket.gethostname()


def walk_class_hierarchy(clazz, encountered=None):
    """Walk class hierarchy, yielding most derived classes first."""
    if not encountered:
        encountered = []
    for subclass in clazz.__subclasses__():
        if subclass not in encountered:
            encountered.append(subclass)
            # drill down to leaves first
            for subsubclass in walk_class_hierarchy(subclass, encountered):
                yield subsubclass
            yield subclass


def _check_port_open(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(1)
        s.connect((host, port))
        return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False
    finally:
        s.close()


def wait_for_port_connectivity(address, port, max_wait=300):
    i = 0
    while not _check_port_open(address, port) and i < max_wait:
        time.sleep(1)
        i += 1
    if i == max_wait:
        raise exception.VDIBrokerException("Connection failed on port %s" %
                                           port)
