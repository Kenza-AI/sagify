#!/bin/sh

test_path=$1
tag=$2
image=$3

docker run -it -v ${test_path}:/opt/ml -p 8080:8080 --rm "${image}:${tag}" serve
