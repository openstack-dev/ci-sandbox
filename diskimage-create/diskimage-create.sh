#!/bin/bash
#
# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

set -e

usage() {
    echo
    echo "Usage: $(basename $0)"
    echo "            [-a i386 | **amd64** | armhf ]"
    echo "            [-b **haproxy** ]"
    echo "            [-c **~/.cache/image-create** | <cache directory> ]"
    echo "            [-h]"
    echo "            [-i **ubuntu** | fedora | centos ]"
    echo "            [-o **amphora-x64-haproxy** | <filename> ]"
    echo "            [-r <root password> ]"
    echo "            [-s **5** | <size in GB> ]"
    echo "            [-t **qcow2** | tar ]"
    echo "            [-v]"
    echo "            [-w <working directory> ]"
    echo
    echo "        '-a' is the architecture type for the image (default: amd64)"
    echo "        '-b' is the backend type (default: haproxy)"
    echo "        '-c' is the path to the cache directory (default: ~/.cache/image-create)"
    echo "        '-h' display this help message"
    echo "        '-i' is the base OS (default: ubuntu)"
    echo "        '-o' is the output image file name"
    echo "        '-r' enable the root account in the generated image (default: disabled)"
    echo "        '-s' is the image size to produce in gigabytes (default: 5)"
    echo "        '-t' is the image type (default: qcow2)"
    echo "        '-v' display the script version"
    echo "        '-w' working directory for image building (default: .)"
    echo
    exit 1
}

version() {
    echo "Amphora disk image creation script version:"\
        "`cat $OCTAVIA_REPO_PATH/diskimage-create/version.txt`"
    exit 1
}

