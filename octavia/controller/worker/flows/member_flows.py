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
from octavia.controller.worker.tasks import network_tasks


class MemberFlows(object):

    def get_create_member_flow(self):
        """Create a flow to create a member

        :returns: The flow for creating a member
        """
        create_member_flow = linear_flow.Flow(constants.CREATE_MEMBER_FLOW)
        create_member_flow.add(network_tasks.CalculateDelta(
            requires=constants.LOADBALANCER,
            provides=constants.DELTAS))
        create_member_flow.add(network_tasks.HandleNetworkDeltas(
            requires=constants.DELTAS))
        create_member_flow.add(amphora_driver_tasks.AmphoraePostNetworkPlug(
            requires=constants.LOADBALANCER
        ))
        create_member_flow.add(amphora_driver_tasks.ListenerUpdate(
            requires=(constants.LISTENER, constants.VIP)))
        create_member_flow.add(database_tasks.
                               MarkLBAndListenerActiveInDB(
                                   requires=(constants.LOADBALANCER,
                                             constants.LISTENER)))

        return create_member_flow

    def get_delete_member_flow(self):
        """Create a flow to delete a member

        :returns: The flow for deleting a member
        """
        delete_member_flow = linear_flow.Flow(constants.DELETE_MEMBER_FLOW)
        delete_member_flow.add(model_tasks.
                               DeleteModelObject(rebind={'object': 'member'}))
        delete_member_flow.add(amphora_driver_tasks.ListenerUpdate(
            requires=['listener', 'vip']))
        delete_member_flow.add(database_tasks.DeleteMemberInDB(
            requires='member_id'))
        delete_member_flow.add(database_tasks.
                               MarkLBAndListenerActiveInDB(
                                   requires=['loadbalancer', 'listener']))

        return delete_member_flow

    def get_update_member_flow(self):
        """Create a flow to update a member

        :returns: The flow for updating a member
        """
        update_member_flow = linear_flow.Flow(constants.UPDATE_MEMBER_FLOW)
        update_member_flow.add(model_tasks.
                               UpdateAttributes(
                                   rebind={'object': 'member'},
                                   requires=['update_dict']))
        update_member_flow.add(amphora_driver_tasks.ListenerUpdate(
            requires=['listener', 'vip']))
        update_member_flow.add(database_tasks.UpdateMemberInDB(
            requires=['member', 'update_dict']))
        update_member_flow.add(database_tasks.
                               MarkLBAndListenerActiveInDB(
                                   requires=['loadbalancer', 'listener']))

        return update_member_flow
