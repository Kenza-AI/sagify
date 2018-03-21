#!/bin/sh

image={{ cookiecutter.project_slug }}-img
test_path=$1
input_data_path=$2
hyperparam_file_path=$3
model_save_path=$4
failure_path=$5

docker run -v ${test_path}:/opt/ml --rm ${image} training/train --input-data-dir ${input_data_path} --model-save-dir ${model_save_path}  --hyperparams-json-file ${hyperparam_file_path} --failure-dir ${failure_path}