# Figure out where our directory is located
if [ -z $OCTAVIA_REPO_PATH ]; then
    AMP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    OCTAVIA_REPO_PATH=${OCTAVIA_REPO_PATH:-${AMP_DIR%/*}}
fi

while getopts "a:b:c:hi:o:t:r:s:vw:" opt; do
    case $opt in
        a)
            AMP_ARCH=$OPTARG
            if [ $AMP_ARCH != "i386" ] && \
                [ $AMP_ARCH != "amd64" ] && \
                [ $AMP_ARCH != "armhf" ]; then
                echo "Error: Unsupported architecture " $AMP_ARCH " specified"
                exit 3
            fi
        ;;
        b)
            if [ $OPTARG == "haproxy" ]; then
                AMP_BACKEND=$OPTARG-octavia
            else
                echo "Error: Unsupported backend type " $AMP_BACKEND " specified"
                exit 3
            fi
        ;;
        c)
            AMP_CACHEDIR=$OPTARG
        ;;
        h)
            usage
        ;;
        i)
            AMP_BASEOS=$OPTARG
            if [ $AMP_BASEOS != "ubuntu" ] && \
                [ $AMP_BASEOS != "fedora" ] && \
                [ $AMP_BASEOS != "centos" ]; then
                echo "Error: Unsupported base OS " $AMP_BASEOS " specified"
                exit 3
            fi
        ;;
        o)
            AMP_OUTPUTFILENAME=$OPTARG
        ;;
        t)
            AMP_IMAGETYPE=$OPTARG
            if [ $AMP_IMAGETYPE != "qcow2" ] && \
                [ $AMP_IMAGETYPE != "tar" ]; then
                echo "Error: Unsupported image type " $AMP_IMAGETYPE " specified"
                exit 3
            fi
        ;;
        r)
            AMP_ROOTPW=$OPTARG
        ;;
        s)
            AMP_IMAGESIZE=$OPTARG
            if ! [[ $AMP_IMAGESIZE =~ ^[0-9]+$ ]]; then
                echo "Error: Invalid image size " $AMP_IMAGESIZE " specified"
                exit 3
            fi
        ;;
        v)
            version
        ;;
        w)
            AMP_WORKING_DIR=$OPTARG
        ;;
        *)
            usage
        ;;
    esac
done

shift $((OPTIND-1))
if [ "$1" ]; then
    usage
fi

# Set the Octavia Amphora defaults if they aren't already set
AMP_ARCH=${AMP_ARCH:-"amd64"}

AMP_BACKEND=${AMP_BACKEND:-"haproxy-octavia"}

AMP_CACHEDIR=${AMP_CACHEDIR:-"$HOME/.cache/image-create"}

AMP_BASEOS=${AMP_BASEOS:-"ubuntu"}

AMP_OUTPUTFILENAME=${AMP_OUTPUTFILENAME:-"$AMP_DIR/amphora-x64-haproxy"}

AMP_IMAGETYPE=${AMP_IMAGETYPE:-"qcow2"}

AMP_IMAGESIZE=${AMP_IMAGESIZE:-5}

OCTAVIA_ELEMENTS_PATH=$OCTAVIA_REPO_PATH/elements

if ! [ -d $OCTAVIA_ELEMENTS_PATH ]; then
    echo "ERROR: Octavia elements directory not found at: " $OCTAVIA_ELEMENTS_PATH " Exiting."
    exit 1
fi

DIB_REPO_PATH=${DIB_REPO_PATH:-${OCTAVIA_REPO_PATH%/*}/diskimage-builder}

if ! [ -d $DIB_REPO_PATH ]; then
    echo "ERROR: diskimage-builder repo directory not found at: " $DIB_REPO_PATH " Exiting."
    exit 1
fi

export PATH=$PATH:$DIB_REPO_PATH/bin

DIB_ELEMENTS_PATH=${DIB_REPO_PATH:-${OCTAVIA_REPO_PATH%/*}/diskimage-builder/elements}

if ! [ -d $DIB_ELEMENTS_PATH ]; then
    echo "ERROR: diskimage-builder elements directory not found at: " $DIB_ELEMENTS_PATH " Exiting."
    exit 1
fi

ELEMENTS_REPO_PATH=${ELEMENTS_REPO_PATH:-${OCTAVIA_REPO_PATH%/*}/tripleo-image-elements}

if ! [ -d $ELEMENTS_REPO_PATH ]; then
    echo "ERROR: tripleo-image-elements repo directory not found at: " $ELEMENTS_REPO_PATH " Exiting."
    exit 1
fi

TRIPLEO_ELEMENTS_PATH=${ELEMENTS_PATH:-$ELEMENTS_REPO_PATH/elements}

if ! [ -d $TRIPLEO_ELEMENTS_PATH ]; then
    echo "ERROR: tripleo-image-elements elements directory not found at: " $TRIPLEO_ELEMENTS_PATH " Exiting."
    exit 1
fi

if [ "$DIB_LOCAL_ELEMENTS_PATH" ]; then
    export ELEMENTS_PATH=$DIB_ELEMENTS_PATH:$TRIPLEO_ELEMENTS_PATH:$OCTAVIA_ELEMENTS_PATH:$DIB_LOCAL_ELEMENTS_PATH
else
    export ELEMENTS_PATH=$DIB_ELEMENTS_PATH:$TRIPLEO_ELEMENTS_PATH:$OCTAVIA_ELEMENTS_PATH
fi

export CLOUD_INIT_DATASOURCES=${CLOUD_INIT_DATASOURCES:-"ConfigDrive"}

# Find out what platform we are on
if [ -e /etc/os-release ]; then
    platform=$(head -1 /etc/os-release)
else
    platform=$(head -1 /etc/system-release | grep -e CentOS -e 'Red Hat Enterprise Linux' || :)
    if [ -z "$platform" ]; then
        echo -e "Unknown Host OS. Impossible to build images.\nAborting"
        exit 2
    fi
fi

if [ "$AMP_ROOTPW" ] && [ "$platform" != 'NAME="Ubuntu"' ]; then
    if [ "$(getenforce)" != "Disabled" ]; then
        echo "A root password cannot be enabled for images built on this platform while SELinux is enabled."
        exit 1
    fi
fi

if [ "$AMP_ROOTPW" ]; then
    echo "Warning: Using a root password in the image, NOT FOR PRODUCTION USAGE."
fi

# Make sure we have the required packages installed
if [ "$platform" = 'NAME="Ubuntu"' ]; then
    PKG_LIST="qemu kpartx git"
    for pkg in $PKG_LIST; do
        if ! dpkg --get-selections | grep -q "^$pkg[[:space:]]*install$" >/dev/null; then
            echo "Required package " $pkg " is not installed.  Exiting."
            exit 1
        fi
    done

    # Also check if we can build the BASEOS on this Ubuntu version
    UBUNTU_VERSION=`lsb_release -r | awk '{print $2}'`
    if [ "$AMP_BASEOS" != "ubuntu" ] && \
        [ 1 -eq $(echo "$UBUNTU_VERSION < 14.04" | bc) ]; then
            echo "Ubuntu minimum version 14.04 required to build $AMP_BASEOS."
            echo "Earlier versions don't support the extended attributes required."
            exit 1
    fi

elif [ "$platform" = 'NAME=Fedora' ]; then
    PKG_LIST="qemu kpartx git"
    for pkg in $PKG_LIST; do
        if ! yum list $pkg &> /dev/null; then
            echo "Required package " $pkg " is not installed.  Exiting."
            exit 1
        fi
    done
else
    # centos or rhel
        PKG_LIST="qemu-kvm qemu-img kpartx git"
        for pkg in $PKG_LIST; do
            if ! yum list $pkg &> /dev/null; then
                echo "Required package " $pkg " is not installed.  Exiting."
                exit 1
            fi
        done
        if [ ${platform:0:6} = "CentOS" ]; then
            # install EPEL repo, in order to install argparse
            PKG_LIST="python-argparse"
            if ! yum list $pkg &> /dev/null; then
                echo "CentOS requires the python-argparse package be "
                echo "installed separately from the EPEL repo."
                echo "Required package " $pkg " is not installed.  Exiting."
                exit 1
            fi
        fi
fi

# "pip freeze" does not show argparse, even if it is explictly installed,
# because it is part of of the standard python library in 2.7.
# See https://github.com/pypa/pip/issues/1570

PKG_LIST="Babel dib-utils PyYAML"
    for pkg in $PKG_LIST; do
        if ! pip freeze 2>/dev/null| grep -q "^$pkg==" &>/dev/null; then
            echo "Required python package " $pkg " is not installed.  Exiting."
            exit 1
        fi
    done

if  [ "$AMP_WORKING_DIR" ]; then
    mkdir -p $AMP_WORKING_DIR
    TEMP=$(mktemp -d $AMP_WORKING_DIR/diskimage-create.XXXXXX)
else
    TEMP=$(mktemp -d diskimage-create.XXXXXX)
fi
pushd $TEMP > /dev/null

# Setup some environment variables with the commit IDs used to build the image
pushd $DIB_REPO_PATH > /dev/null
export DIB_COMMIT_ID=`git rev-parse HEAD`
popd > /dev/null

pushd $ELEMENTS_REPO_PATH > /dev/null
export ELEMENTS_COMMIT_ID=`git rev-parse HEAD`
popd > /dev/null

pushd $OCTAVIA_REPO_PATH > /dev/null
export OCTAVIA_COMMIT_ID=`git rev-parse HEAD`
popd > /dev/null


# Setup the elements list

if [ "$AMP_BASEOS" = "ubuntu" ]; then
    AMP_element_sequence=${AMP_element_sequence:-"base vm ubuntu"}
    AMP_element_sequence="$AMP_element_sequence $AMP_BACKEND-ubuntu"
    if [ "$BASE_OS_MIRROR" ]; then
        AMP_element_sequence="$AMP_element_sequence apt-mirror"
        export UBUNTU_MIRROR="$BASE_OS_MIRROR"
    fi
elif [ "$AMP_BASEOS" = "fedora" ]; then
    AMP_element_sequence=${AMP_element_sequence:-"base vm fedora"}
    AMP_element_sequence="$AMP_element_sequence $AMP_BACKEND"
    if [ "$BASE_OS_MIRROR" ]; then
        AMP_element_sequence="$AMP_element_sequence fedora-mirror"
        export FEDORA_MIRROR="$BASE_OS_MIRROR"
    fi
elif [ "$AMP_BASEOS" = "centos" ]; then
    AMP_element_sequence=${AMP_element_sequence:-"base vm centos7"}
    AMP_element_sequence="$AMP_element_sequence $AMP_BACKEND"
    if [ "$BASE_OS_MIRROR" ]; then
        AMP_element_sequence="$AMP_element_sequence centos-mirror"
        export CENTOS_MIRROR="$BASE_OS_MIRROR"
    fi
fi

if [ "$AMP_ROOTPW" ]; then
    AMP_element_sequence="$AMP_element_sequence root-passwd"
    export DIB_PASSWORD=$AMP_ROOTPW
fi

# Add the Octavia Amphora agent element
AMP_element_sequence="$AMP_element_sequence amphora-agent"

# Allow full elements override
if [ "$DIB_ELEMENTS" ]; then
    AMP_element_sequence="$DIB_ELEMENTS"
fi

if [ "$DIB_LOCAL_ELEMENTS" ]; then
    AMP_element_sequence="$AMP_element_sequence $DIB_LOCAL_ELEMENTS"
fi

# Build the image

if [ "$AMP_BASEOS" = "ubuntu" ]; then
    export DIB_CLOUD_INIT_DATASOURCES=$CLOUD_INIT_DATASOURCES
fi

disk-image-create -a $AMP_ARCH -o $AMP_OUTPUTFILENAME -t $AMP_IMAGETYPE --image-size $AMP_IMAGESIZE --image-cache $AMP_CACHEDIR $AMP_element_sequence

popd > /dev/null # out of $TEMP
rm -rf $TEMP
