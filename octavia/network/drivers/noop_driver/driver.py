# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_log import log as logging

from octavia.network import base as driver_base

LOG = logging.getLogger(__name__)


class NoopManager(object):
    def __init__(self):
        super(NoopManager, self).__init__()
        self.networkconfigconfig = {}

    def allocate_vip(self, load_balancer):
        LOG.debug("Network %s no-op, allocate_vip load_balancer %s",
                  self.__class__.__name__, load_balancer)
        self.networkconfigconfig[load_balancer] = (
            load_balancer, 'allocate_vip')

    def deallocate_vip(self, vip):
        LOG.debug("Network %s no-op, deallocate_vip vip %s",
                  self.__class__.__name__, vip.ip_address)
        self.networkconfigconfig[vip.ip_address] = (vip,
                                                    'deallocate_vip')

    def plug_vip(self, load_balancer, vip):
        LOG.debug("Network %s no-op, plug_vip load_balancer %s, vip %s",
                  self.__class__.__name__,
                  load_balancer.id, vip.ip_address)
        self.networkconfigconfig[(load_balancer.id,
                                  vip.ip_address)] = (load_balancer, vip,
                                                      'plug_vip')

    def unplug_vip(self, load_balancer, vip):
        LOG.debug("Network %s no-op, unplug_vip load_balancer %s, vip %s",
                  self.__class__.__name__,
                  load_balancer.id, vip.ip_address)
        self.networkconfigconfig[(load_balancer.id,
                                  vip.ip_address)] = (load_balancer, vip,
                                                      'unplug_vip')

    def plug_network(self, amphora_id, network_id, ip_address=None):
        LOG.debug("Network %s no-op, plug_network amphora_id %s, network_id "
                  "%s, ip_address %s", self.__class__.__name__, amphora_id,
                  network_id, ip_address)
        self.networkconfigconfig[(amphora_id, network_id, ip_address)] = (
            amphora_id, network_id, ip_address, 'plug_network')

    def unplug_network(self, amphora_id, network_id):
        LOG.debug("Network %s no-op, unplug_network amphora_id %s, "
                  "network_id %s",
                  self.__class__.__name__, amphora_id, network_id)
        self.networkconfigconfig[(amphora_id, network_id)] = (
            amphora_id, network_id, 'unplug_network')

    def get_plugged_networks(self, amphora_id):
        LOG.debug("Network %s no-op, get_plugged_networks amphora_id %s",
                  self.__class__.__name__, amphora_id)
        self.networkconfigconfig[amphora_id] = (
            amphora_id, 'get_plugged_networks')

    def update_vip(self, load_balancer):
        LOG.debug("Network %s no-op, update_vip load_balancer %s",
                  self.__class__.__name__, load_balancer)
        self.networkconfigconfig[load_balancer] = (load_balancer, 'update_vip')

    def get_network(self, network_id=None, subnet_id=None):
        LOG.debug("Network %s no-op, get_network network_id %s",
                  self.__class__.__name__, network_id)
        self.networkconfigconfig[network_id, subnet_id] = (
            network_id, subnet_id, 'get_network')


class NoopNetworkDriver(driver_base.AbstractNetworkDriver):
    def __init__(self):
        super(NoopNetworkDriver, self).__init__()
        self.driver = NoopManager()

    def allocate_vip(self, load_balancer):
        self.driver.allocate_vip(load_balancer)

    def deallocate_vip(self, vip):
        self.driver.deallocate_vip(vip)

    def plug_vip(self, load_balancer, vip):
        self.driver.plug_vip(load_balancer, vip)

    def unplug_vip(self, load_balancer, vip):
        self.driver.unplug_vip(load_balancer, vip)

    def plug_network(self, amphora_id, network_id, ip_address=None):
        self.driver.plug_network(amphora_id, network_id, ip_address)

    def unplug_network(self, amphora_id, network_id):
        self.driver.unplug_network(amphora_id, network_id)

    def get_plugged_networks(self, amphora_id):
        self.driver.get_plugged_networks(amphora_id)

    def update_vip(self, load_balancer):
        self.driver.update_vip(load_balancer)

    def get_network(self, network_id=None, subnet_id=None):
        self.driver.get_network(network_id, subnet_id)
