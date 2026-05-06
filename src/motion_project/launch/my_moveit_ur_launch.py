#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg = get_package_share_directory('webots_ros2_universal_robot')

    # -------- STEP 1: WEBOTS WORLD --------
    webots = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'robot_world_launch.py')
        )
    )

    # -------- STEP 2: ROBOT + MOVEIT (DELAYED) --------
    moveit = TimerAction(
        period=5.0,   # wait for Webots to start
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg, 'launch', 'robot_moveit_nodes_launch.py')
                )
            )
        ]
    )

    # -------- STEP 3: YOUR NODE (MORE DELAY) --------
    my_node = TimerAction(
        period=12.0,  # wait for controllers + MoveIt
        actions=[
            Node(
                package='motion_project',
                executable='my_node',
                output='screen',
                parameters=[{'use_sim_time': True}]
            )
        ]
    )

    return LaunchDescription([
        webots,
        moveit,
        my_node
    ])
