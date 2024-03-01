#!/bin/bash

if [[ -z "${DOCKER_USER}" ]]; then
   echo "Warning: Currently using user name $USER as none was supplied"
   echo "Usage :DOCKER_USER=NAME ./build_all_containers_clean.sh: If user name other than current user name $USER is desired then NAME must be set"
   echo "Please set DOCKER_USER environment variable!"
   #exit -1
   DOCKER_USER=$USER
fi

TMPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd
homedir=$(pwd)
cd $TMPDIR

docker rm -f streamdeck

docker run \
    --name streamdeck \
    --rm \
    -it \
    --user $DOCKER_USER \
    --privileged \
    -v /dev/bus/usb:/dev/bus/usb \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $TMPDIR/files:/home/$DOCKER_USER/files \
    streamdeck \
    bash
