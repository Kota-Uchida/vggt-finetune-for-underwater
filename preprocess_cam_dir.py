import os
import shutil
import re

################
# Configurable Parameters
################
infinigen_output_dir = 'infinigen/outputs/'
target_dir_list = ['coral_5']

def preprocess_cam_dir(infinigen_output_dir, target_dir_list):
    for target_dir in target_dir_list:
        source_dir = os.path.join(infinigen_output_dir, target_dir)
        if not os.path.isdir(source_dir):
            continue
        scene_dir_list = sorted(
            [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
        )
        frame_dir_list = [
            os.path.join(source_dir, scene_dir, 'frames')
            for scene_dir in scene_dir_list
        ]
        
        for frame_dir in frame_dir_list:
            if not os.path.isdir(frame_dir):
                continue
            for data_dir in os.listdir(frame_dir):
                data_path = os.path.join(frame_dir, data_dir)
                if not os.path.isdir(data_path):
                    continue
                
                # Fetch all files recursively
                # Collect files without using os.walk:
                # - files directly under data_path
                # - files one level down inside immediate subdirectories
                candidates = []  # list of (root_dir, filename)
                try:
                    for entry in os.listdir(data_path):
                        entry_path = os.path.join(data_path, entry)
                        if os.path.isfile(entry_path):
                            candidates.append((data_path, entry))
                        elif os.path.isdir(entry_path):
                            # gather files inside this subdirectory (non-recursive)
                            for sub in os.listdir(entry_path):
                                sub_path = os.path.join(entry_path, sub)
                                if os.path.isfile(sub_path):
                                    candidates.append((entry_path, sub))
                except Exception:
                    # silently skip directories we cannot list
                    continue

                # Filename convention (example): (data)_(cam_id)_0_(frameid4)_0.<ext>
                # Use regex to extract cam_id robustly.
                pattern = re.compile(r'^[^_]+_(?P<cam_id>[^_]+)_0_\d{4}_0\..+$')
                for root, file in candidates:
                    m = pattern.match(file)
                    if not m:
                        # skip files that do not match expected pattern
                        continue
                    cam_id = m.group('cam_id')
                    dst_dir = os.path.join(data_path, f"camera_{cam_id}")
                    os.makedirs(dst_dir, exist_ok=True)
                    src = os.path.join(root, file)
                    dst = os.path.join(dst_dir, file)
                    try:
                        shutil.move(src, dst)
                    except Exception:
                        # silently ignore move failures and continue
                        continue

if __name__ == "__main__":
    preprocess_cam_dir(infinigen_output_dir, target_dir_list)


