#!/usr/bin/env bash

# This script shows how to build the Docker image

sagify_module_path=$1
dockerfile_path=$2
requirements_file_path=$3

image={{ cookiecutter.project_slug }}-img

img_id=$(docker images ${image} -q)
if [ "$img_id" != "" ]
then
    docker rmi -f ${img_id}
fi

# Build the docker image

docker build -t ${image} -f ${dockerfile_path} . --build-arg sagify_module_path=${sagify_module_path} --build-arg requirements_file_path=${requirements_file_path}
