"""
Map turtlebot3_world with slam_toolbox: the simulation, slam_toolbox in online async mode, and RViz
showing the map as it grows.

Usage:
    ros2 launch turtlebot3_sim mapping.launch.py
    ros2 run teleop_twist_keyboard teleop_twist_keyboard
    ros2 run nav2_map_server map_saver_cli -f ~/turtlebot3_ws/src/turtlebot3_sim/maps/turtlebot3_world
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("turtlebot3_sim")
    gui = LaunchConfiguration("gui")

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share, "launch", "simulation.launch.py")),
        launch_arguments={"gui": gui}.items(),
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory("slam_toolbox"), "launch", "online_async_launch.py")),
        launch_arguments={"use_sim_time": "true"}.items(),
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", os.path.join(pkg_share, "rviz", "mapping.rviz")],
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    return LaunchDescription([
        DeclareLaunchArgument("gui", default_value="true", description="Open the Gazebo window"),
        simulation,
        slam,
        rviz,
    ])
