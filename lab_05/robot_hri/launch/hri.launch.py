"""
Drive diffdrive_bot in Gazebo by speech, by hand gestures, or by both.

Usage:
    ros2 launch robot_hri hri.launch.py input:=speech
    ros2 launch robot_hri hri.launch.py input:=gesture
    ros2 launch robot_hri hri.launch.py input:=both
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    bot_share = get_package_share_directory("diffdrive_bot")
    input_mode = LaunchConfiguration("input")

    def uses(mode):
        return IfCondition(PythonExpression(["'", input_mode, "' in ('", mode, "', 'both')"]))

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(bot_share, "launch", "gazebo.launch.py")))

    driver = Node(
        package="robot_hri",
        executable="command_driver.py",
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    speech = Node(
        package="robot_hri",
        executable="speech_commands.py",
        parameters=[{"device": ParameterValue(LaunchConfiguration("microphone"), value_type=str)}],
        output="screen",
        condition=uses("speech"),
    )

    gesture = Node(
        package="robot_hri",
        executable="gesture_commands.py",
        parameters=[{"camera": ParameterValue(LaunchConfiguration("camera"), value_type=str)}],
        output="screen",
        condition=uses("gesture"),
    )

    return LaunchDescription([
        DeclareLaunchArgument("input", default_value="both", choices=["speech", "gesture", "both"],
                              description="Which commands drive the robot"),
        DeclareLaunchArgument("microphone", default_value="",
                              description="Microphone index or name; empty for the default"),
        DeclareLaunchArgument("camera", default_value="0", description="Webcam index, or the path of a video file"),
        simulation,
        driver,
        speech,
        gesture,
    ])
