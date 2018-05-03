#!/usr/bin/env bash

if [ $1 = "train" ]; then
    python ./sagify/training/train
else
    python ./sagify/prediction/serve
fi