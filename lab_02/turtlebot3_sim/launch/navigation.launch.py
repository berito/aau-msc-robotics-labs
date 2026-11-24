"""
Navigate turtlebot3_world on the saved map: the simulation, Nav2 with AMCL localization, and RViz
with the Nav2 tools.

Usage:
    ros2 launch turtlebot3_sim navigation.launch.py
    ros2 launch turtlebot3_sim navigation.launch.py map:=/path/to/map.yaml
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
    nav2_share = get_package_share_directory("nav2_bringup")

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share, "launch", "simulation.launch.py")),
        launch_arguments={"gui": LaunchConfiguration("gui")}.items(),
    )

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_share, "launch", "bringup_launch.py")),
        launch_arguments={"map": LaunchConfiguration("map"), "use_sim_time": "true"}.items(),
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", os.path.join(nav2_share, "rviz", "nav2_default_view.rviz")],
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    return LaunchDescription([
        DeclareLaunchArgument("gui", default_value="true", description="Open the Gazebo window"),
        DeclareLaunchArgument("map", default_value=os.path.join(pkg_share, "maps", "turtlebot3_world.yaml"),
                              description="Map to navigate on"),
        simulation,
        nav2,
        rviz,
    ])
