############################
# 23 Nov 2025, Kota Uchida
# Convert Infinigen data to CO3D format to be used with VGGT trainer.
############################

import argparse
import gzip
import json
import os
import random
import shutil

import cv2
import numpy as np


def get_parser():
    parser = argparse.ArgumentParser(
        description="Convert Infinigen data to CO3D format."
    )

    parser.add_argument(
        "--infinigen_data_dir",
        type=str,
        nargs="+",
        required=True,
        help="Path(s) to the Infinigen data output directory. You can pass multiple paths separated by space.",
    )
    parser.add_argument(
        "--data_output_dir",
        type=str,
        default="data/default",
        help="Directory where preprocessed data will be saved.",
    )
    parser.add_argument(
        "--annotation_output_dir",
        type=str,
        default="data/annotations",
        help="Directory where annotation files will be saved.",
    )
    parser.add_argument(
        "--category",
        type=str,
        default="default",
        help="Category name to process. This will be used as the output folder name.",
    )
    parser.add_argument(
        "--train_split",
        type=float,
        default=0.8,
        help="Train split ratio (between 0 and 1).",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducible splits."
    )

    return parser


def infinigen_to_co3dformat(args):
    os.makedirs(os.path.join(args.data_output_dir, args.category), exist_ok=True)
    os.makedirs(os.path.join(args.annotation_output_dir, args.category), exist_ok=True)

    path_to_annotation_category = os.path.join(
        args.annotation_output_dir, args.category
    )

    annotation_train_path_jgz = os.path.join(
        path_to_annotation_category, f"{args.category}_train.jgz"
    )
    annotation_test_path_jgz = os.path.join(
        path_to_annotation_category, f"{args.category}_test.jgz"
    )
    annotation_train_path_json = os.path.join(
        path_to_annotation_category, f"{args.category}_train.json"
    )
    annotation_test_path_json = os.path.join(
        path_to_annotation_category, f"{args.category}_test.json"
    )

    annotations_train = {}
    annotations_test = {}

    # Treat multiple input directories and multiple cameras
    all_scenes_camera_pairs = []
    for data_dir in args.infinigen_data_dir:
        scenes = [
            d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))
        ]
        for scene in scenes:
            frames_dir = os.path.join(data_dir, scene, "frames")
            img_dir = os.path.join(frames_dir, "Image")
            if not os.path.exists(img_dir):
                print(f"Skipping scene {scene} due to missing Image directory.")
                print(img_dir)
                continue
            camera_dirs = [
                c
                for c in os.listdir(img_dir)
                if os.path.isdir(os.path.join(img_dir, c)) and c.startswith("camera_")
            ]
            for camera in camera_dirs:
                all_scenes_camera_pairs.append((data_dir, scene, camera))

    # Shuffle and split scenes into train/test
    random.seed(args.seed)
    random.shuffle(all_scenes_camera_pairs)

    num_train = int(len(all_scenes_camera_pairs) * args.train_split)
    train_cases = set(all_scenes_camera_pairs[:num_train])
    test_cases = set(all_scenes_camera_pairs[num_train:])

    for data_dir, scene, camera in all_scenes_camera_pairs:
        scene_key = f"{scene}_{camera}"  # e.g., "1a0bdba9_camera_0"
        scene_entries = []
        rgb_dir = os.path.join(data_dir, scene, "frames", "Image", camera)
        depth_dir = os.path.join(data_dir, scene, "frames", "Depth", camera)
        camera_dir = os.path.join(data_dir, scene, "frames", "camview", camera)
        segment_dir = os.path.join(
            data_dir, scene, "frames", "ObjectSegmentation", camera
        )
        rgb_destination = os.path.join(
            args.data_output_dir, args.category, scene_key, "images"
        )
        depth_destination = os.path.join(
            args.data_output_dir, args.category, scene_key, "depths"
        )
        mask_destination = os.path.join(
            args.data_output_dir, args.category, scene_key, "masks"
        )
        depthmask_destination = os.path.join(
            args.data_output_dir, args.category, scene_key, "depth_masks"
        )

        if (
            not os.path.exists(rgb_dir)
            or not os.path.exists(depth_dir)
            or not os.path.exists(camera_dir)
            or not os.path.exists(segment_dir)
        ):
            print(f"Skipping scene {scene} due to missing directories.")
            print("rgb_dir: ", rgb_dir)
            print("depth_dir: ", depth_dir)
            print("camera_dir: ", camera_dir)
            continue

        rgb_files = sorted([f for f in os.listdir(rgb_dir) if f.endswith(".png")])
        depth_files = sorted([f for f in os.listdir(depth_dir) if f.endswith(".npy")])
        camera_npz_files = sorted(
            [f for f in os.listdir(camera_dir) if f.endswith(".npz")]
        )
        segment_files = sorted(
            [f for f in os.listdir(segment_dir) if f.endswith(".npy")]
        )

        if (
            len(rgb_files) != len(depth_files)
            or len(rgb_files) != len(camera_npz_files)
            or len(rgb_files) != len(segment_files)
        ):
            # In some cases, you need to discard first 5 scenes of rgb and camera files to match depth files..., but why?
            rgb_files = rgb_files[5:]
            camera_npz_files = camera_npz_files[5:]
            if len(rgb_files) != len(depth_files) or len(rgb_files) != len(
                camera_npz_files
            ):
                print(f"Skipping scene {scene} due to mismatched number of files.")
                print(
                    f"RGB files: {len(rgb_files)+5}, Depth files: {len(depth_files)}, Camera files: {len(camera_npz_files)+5}, Segment files: {len(segment_files)}"
                )
                continue

        os.makedirs(rgb_destination, exist_ok=True)
        os.makedirs(depth_destination, exist_ok=True)
        os.makedirs(mask_destination, exist_ok=True)
        os.makedirs(depthmask_destination, exist_ok=True)

        for i in range(len(rgb_files)):
            # Rename/move RGB
            rgb_src = os.path.join(rgb_dir, rgb_files[i])
            segment_src = os.path.join(segment_dir, segment_files[i])
            rgb_dst_name = f"rgb_{i:06d}.png"
            rgbmask_name = f"rgb_{i:06d}_mask.png"
            rgb_dst = os.path.join(rgb_destination, rgb_dst_name)
            rgbmask_dst = os.path.join(mask_destination, rgbmask_name)
            shutil.copy2(rgb_src, rgb_dst)
            generate_mask(segment_src, rgbmask_dst)

            # Rename/move Depth and Depth masks
            depth_src = os.path.join(depth_dir, depth_files[i])
            # For some reason, vggt trainer expects depth files to be named like this;
            depth_dst_name = f"rgb_{i:06d}.png.geometric.png"
            depthmask_dst_name = f"rgb_{i:06d}.png"
            depth_dst = os.path.join(depth_destination, depth_dst_name)
            depthmask_dst = os.path.join(depthmask_destination, depthmask_dst_name)
            convert_depth_npy_to_geometric_png(depth_src, depth_dst, depthmask_dst)

            # Load Camera
            npz_path = os.path.join(camera_dir, camera_npz_files[i])
            with np.load(npz_path) as data:
                K = data["K"].tolist()
                T = data["T"].tolist()

            rel_filepath = os.path.join(
                args.category, scene_key, "images", rgb_dst_name
            )

            entry = {"filepath": rel_filepath, "intri": K, "extri": T[:3]}

            scene_entries.append(entry)

        if (data_dir, scene, camera) in train_cases:
            annotations_train[scene_key] = scene_entries
        else:
            annotations_test[scene_key] = scene_entries

    # Save training/testing annotations (both .jgz and .json formats)
    with gzip.open(annotation_train_path_jgz, "wt", encoding="utf-8") as f:
        json.dump(annotations_train, f)
    with open(annotation_train_path_json, "w", encoding="utf-8") as f:
        json.dump(annotations_train, f, indent=2)

    with gzip.open(annotation_test_path_jgz, "wt", encoding="utf-8") as f:
        json.dump(annotations_test, f)
    with open(annotation_test_path_json, "w", encoding="utf-8") as f:
        json.dump(annotations_test, f, indent=2)


