#!/bin/bash
cd infinigen

python -m infinigen.datagen.manage_jobs \
    --output_folder outputs/coral_2 \
    --num_scenes 9 \
    --configs circular_coral_9 simple coral_reef \
    --pipeline_configs local_16GB monocular_video blender_gt cuda_terrain \
    --overrides camera.spawn_and_animate_cameras.n_cameras=9 fine_terrain.mesher_backend="OcMesher" compose_nature.fish_school_chance=0.0 \
    --pipeline_overrides iterate_scene_tasks.n_camera_rigs=9 \
    --warmup_sec 12000 \
    --cleanup big_files \
    --overwrite 

# python -m infinigen.datagen.manage_jobs \
#     --output_folder outputs/coral_2 \
#     --num_scenes 1 \
#     --configs circular_coral_9 simple coral_reef \
#     --pipeline_configs local_64GB monocular_video blender_gt cuda_terrain \
#     --overrides camera.spawn_and_animate_cameras.n_cameras=9 fine_terrain.mesher_backend="OcMesher" \
#     --pipeline_overrides iterate_scene_tasks.n_camera_rigs=9 \
#     --overwrite

# python -m infinigen.datagen.manage_jobs --output_folder outputs/hello_world_0 --num_scenes 1 --specific_seed 0 \
# --configs desert.gin simple.gin --pipeline_configs local_16GB.gin monocular.gin blender_gt.gin
