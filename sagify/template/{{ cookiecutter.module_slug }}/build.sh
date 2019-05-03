#!/usr/bin/env bash

# Build the docker image

module_path=$1
target_dir_name=$2
dockerfile_path=$3
requirements_file_path=$4
tag=$5
image=$6
python_version=$7

docker build \
-t "${image}:${tag}" \
-f ${dockerfile_path} . \
--build-arg module_path=${module_path} \
--build-arg target_dir_name=${target_dir_name} \
--build-arg requirements_file_path=${requirements_file_path} \
--build-arg python_version=${python_version}
