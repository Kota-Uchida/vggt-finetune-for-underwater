import os
import random

def reduce_files_to_num(dir_path, seed=None, target_num=100):
    if seed is not None:
        random.seed(seed)

    files = [
        f for f in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, f))
    ]

    if len(files) <= target_num:
        print(f"Directory already has {len(files)} files (≤ {target_num}). No action taken.")
        return

    keep = set(random.sample(files, target_num))
    for f in files:
        if f not in keep:
            os.remove(os.path.join(dir_path, f))

    print(f"Reduced files from {len(files)} to {target_num}.")

# Example usage
reduce_files_to_num("/home/kota/data/garden_vggt/images", seed=42, target_num=50)
