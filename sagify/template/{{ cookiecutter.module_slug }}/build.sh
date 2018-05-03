#!/usr/bin/env bash

# This script shows how to build the Docker image

module_path=$1
target_dir_name=$2
dockerfile_path=$3
requirements_file_path=$4

image={{ cookiecutter.project_slug }}-img

img_id=$(docker images ${image} -q)
if [ "$img_id" != "" ]
then
    docker rmi -f ${img_id}
fi

# Build the docker image

docker build -t ${image} -f ${dockerfile_path} . --build-arg module_path=${module_path} --build-arg target_dir_name=${target_dir_name} --build-arg requirements_file_path=${requirements_file_path}
