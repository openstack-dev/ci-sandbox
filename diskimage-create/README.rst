Diskimage-builder script for creating Octavia Amphora images
============================================================

Octavia is an operator-grade reference implementation for Load Balancing as a
Service (LBaaS) for OpenStack.  The component of Octavia that does the load
balancing is known as amphora.  Amphora may be a virtual machine, may be a
container, or may run on bare metal.  Creating images for bare metal amphora
installs is outside the scope of this version but may be added in a
future release.

Prerequisites
=============

This script assumes a typical Linux environment and was developed on
Ubuntu 12.04.5 LTS.

Python pip should be installed as well as the following python modules:

 | argparse
 | Babel>=1.3
 | dib-utils
 | PyYAML

Your cache directory should have at least 1GB available, the working directory
will need ~1.5GB, and your image destination will need ~500MB

The script expects to find the diskimage-builder and tripleo-image-elements
git repositories one directory above the Octavia git repository.

 | /<some directory>/octavia
 | /<some directory>/diskimage-builder
 | /<some directory>/tripleo-image-elements

 | cd /<some directory>
 | git clone https://github.com/stackforge/octavia.git
 | git clone https://git.openstack.org/openstack/diskimage-builder.git
 | git clone https://git.openstack.org/openstack/tripleo-image-elements.git

These paths can be overriden with the following environment variables:

 | OCTAVIA_REPO_PATH = /<some directory>/octavia
 | DIB_REPO_PATH = /<some directory>/diskimage-builder
 | DIB_ELEMENTS = /<some directory>/diskimage-builder/elements
 | ELEMENTS_REPO_PATH = /<some directory>/tripleo-image-elements
 | TRIPLEO_ELEMENTS_PATH = /<some directory>/tripleo-image-elements/elements

The following packages are required on each platform:
Ubuntu and Fedora: qemu kpartx git
CentOS and RedHat Enterprise Linux: qemu-kvm qemu-img kpartx git
CentOS requires the EPEL repo and python-argparse:

.. code:: bash

    $ sudo rpm -Uvh --force http://mirrors.kernel.org/fedora-epel/6/i386/epel-release-6-8.noarch.rpm
    $ yum install python-argparse

Test Prerequisites
------------------
The tox image tests require libguestfs-tools 1.24 or newer.
Libguestfs allows testing the Amphora image without requiring root privledges.
On Ubuntu systems you also need to give read access to the kernels for the user
running the tests:

.. code:: bash

    $ sudo chmod 0644 /boot/vmlinuz*

Tests were run on Ubuntu 14.04.1 LTS during development.

Usage
=====
This script and associated elements will build Amphora images.  Current support
is with an Ubuntu base OS and HAProxy.  The script can use Fedora
or CentOS as a base OS but these will not initially be tested or supported.
As the project progresses and/or the diskimage-builder project adds support
for additional base OS options they may become available for Amphora images.
This does not mean that they are necessarily supported or tested.

The script will use environment variables to customize the build beyond the
Octavia project defaults, such as adding elements.

The supported and tested image is created by using the diskimage-create.sh
defaults (no command line parameters or environment variables set).  As the
project progresses we may add additional supported configurations.

Command syntax:


.. line-block::

    $ diskimage-create.sh
            [-a i386 | **amd64** | armhf ]
            [-b **haproxy** ]
            [-c **~/.cache/image-create** | <cache directory> ]
            [-h]
            [-i **ubuntu** | fedora | centos ]
            [-o **amphora-x64-haproxy** | <filename> ]
            [-r <root password> ]
            [-s **5** | <size in GB> ]
            [-t **qcow2** | tar ]
            [-v]
            [-w <working directory> ]

        '-a' is the architecture type for the image (default: amd64)
        '-b' is the backend type (default: haproxy)
        '-c' is the path to the cache directory (default: ~/.cache/image-create)
        '-h' display help message
        '-i' is the base OS (default: ubuntu)
        '-o' is the output image file name
        '-r' enable the root account in the generated image (default: disabled)
        '-s' is the image size to produce in gigabytes (default: 5)
        '-t' is the image type (default: qcow2)
        '-v' display the script version
        '-w' working directory for image building (default: .)


Environment Variables
=====================
These are optional environment variables that can be set to override the script
defaults.

CLOUD_INIT_DATASOURCES
    - Comma seperated list of cloud-int datasources
    - Default: ConfigDrive
    - Options: NoCloud, ConfigDrive, OVF, MAAS, Ec2, <others>
    - Reference: https://launchpad.net/cloud-init

BASE_OS_MIRROR
    - URL to a mirror for the base OS selected
    - Default: None

DIB_ELEMENTS
    - Override the elements used to build the image
    - Default: None

DIB_LOCAL_ELEMENTS
    - Elements to add to the build (requires DIB_LOCAL_ELEMENTS_PATH be
      specified)
    - Default: None

DIB_LOCAL_ELEMENTS_PATH
    - Path to the local elements directory
    - Default: None

DIB_REPO_PATH
    - Directory containing diskimage-builder
    - Default: <directory above OCTAVIA_HOME>/diskimage-builder
    - Reference: https://github.com/openstack/diskimage-builder

ELEMENTS_PATH
    - Directory that contains the default elements
    - Default: <ELEMENTS_REPO_PATH>/elements
    - Reference: https://github.com/openstack/tripleo-image-elements

ELEMENTS_REPO_PATH
    - Directory containing tripleo-image-elements
    - Default: <directory above OCTAVIA_HOME>/tripleo-image-elements
    - Reference: https://github.com/openstack/tripleo-image-elements

OCTAVIA_REPO_PATH
    - Directory containing octavia
    - <directory above the script location>
    - Reference: https://github.com/stackforge/octavia

Container Support
=================
The Docker command line required to import a tar file created with this script
is:

.. code:: bash

    $ docker import - image:amphora-x64-haproxy < amphora-x64-haproxy.tar


References
==========

This documentation and script(s) leverage prior work by the OpenStack TripleO
and Sahara teams.  Thank you to everyone that worked on them for providing a
great foundation for creating Octavia Amphora images.

    | https://github.com/openstack/diskimage-builder
    | https://github.com/openstack/diskimage-builder/blob/master/docs/docker.md
    | https://github.com/openstack/tripleo-image-elements
    | https://github.com/openstack/sahara-image-elements

Copyright
=========

Copyright 2014 Hewlett-Packard Development Company, L.P.

All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

   | http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

