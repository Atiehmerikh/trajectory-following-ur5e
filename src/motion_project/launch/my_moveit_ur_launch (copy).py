#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # Path to UR package
    #ur_package_dir = get_package_share_directory('webots_ros2_universal_robot')

    # 👉 Include FULL original launch (this brings Webots + MoveIt + controllers)
    #ur_launch = IncludeLaunchDescription(
     #   PythonLaunchDescriptionSource(
    #        os.path.join(ur_package_dir, 'launch', 'universal_robot.launch.py')
     #   )
    #)

    moveit_controllers = {
    'moveit_controller_manager': 'moveit_simple_controller_manager/MoveItSimpleControllerManager',
    'moveit_simple_controller_manager': load_yaml('moveit_controllers.yaml')
	}
    
    # 👉 Your node (runs AFTER everything is up)
    my_node = Node(
        package='motion_project',
        executable='my_node',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        #ur_launch,
        my_node
    ])
