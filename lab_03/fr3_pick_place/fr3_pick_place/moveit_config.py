"""MoveIt parameters for the FR3 with Franka Hand, shared by the launch files."""

import os

from ament_index_python.packages import get_package_share_directory
from launch.substitutions import Command, FindExecutable
from launch_ros.parameter_descriptions import ParameterValue
import yaml

MOVEIT_CONFIG_PKG = 'franka_fr3_moveit_config'


def load_yaml(package, path):
    with open(os.path.join(get_package_share_directory(package), path)) as f:
        return yaml.safe_load(f)


def robot_description(xacro_file, **mappings):
    args = ''.join(f' {key}:={value}' for key, value in mappings.items())
    return {'robot_description': ParameterValue(
        Command([FindExecutable(name='xacro'), ' ', xacro_file, args]), value_type=str)}


def robot_description_semantic():
    srdf = os.path.join(get_package_share_directory('franka_description'),
                        'robots', 'fr3', 'fr3.srdf.xacro')
    return {'robot_description_semantic': ParameterValue(
        Command([FindExecutable(name='xacro'), ' ', srdf, ' hand:=true ee_id:=franka_hand']),
        value_type=str)}


def kinematics():
    return {'robot_description_kinematics':
            load_yaml(MOVEIT_CONFIG_PKG, 'config/kinematics.yaml')}


def planning_pipeline():
    pipeline = {
        'move_group': {
            'planning_plugin': 'ompl_interface/OMPLPlanner',
            'request_adapters':
                'default_planner_request_adapters/AddTimeOptimalParameterization '
                'default_planner_request_adapters/ResolveConstraintFrames '
                'default_planner_request_adapters/FixWorkspaceBounds '
                'default_planner_request_adapters/FixStartStateBounds '
                'default_planner_request_adapters/FixStartStateCollision '
                'default_planner_request_adapters/FixStartStatePathConstraints',
            'start_state_max_bounds_error': 0.1,
        }
    }
    pipeline['move_group'].update(load_yaml(MOVEIT_CONFIG_PKG, 'config/ompl_planning.yaml'))
    return pipeline


def move_group_parameters(description):
    return [
        description,
        robot_description_semantic(),
        kinematics(),
        planning_pipeline(),
        {
            'moveit_simple_controller_manager':
                load_yaml('fr3_pick_place', 'config/moveit_controllers.yaml'),
            'moveit_controller_manager':
                'moveit_simple_controller_manager/MoveItSimpleControllerManager',
            'moveit_manage_controllers': True,
            'trajectory_execution.allowed_execution_duration_scaling': 1.2,
            'trajectory_execution.allowed_goal_duration_margin': 0.5,
            'trajectory_execution.allowed_start_tolerance': 0.01,
            'publish_planning_scene': True,
            'publish_geometry_updates': True,
            'publish_state_updates': True,
            'publish_transforms_updates': True,
        },
    ]


def rviz_parameters(description):
    return [description, robot_description_semantic(), planning_pipeline(), kinematics()]


def rviz_config():
    return os.path.join(get_package_share_directory(MOVEIT_CONFIG_PKG), 'rviz', 'moveit.rviz')
