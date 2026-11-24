#!/usr/bin/env python3
"""
Patrol a list of waypoints on the map with Nav2.

Sets the start pose for AMCL, waits until Nav2 is active, then sends the waypoints to Nav2's waypoint
follower, one round after another. At each waypoint the robot faces the next one.

Parameters:
    initial_pose   x, y, yaw of the robot at start, in the map frame ([0.0, 0.0, 0.0])
    waypoints      x, y of each waypoint in the map frame, as one list (a square around the
                   centre pillar of turtlebot3_world)
    rounds         rounds to drive; 0 patrols until stopped (0)

Usage:
    ros2 launch turtlebot3_sim navigation.launch.py
    ros2 run robot_navigation patrol.py
    ros2 run robot_navigation patrol.py --ros-args -p rounds:=1
"""

import math

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.parameter import Parameter

SQUARE = [1.45, -0.05, 2.55, -0.05, 2.55, 1.05, 1.45, 1.05]


def make_pose(navigator, x, y, yaw):
    pose = PoseStamped()
    pose.header.frame_id = "map"
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.z = math.sin(yaw / 2)
    pose.pose.orientation.w = math.cos(yaw / 2)
    return pose


def waypoint_poses(navigator, flat):
    points = list(zip(flat[0::2], flat[1::2]))
    poses = []
    for i, (x, y) in enumerate(points):
        next_x, next_y = points[(i + 1) % len(points)]
        poses.append(make_pose(navigator, x, y, math.atan2(next_y - y, next_x - x)))
    return poses


def main():
    rclpy.init()
    navigator = BasicNavigator()
    navigator.set_parameters([Parameter("use_sim_time", value=True)])
    navigator.declare_parameter("initial_pose", [0.0, 0.0, 0.0])
    navigator.declare_parameter("waypoints", SQUARE)
    navigator.declare_parameter("rounds", 0)

    x, y, yaw = navigator.get_parameter("initial_pose").value
    navigator.setInitialPose(make_pose(navigator, x, y, yaw))
    navigator.waitUntilNav2Active()

    rounds = navigator.get_parameter("rounds").value
    completed = 0
    try:
        while rounds == 0 or completed < rounds:
            poses = waypoint_poses(navigator, navigator.get_parameter("waypoints").value)
            navigator.followWaypoints(poses)
            current = -1
            while not navigator.isTaskComplete():
                feedback = navigator.getFeedback()
                if feedback and feedback.current_waypoint != current:
                    current = feedback.current_waypoint
                    navigator.get_logger().info(f"Driving to waypoint {current + 1}/{len(poses)}")
            if navigator.getResult() != TaskResult.SUCCEEDED:
                navigator.get_logger().error(f"Patrol stopped: {navigator.getResult()}")
                break
            completed += 1
            navigator.get_logger().info(f"Round {completed} done")
    except KeyboardInterrupt:
        navigator.cancelTask()
    finally:
        navigator.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
