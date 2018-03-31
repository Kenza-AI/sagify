#!/usr/bin/env bash

if [ $1 = "train" ]; then
    python ./training/train
else
    python ./prediction/serve
fi