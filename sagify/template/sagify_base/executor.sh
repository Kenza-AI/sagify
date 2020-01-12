#!/usr/bin/env bash

if [ $1 = "train" ]; then
    python ./sagify_base/training/train
else
    python ./sagify_base/prediction/serve
fi