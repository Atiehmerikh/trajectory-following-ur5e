# trajectory-following-ur5e
Ur5e robot modeled in webots and motion planning in moveit


first sourcing:
source /opt/ros/${ROS_DISTRO}/setup.bash
source install/setup.bash


second: in terminl 1:
ros2 launch webots_ros2_universal_robot robot_world_launch.py

third in terminal 2: 
ros2 launch webots_ros2_universal_robot robot_moveit_nodes_launch.py


fourth: in terminal 3 
ros2 launch motion_project my_moveit_ur_launch.py
