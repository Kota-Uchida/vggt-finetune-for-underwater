#!/bin/bash

python preprocess_infinigen.py \
    --infinigen_data_dir infinigen/outputs/coral_5 \
    --data_output_dir data \
    --annotation_output_dir annotations \
    --category coral_5 \
    --train_split 0.8 \
    --seed 42
