#!/bin/bash

USER_NAME=$1

if [ $# -ne 1 ]
then
   echo "Warning: Currently using user name $USER as none was supplied"
   echo "Usage : ./build_all_containers_clean.sh DOCKER_USER_NAME: $1 needs to be the docker user name if user name other than current user name $USER is desired"
   #exit -1
   USER_NAME=$USER
fi

docker rm streamdeck
docker rmi streamdeck
docker image prune -f

DOCKER_USER=$USER_NAME ./build_streamdeck.sh
