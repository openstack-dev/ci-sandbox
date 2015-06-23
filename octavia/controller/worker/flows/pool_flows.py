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

from taskflow.patterns import linear_flow

from octavia.common import constants
from octavia.controller.worker.tasks import amphora_driver_tasks
from octavia.controller.worker.tasks import database_tasks
from octavia.controller.worker.tasks import model_tasks


class PoolFlows(object):

    def get_create_pool_flow(self):
        """Create a flow to create a pool

        :returns: The flow for creating a pool
        """
        create_pool_flow = linear_flow.Flow(constants.CREATE_POOL_FLOW)
        create_pool_flow.add(amphora_driver_tasks.ListenerUpdate(
            requires=['listener', 'vip']))
        create_pool_flow.add(database_tasks.MarkLBAndListenerActiveInDB(
            requires=['loadbalancer', 'listener']))

        return create_pool_flow

    def get_delete_pool_flow(self):
        """Create a flow to delete a pool

        :returns: The flow for deleting a pool
        """
        delete_pool_flow = linear_flow.Flow(constants.DELETE_POOL_FLOW)
        delete_pool_flow.add(model_tasks.
                             DeleteModelObject(rebind={'object': 'pool'}))
        delete_pool_flow.add(amphora_driver_tasks.ListenerUpdate(
            requires=['listener', 'vip']))
        delete_pool_flow.add(database_tasks.DeletePoolInDB(requires='pool_id'))
        delete_pool_flow.add(database_tasks.MarkLBAndListenerActiveInDB(
            requires=['loadbalancer', 'listener']))

        return delete_pool_flow

    def get_update_pool_flow(self):
        """Create a flow to update a pool

        :returns: The flow for updating a pool
        """
        update_pool_flow = linear_flow.Flow(constants.UPDATE_POOL_FLOW)
        update_pool_flow.add(model_tasks.
                             UpdateAttributes(
                                 rebind={'object': 'pool'},
                                 requires=['update_dict']))
        update_pool_flow.add(amphora_driver_tasks.ListenerUpdate(
            requires=['listener', 'vip']))
        update_pool_flow.add(database_tasks.UpdatePoolInDB(
            requires=['pool', 'update_dict']))
        update_pool_flow.add(database_tasks.MarkLBAndListenerActiveInDB(
            requires=['loadbalancer', 'listener']))

        return update_pool_flow
