#!/bin/bash

python preprocess_infinigen.py \
    --infinigen_data_dir infinigen/outputs/coral_1 infinigen/outputs/coral_2 infinigen/outputs/coral_8 \
    --data_output_dir data \
    --annotation_output_dir annotations \
    --category coral \
    --train_split 0.8 \
    --seed 42
