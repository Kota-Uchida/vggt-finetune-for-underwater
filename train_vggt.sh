#!/bin/bash

cd vggt

pip install -e .

# Before running this script, check configurations in vggt/training/config/default.yaml

torchrun --nproc_per_node=2 training/launch.py