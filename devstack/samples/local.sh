#!/usr/bin/env bash

# Sample ``local.sh`` that configures two simple webserver instances and sets
# up a Neutron LBaaS Version 2 loadbalancer backed by Octavia.

# Keep track of the DevStack directory
TOP_DIR=$(cd $(dirname "$0") && pwd)
BOOT_DELAY=60

# Import common functions
source ${TOP_DIR}/functions

# Use openrc + stackrc for settings
source ${TOP_DIR}/stackrc

# Destination path for installation ``DEST``
DEST=${DEST:-/opt/stack}

if is_service_enabled nova; then

    # Get OpenStack demo user auth
    source ${TOP_DIR}/openrc demo demo

    # Create an SSH key to use for the instances
    DEVSTACK_LBAAS_SSH_KEY_NAME=$(hostname)_DEVSTACK_LBAAS_SSH_KEY_RSA
    DEVSTACK_LBAAS_SSH_KEY_DIR=${TOP_DIR}
    DEVSTACK_LBAAS_SSH_KEY=${DEVSTACK_LBAAS_SSH_KEY_DIR}/${DEVSTACK_LBAAS_SSH_KEY_NAME}
    rm -f ${DEVSTACK_LBAAS_SSH_KEY}.pub ${DEVSTACK_LBAAS_SSH_KEY}
    ssh-keygen -b 2048 -t rsa -f ${DEVSTACK_LBAAS_SSH_KEY} -N ""
    nova keypair-add --pub_key=${DEVSTACK_LBAAS_SSH_KEY}.pub ${DEVSTACK_LBAAS_SSH_KEY_NAME}

    # Add tcp/22,80 and icmp to default security group
    nova secgroup-add-rule default tcp 22 22 0.0.0.0/0
    nova secgroup-add-rule default tcp 80 80 0.0.0.0/0
    nova secgroup-add-rule default icmp -1 -1 0.0.0.0/0

    # Boot some instances
    NOVA_BOOT_ARGS="--key-name ${DEVSTACK_LBAAS_SSH_KEY_NAME} --image $(nova image-list | awk '/ cirros-0.3.0-x86_64-disk / {print $2}') --flavor 1 --nic net-id=$(neutron net-list | awk '/ private / {print $2}')"

    nova boot ${NOVA_BOOT_ARGS} node1
    nova boot ${NOVA_BOOT_ARGS} node2

    echo "Waiting ${BOOT_DELAY} seconds for instances to boot"
    sleep ${BOOT_DELAY}

    IP1=$(nova show node1 | grep "private network" | awk '{print $5}')
    IP2=$(nova show node2 | grep "private network" | awk '{print $5}')

    ssh-keygen -R ${IP1}
    ssh-keygen -R ${IP2}

    # Run a simple web server on the instances
    scp -i ${DEVSTACK_LBAAS_SSH_KEY} -o StrictHostKeyChecking=no ${TOP_DIR}/webserver.sh cirros@${IP1}:webserver.sh
    scp -i ${DEVSTACK_LBAAS_SSH_KEY} -o StrictHostKeyChecking=no ${TOP_DIR}/webserver.sh cirros@${IP2}:webserver.sh

    screen_process node1 "ssh -i ${DEVSTACK_LBAAS_SSH_KEY} -o StrictHostKeyChecking=no cirros@${IP1} ./webserver.sh"
    screen_process node2 "ssh -i ${DEVSTACK_LBAAS_SSH_KEY} -o StrictHostKeyChecking=no cirros@${IP2} ./webserver.sh"

fi

if is_service_enabled q-lbaasv2; then

    neutron lbaas-loadbalancer-create --name lb1 private-subnet
    sleep 10
    neutron lbaas-listener-create --loadbalancer lb1 --protocol HTTP --protocol-port 80 --name listener1
    sleep 10
    neutron lbaas-pool-create --lb-algorithm ROUND_ROBIN --listener listener1 --protocol HTTP --name pool1
    neutron lbaas-member-create  --subnet private-subnet --address ${IP1} --protocol-port 80 pool1
    neutron lbaas-member-create  --subnet private-subnet --address ${IP2} --protocol-port 80 pool1

fi
