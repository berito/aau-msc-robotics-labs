"""
TurtleBot3 Burger in turtlebot3_world on Gazebo Harmonic, with its topics bridged to ROS 2.

Usage:
    ros2 launch turtlebot3_sim simulation.launch.py
    ros2 launch turtlebot3_sim simulation.launch.py gui:=false
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("turtlebot3_sim")
    world = os.path.join(pkg_share, "worlds", "turtlebot3_world.world")
    with open(os.path.join(pkg_share, "urdf", "turtlebot3_burger.urdf")) as f:
        robot_description = f.read()

    # must be set before Gazebo starts
    model_path = AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", os.path.join(pkg_share, "models"))

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py")),
        launch_arguments={"gz_args": [
            world, " -r",
            PythonExpression(["'' if '", LaunchConfiguration("gui"), "' == 'true' else ' -s'"]),
        ]}.items(),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description, "use_sim_time": True}],
        output="screen",
    )

    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", "burger",
            "-file", os.path.join(pkg_share, "models", "turtlebot3_burger", "model.sdf"),
            "-x", LaunchConfiguration("x"),
            "-y", LaunchConfiguration("y"),
            "-z", "0.01",
        ],
        output="screen",
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{"config_file": os.path.join(pkg_share, "config", "bridge.yaml")}],
        output="screen",
    )

    return LaunchDescription([
        DeclareLaunchArgument("gui", default_value="true", description="Open the Gazebo window"),
        DeclareLaunchArgument("x", default_value="-2.0", description="Start position x (m)"),
        DeclareLaunchArgument("y", default_value="-0.5", description="Start position y (m)"),
        model_path,
        gazebo,
        robot_state_publisher,
        spawn,
        bridge,
    ])