def generate_mask(segment_path, mask_path, object_id=None):
    # TODO: Make accurate mask to enhance the quality
    segment = np.load(segment_path)  # Load the segmentation data
    segment = np.nan_to_num(segment)  # Replace NaNs with 0, or adjust accordingly

    if object_id is None:
        mask = (segment > 0).astype(np.uint8) * 255
    else:
        mask = (segment == object_id).astype(np.uint8) * 255
    cv2.imwrite(mask_path, mask)


def convert_depth_npy_to_geometric_png(
    npy_path, png_path, depthmask_path, min_depth=0.1, max_depth=100.0
):
    # Load depth map from .npy file and convert to 16-bit PNG
    depth = np.load(npy_path)

    # Normalize depth to 16-bit range if needed
    if depth.dtype != np.uint16:
        depth_min = depth.min()
        depth_max = depth.max()
        if depth_max - depth_min > 0:
            depth_normalized = (depth - depth_min) / (depth_max - depth_min)
        else:
            depth_normalized = np.zeros_like(depth)
        depth_16bit = (depth_normalized * 65535).astype(np.uint16)
    else:
        depth_16bit = depth

    cv2.imwrite(png_path, depth_16bit)

    # Generate depth mask based on the threshold (valid depth range)
    depth_mask = np.logical_and(depth >= min_depth, depth <= max_depth).astype(np.uint8)
    depth_mask[depth == 0] = 0  # Mask out regions with 0 depth (e.g., background)
    depth_mask[np.isnan(depth)] = 0  # Mask out NaN regions if any

    cv2.imwrite(depthmask_path, depth_mask * 255)


if __name__ == "__main__":
    args = get_parser().parse_args()
    for data_dir in args.infinigen_data_dir:
        if not os.path.exists(data_dir):
            raise ValueError(f"Infinigen data directory {data_dir} does not exist.")

    infinigen_to_co3dformat(args)
