#!/bin/sh

image={{ cookiecutter.project_slug }}-img
test_path=$1
tag=$2

docker run -v ${test_path}:/opt/ml --rm "${image}:${tag}" train
