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

import threading
import time
import uuid

from novaclient import client as nova_client
from oslo_log import log as logging

from vdibroker.applications import api as application_api
from vdibroker.applications.pool import keystone
from vdibroker import constants
from vdibroker import exception
from vdibroker import utils

NOVA_API_VERSION = 2
GLANCE_API_VERSION = 1
INSTANCE_NAME_FORMAT = "vdi-broker-%s"
SLEEP_INTERVAL = 5

LOG = logging.getLogger(__name__)

_pool_managers = {}


class PoolManager(object):
    def __init__(self, ctxt, application_id):
        self._application_api = application_api.API()
        self._ctxt = ctxt
        self._application_id = application_id
        self._trust_id = None
        self._thread = None
        self._done = False

    @staticmethod
    def _get_unique_name():
        return INSTANCE_NAME_FORMAT % str(uuid.uuid4())

    def _get_flavor(self, nova, flavor_name):
        flavors = nova.flavors.findall(name=flavor_name)
        if not flavors:
            raise exception.VDIBrokerException(
                "Flavor not found: %s" % flavor_name)
        return flavors[0]

    def _wait_for_instance(self, nova, instance_id, expected_status='ACTIVE'):
        instance = nova.servers.get(instance_id)
        while instance.status not in [expected_status, 'ERROR']:
            LOG.debug('Instance %(id)s status: %(status)s. '
                      'Waiting for status: "%(expected_status)s".',
                      {'id': instance_id, 'status': instance.status,
                       'expected_status': expected_status})
            time.sleep(2)
            instance = nova.servers.get(instance.id)
        if instance.status != expected_status:
            raise exception.VDIBrokerException(
                "VM is in status: %s" % instance.status)

    def _spawn_instances(self, count, image_id, flavor_name, keypair_name,
                         network_id, userdata, fip_pool_name, sec_group_id):
        session = keystone.create_keystone_session(self._trust_id)
        nova = nova_client.Client(NOVA_API_VERSION, session=session)

        flavor = self._get_flavor(nova, flavor_name)

        instances = []
        try:
            instance = None
            floating_ip = None

            instance = nova.servers.create(
                name=self._get_unique_name(),
                image=image_id,
                flavor=flavor,
                key_name=keypair_name,
                userdata=userdata,
                nics=[{'net-id': network_id}])

            floating_ip = nova.floating_ips.create(pool=fip_pool_name)
            instance.add_security_group(sec_group_id)

            instances.append((instance, floating_ip))
        except Exception as ex:
            LOG.exception(ex)
            if instance:
                nova.servers.delete(instance)
            if floating_ip:
                nova.floating_ips.delete(floating_ip)

        instances_data = []
        for instance, floating_ip in instances:
            try:
                self._wait_for_instance(nova, instance.id, 'ACTIVE')
                instance.add_floating_ip(floating_ip)
                # utils.wait_for_port_connectivity(
                #    floating_ip.ip, constants.RDP_PORT)
                instances_data.append((instance.id, floating_ip.ip))
            except Exception as ex:
                LOG.exception(ex)
                nova.servers.delete(instance)
                nova.floating_ips.delete(floating_ip)

        return instances_data

    def _run(self):
        while not self._done:
            application = self._application_api.get_application(
                self._ctxt, self._application_id)
            instances_count = max(
                application["pool_size"] -
                len(application["instances_data"]), 0)

            if instances_count > 0:
                image_data = application["image_data"]
                image_id = image_data["image_id"]
                flavor_name = image_data["flavor_name"]
                network_id = image_data["network_id"]
                fip_pool_name = image_data["fip_pool_name"]
                sec_group_id = image_data["sec_group_id"]
                keypair_name = image_data.get("keypair_name")
                userdata = image_data.get("userdata")

                LOG.info("Spawning %(instances_count)s instances for "
                         "application %(application_id)s",
                         {"instances_count": instances_count,
                          "application_id": self._application_id})

                instances_data = self._spawn_instances(
                    instances_count, image_id, flavor_name, keypair_name,
                    network_id, userdata, fip_pool_name, sec_group_id)

                LOG.debug("Instances data: %s", instances_data)

                if instances_data:
                    self._application_api.add_application_instances_data(
                        self._ctxt, self._application_id, instances_data)

            time.sleep(SLEEP_INTERVAL)

    def start(self):
        self._trust_id = keystone.create_trust(self._ctxt)
        self._thread = threading.Thread(target=self._run)
        self._done = False
        self._thread.start()

    def stop(self, join=False):
        self._done = True
        if join:
            self._thread.join()

        keystone.delete_trust(self._trust_id)
        self._trust_id = None


def start_pool_manager(ctxt, application_id):
    global _pool_managers
    if application_id not in _pool_managers:
        pool_manager = PoolManager(ctxt, application_id)
        pool_manager.start()
        _pool_managers[application_id] = pool_manager


def stop_pool_manager(ctxt, application_id):
    global _pool_managers
    pool_manager = _pool_managers.pop(application_id, None)
    if pool_manager:
        pool_manager.stop()
