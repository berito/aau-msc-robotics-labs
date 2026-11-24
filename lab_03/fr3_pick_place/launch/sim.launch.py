"""FR3 with Franka Hand on mock hardware, MoveIt move_group and RViz."""

import os

from ament_index_python.packages import get_package_share_directory
from fr3_pick_place import moveit_config
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('fr3_pick_place')
    description = moveit_config.robot_description(
        os.path.join(pkg_share, 'urdf', 'fr3_sim.urdf.xacro'))

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[description],
    )

    ros2_control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        output='screen',
        parameters=[description, os.path.join(pkg_share, 'config', 'ros2_controllers.yaml')],
    )

    spawners = [
        Node(package='controller_manager', executable='spawner',
             arguments=[name, '--controller-manager-timeout', '60'],
             output='screen')
        for name in ['joint_state_broadcaster', 'fr3_arm_controller', 'fr3_hand_controller']
    ]

    move_group = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=moveit_config.move_group_parameters(description),
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='log',
        arguments=['-d', moveit_config.rviz_config()],
        parameters=moveit_config.rviz_parameters(description),
        condition=IfCondition(LaunchConfiguration('use_rviz')),
    )

    add_scene = Node(
        package='fr3_pick_place',
        executable='add_scene',
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_rviz', default_value='true', description='Start RViz'),
        robot_state_publisher,
        ros2_control_node,
        *spawners,
        move_group,
        rviz,
        add_scene,
    ])
