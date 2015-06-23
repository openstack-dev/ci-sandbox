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
#

import logging
import time

from oslo.config import cfg
from stevedore import driver as stevedore_driver
from taskflow import task
from taskflow.types import failure

from octavia.common import constants
from octavia.common import exceptions
from octavia.i18n import _LE, _LW

CONF = cfg.CONF
CONF.import_group('controller_worker', 'octavia.common.config')
LOG = logging.getLogger(__name__)


class BaseComputeTask(task.Task):
    """Base task to load drivers common to the tasks."""

    def __init__(self, **kwargs):
        super(BaseComputeTask, self).__init__(**kwargs)
        self.compute = stevedore_driver.DriverManager(
            namespace='octavia.compute.drivers',
            name=CONF.controller_worker.compute_driver,
            invoke_on_load=True,
            invoke_kwds={'region': CONF.nova_region_name}
        ).driver


class ComputeCreate(BaseComputeTask):
    """Create the compute instance for a new amphora."""

    def execute(self, amphora_id):
        """Create an amphora

        :returns: an amphora
        """
        LOG.debug("Nova Create execute for amphora with id %s" % amphora_id)

        try:
            compute_id = self.compute.build(
                name="amphora-" + amphora_id,
                amphora_flavor=CONF.controller_worker.amp_flavor_id,
                image_id=CONF.controller_worker.amp_image_id,
                key_name=CONF.controller_worker.amp_ssh_key_name,
                sec_groups=CONF.controller_worker.amp_secgroup_list,
                network_ids=[CONF.controller_worker.amp_network])

            LOG.debug("Server created with id: %s for amphora id: %s" %
                      (compute_id, amphora_id))
            return compute_id

        except Exception as e:
            LOG.error(_LE("Nova create for amphora id: %(amp)s "
                          "failed: %(exp)s"),
                      {'amp': amphora_id, 'exp': e})
            raise e

    def revert(self, result, amphora_id, *args, **kwargs):
        """This method will revert the creation of the

        amphora. So it will just delete it in this flow
        """
        if isinstance(result, failure.Failure):
            return
        compute_id = result
        LOG.warn(_LW("Reverting Nova create for amphora with id"
                     "%(amp)s and compute id: %(comp)s"),
                 {'amp': amphora_id, 'comp': compute_id})
        try:
            self.compute.delete(compute_id)
        except Exception as e:
            LOG.error(_LE("Reverting Nova create failed"
                          " with exception %s"), e)


class ComputeWait(BaseComputeTask):
    """Wait for the compute driver to mark the amphora active."""

    def execute(self, compute_id):
        """Wait for the compute driver to mark the amphora active

        :raises: Generic exception if the amphora is not active
        :returns: An amphora object
        """
        time.sleep(CONF.controller_worker.amp_active_wait_sec)
        amp = self.compute.get_amphora(compute_id)
        if amp.status == constants.ACTIVE:
            return amp

        raise exceptions.ComputeWaitTimeoutException()
