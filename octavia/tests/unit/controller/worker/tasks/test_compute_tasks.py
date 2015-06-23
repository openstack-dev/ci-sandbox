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

import time

import mock
from oslo_config import cfg
from oslo_config import fixture as oslo_fixture
from oslo_utils import uuidutils

from octavia.common import constants
from octavia.common import exceptions
from octavia.controller.worker.tasks import compute_tasks
import octavia.tests.unit.base as base

AMP_FLAVOR_ID = 10
AMP_IMAGE_ID = 11
AMP_SSH_KEY_NAME = None
AMP_NET = uuidutils.generate_uuid()
AMP_SEC_GROUPS = []
AMP_WAIT = 12
AMPHORA_ID = uuidutils.generate_uuid()
COMPUTE_ID = uuidutils.generate_uuid()
LB_NET_IP = '192.0.2.1'
AUTH_VERSION = '2'


class TestException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

_amphora_mock = mock.MagicMock()


class TestComputeTasks(base.TestCase):

    def setUp(self):
        conf = oslo_fixture.Config(cfg.CONF)
        conf.config(group="controller_worker", amp_flavor_id=AMP_FLAVOR_ID)
        conf.config(group="controller_worker", amp_image_id=AMP_IMAGE_ID)
        conf.config(group="controller_worker",
                    amp_ssh_key_name=AMP_SSH_KEY_NAME)
        conf.config(group="controller_worker", amp_network=AMP_NET)
        conf.config(group="controller_worker", amp_active_wait_sec=AMP_WAIT)
        conf.config(group="keystone_authtoken", auth_version=AUTH_VERSION)

        _amphora_mock.id = AMPHORA_ID

        logging_mock = mock.MagicMock()
        compute_tasks.LOG = logging_mock

        super(TestComputeTasks, self).setUp()

    @mock.patch('stevedore.driver.DriverManager.driver')
    def test_compute_create(self, mock_driver):

        mock_driver.build.side_effect = [COMPUTE_ID, TestException('test')]

        # Test execute()
        createcompute = compute_tasks.ComputeCreate()
        compute_id = createcompute.execute(_amphora_mock.id)

        # Validate that the build method was called properly
        mock_driver.build.assert_called_once_with(
            name="amphora-" + _amphora_mock.id,
            amphora_flavor=AMP_FLAVOR_ID,
            image_id=AMP_IMAGE_ID,
            key_name=AMP_SSH_KEY_NAME,
            sec_groups=AMP_SEC_GROUPS,
            network_ids=[AMP_NET])

        # Make sure it returns the expected compute_id
        assert(compute_id == COMPUTE_ID)

        # Test that a build exception is raised

        createcompute = compute_tasks.ComputeCreate()
        self.assertRaises(TestException,
                          createcompute.execute,
                          _amphora_mock)

        # Test revert()

        _amphora_mock.compute_id = COMPUTE_ID

        createcompute = compute_tasks.ComputeCreate()
        createcompute.revert(compute_id, _amphora_mock.id)

        # Validate that the delete method was called properly
        mock_driver.delete.assert_called_once_with(
            COMPUTE_ID)

        # Test that a delete exception is not raised

        createcompute.revert(COMPUTE_ID, _amphora_mock.id)

    @mock.patch('stevedore.driver.DriverManager.driver')
    @mock.patch('time.sleep')
    def test_compute_wait(self,
                          mock_time_sleep,
                          mock_driver):

        _amphora_mock.compute_id = COMPUTE_ID
        _amphora_mock.status = constants.ACTIVE
        _amphora_mock.lb_network_ip = LB_NET_IP

        mock_driver.get_amphora.return_value = _amphora_mock

        computewait = compute_tasks.ComputeWait()
        computewait.execute(COMPUTE_ID)

        time.sleep.assert_called_once_with(AMP_WAIT)

        mock_driver.get_amphora.assert_called_once_with(COMPUTE_ID)

        _amphora_mock.status = constants.DELETED

        self.assertRaises(exceptions.ComputeWaitTimeoutException,
                          computewait.execute,
                          _amphora_mock)
