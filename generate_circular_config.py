import os
import shutil
import numpy as np
from typing import Tuple

"""
Parameters for coral reef
"""
# n_of_cams = 9
# z_focus_bound = (-18.0, -17.0)
# x_center_bound = (-10.0, 10.0)
# y_center_bound = (-10.0, 10.0)
# z_center_bound = (-16.5, -15.5)
# radius_bound = (3.0, 7.0)
# angular_velocity_bound = (0.08, 0.15)
# base_config_dir = "infinigen/infinigen_examples/configs_nature"
# output_name = "circular_coral_9.gin"

"""
Paramters for desert
"""
n_of_cams = 9
z_focus_bound = (5.0, 5.5)
x_center_bound = (-2.0, 2.0)
y_center_bound = (-2.0, 2.0)
z_center_bound = (6.0, 6.5)
radius_bound = (3.0, 5.0)
angular_velocity_bound = (0.08, 0.15)
base_config_dir = "infinigen/infinigen_examples/configs_nature"
output_name = "circular_desert_9.gin"



def generate_config(
        n_of_cams: int,
        z_focus_bound: Tuple[float, float],
        x_center_bound: Tuple[float, float],
        y_center_bound: Tuple[float, float],
        z_center_bound: Tuple[float, float],
        radius_bound: Tuple[float, float],
        angular_velocity_bound: Tuple[float, float]
):
    """
    Generate a circular camera configuration and format it for Gin.
    Args:
        n_of_cams: Number of cameras to generate
        z_focus_bound: Tuple defining the z-axis bounds for focus point
        x_center_bound: Tuple defining the x-axis bounds for center point
        y_center_bound: Tuple defining the y-axis bounds for center point
        z_center_bound: Tuple defining the z-axis bounds for center point
        radius_bound: Tuple defining the radius bounds for camera trajectory
        angular_velocity_bound: Tuple defining the angular velocity bounds for camera trajectory
    Return:
        A string formatted for Gin configuration
    """
    def random_in_bounds(bounds):
        return np.random.uniform(bounds[0], bounds[1])
    
    camera_configs = []

    for i in range(n_of_cams):
        # First, randomly sample center points and radius
        center_points = (
            random_in_bounds(x_center_bound),
            random_in_bounds(y_center_bound),
            random_in_bounds(z_center_bound)
        )
        radius = random_in_bounds(radius_bound)

        # The focus point should be within 60 percent the radius from center point.
        max_xy_focus_distance = 0.6 * radius
        # Define the focus point bound from this condition
        x_focus_bound = (
            center_points[0] - max_xy_focus_distance,
            center_points[0] + max_xy_focus_distance
        )
        y_focus_bound = (
            center_points[1] - max_xy_focus_distance,
            center_points[1] + max_xy_focus_distance
        )
        # Sample focus points
        focus_points = (
            random_in_bounds(x_focus_bound),
            random_in_bounds(y_focus_bound),
            random_in_bounds(z_focus_bound)
        )

        # Sample angular velocity
        angular_velocity = random_in_bounds(angular_velocity_bound)

        # Store it to a dict
        cam_config = {
            'focus': focus_points,
            'center': center_points,
            'radius': radius,
            'angular_velocity': angular_velocity
        }

        camera_configs.append(cam_config)
    
    def format_configs_for_gin(configs):
        config_str = "camera.spawn_and_animate_cameras.cam_configs = [\n"
        for cfg in configs:
            focus = cfg['focus']
            center = cfg['center']
            radius = cfg['radius']
            angular_velocity = cfg['angular_velocity']
            config_str += f"    {{'focus': ({focus[0]:.3f}, {focus[1]:.3f}, {focus[2]:.3f}), "
            config_str += f"'center': ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f}), "
            config_str += f"'radius': {radius:.3f}, 'angular_velocity': {angular_velocity:.3f}}},\n"
        config_str += "]\n"
        return config_str
    
    gin_formatted_str = format_configs_for_gin(camera_configs)
    return gin_formatted_str


if __name__ == '__main__':
    gin_config_str = generate_config(
        n_of_cams=n_of_cams,
        z_focus_bound=z_focus_bound,
        x_center_bound=x_center_bound,
        y_center_bound=y_center_bound,
        z_center_bound=z_center_bound,
        radius_bound=radius_bound,
        angular_velocity_bound=angular_velocity_bound
    )
    
    output_path = os.path.join(base_config_dir, output_name)
    with open(output_path, 'w') as f:
        f.write(gin_config_str)

    print(f"Generated configuration saved to {output_path}")
    print(f"Configuration conditions: n_of_cams={n_of_cams}, z_focus_bound={z_focus_bound}, x_center_bound={x_center_bound}, y_center_bound={y_center_bound}, z_center_bound={z_center_bound}, radius_bound={radius_bound}, angular_velocity_bound={angular_velocity_bound}")


