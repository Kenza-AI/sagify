#!/bin/sh

image={{ cookiecutter.project_slug }}-img
test_path=$1

docker run -v ${test_path}:/opt/ml -p 8080:8080 --rm ${image} prediction/serve
