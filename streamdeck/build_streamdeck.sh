#!/bin/bash

if [[ -z "${DOCKER_USER}" ]]; then
    echo "Please set DOCKER_USER environment variable!"
    exit -1
fi

TMPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd
homedir=$(pwd)
cd $TMPDIR

LOCAL_UID=$(id -u $USER)
LOCAL_GID=$(id -g $USER)

cd $TMPDIR

docker build \
    -t streamdeck \
    -f $TMPDIR/streamdeck_dockerfile \
    --no-cache \
    --build-arg USER=$DOCKER_USER \
    --build-arg UID=$LOCAL_UID \
    --build-arg GID=$LOCAL_GID \
    --build-arg TZ=$(cat /etc/timezone) \
    $TMPDIR
