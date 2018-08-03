#!/usr/bin/env bash

# This script shows how to build the Docker image

module_path=$1
target_dir_name=$2
dockerfile_path=$3
requirements_file_path=$4
tag=$5

image={{ cookiecutter.project_slug }}-img

# Build the docker image

docker build -t "${image}:${tag}" -f ${dockerfile_path} . --build-arg module_path=${module_path} --build-arg target_dir_name=${target_dir_name} --build-arg requirements_file_path=${requirements_file_path}
