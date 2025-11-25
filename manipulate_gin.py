import os
import shutil
import numpy as np
import math
import argparse


def generate_circular_camera_config(radius, num_cameras, center=(0,0,0), offset_height=0, look_at_center=True):
    """
    Generate camera configurations positioned around a circle in the x-y plane.
    
    Args:
        radius: Radius of the circle
        num_cameras: Number of cameras to place around the circle
        center: Center point of the coordinate on which the configs are calculated
        offset_height: Height offset (z-coordinate) for all cameras
        look_at_center: If True, cameras will look toward the center of the circle
        
    Returns:
        List of camera configuration dictionaries with 'loc' and 'rot_euler' keys
    """
    assert num_cameras > 0, "Number of cameras must be positive"
    assert num_cameras < 10, "Number of cameras must be less than 10 to avoid overlap"
    camera_configs = []
    
    for i in range(num_cameras):
        # Calculate angle for this camera
        angle = (2 * math.pi * i) / num_cameras
        
        # Calculate position on the circle
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = offset_height
        
        # Calculate rotation to look at center
        if look_at_center:
            # Camera should look toward the center (0, 0, offset_height)
            # The rotation around z-axis to point toward center
            rot_z = angle + math.pi / 2  # Add 90 degrees to point inward
            rot_euler = (math.pi / 2, 0, rot_z)  # Pitch down to look at center
        else:
            rot_euler = (0, 0, 0)
        
        camera_configs.append({
            'loc': (x + center[0], y + center[1], z + center[2]),
            'rot_euler': rot_euler
        })
    
    return camera_configs


def format_camera_config_for_gin(camera_configs):
    """
    Format camera configurations as a string suitable for Gin config.
    
    Args:
        camera_configs: List of camera configuration dictionaries
        
    Returns:
        String formatted for Gin configuration
    """
    config_str = "camera.spawn_camera_rigs.camera_rig_config = [\n"
    for config in camera_configs:
        loc = config['loc']
        rot = config['rot_euler']
        config_str += f"    {{'loc': ({loc[0]:.3f}, {loc[1]:.3f}, {loc[2]:.3f}), "
        config_str += f"'rot_euler': ({rot[0]:.3f}, {rot[1]:.3f}, {rot[2]:.3f})}},\n"
    config_str += "]\n"
    return config_str


def generate_monocular_gin_config_given_number(n_camera_rigs, center=(0,0,0), radius=5.0, offset_height=1.5):
    base_config_dir = "infinigen/infinigen_examples/configs_nature"
    output_name = f"monocular_{n_camera_rigs}_rigs.gin"
    output_path = os.path.join(base_config_dir, output_name)
    
    camera_configs = generate_circular_camera_config(
        radius=radius,
        num_cameras=n_camera_rigs,
        offset_height=center[2] + offset_height,
        look_at_center=True
    )
    
    # Format the camera configurations for Gin
    gin_config_content = format_camera_config_for_gin(camera_configs)
    
    # Ensure the output directory exists
    os.makedirs(base_config_dir, exist_ok=True)
    
    # Write the configuration to the output file
    with open(output_path, 'w') as f:
        f.write(gin_config_content)
    
    print(f"Generated camera configuration with {n_camera_rigs} rigs at {output_path}")
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate camera configurations arranged in a circle')
    parser.add_argument('--n_camera_rigs', type=int, required=True, help='Number of camera rigs')
    parser.add_argument('--center', type=float, nargs=3, required=True, help='Center point as x y z')
    parser.add_argument('--radius', type=float, required=True, help='Radius of the circle')
    parser.add_argument('--offset_height', type=float, required=True, help='Height offset from center z')
    
    args = parser.parse_args()
    
    generate_monocular_gin_config_given_number(
        n_camera_rigs=args.n_camera_rigs,
        center=tuple(args.center),
        radius=args.radius,
        offset_height=args.offset_height
    )