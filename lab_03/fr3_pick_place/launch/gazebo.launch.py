"""FR3 with Franka Hand in Gazebo Harmonic with the table, basket and cubes, MoveIt and RViz."""

import os

from ament_index_python.packages import get_package_share_directory
from fr3_pick_place import moveit_config
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    RegisterEventHandler,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = get_package_share_directory('fr3_pick_place')
    description = moveit_config.robot_description(
        os.path.join(pkg_share, 'urdf', 'fr3_gazebo.urdf.xacro'),
        controllers_file=os.path.join(pkg_share, 'config', 'ros2_controllers.yaml'))
    sim_time = {'use_sim_time': True}

    resource_path = SetEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        os.path.dirname(get_package_share_directory('franka_description')))

    gazebo = IncludeLaunchDescription(
        PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py']),
        launch_arguments={'gz_args': [
            os.path.join(pkg_share, 'worlds', 'pick_place.sdf'), ' -r',
            PythonExpression(["'' if '", LaunchConfiguration('gui'), "' == 'true' else ' -s'"]),
        ]}.items(),
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen',
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[description, sim_time],
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', '/robot_description', '-name', 'fr3'],
        output='screen',
    )

    spawn_controllers = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', 'fr3_arm_controller', 'fr3_hand_controller',
                   '--controller-manager-timeout', '60'],
        output='screen',
    )

    move_group = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=moveit_config.move_group_parameters(description) + [sim_time],
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='log',
        arguments=['-d', moveit_config.rviz_config()],
        parameters=moveit_config.rviz_parameters(description) + [sim_time],
        condition=IfCondition(LaunchConfiguration('use_rviz')),
    )

    add_scene = Node(
        package='fr3_pick_place',
        executable='add_scene',
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_rviz', default_value='true', description='Start RViz'),
        DeclareLaunchArgument('gui', default_value='true', description='Start the Gazebo GUI'),
        resource_path,
        gazebo,
        clock_bridge,
        robot_state_publisher,
        spawn_robot,
        RegisterEventHandler(OnProcessExit(target_action=spawn_robot,
                                           on_exit=[spawn_controllers])),
        move_group,
        rviz,
        add_scene,
    ])
