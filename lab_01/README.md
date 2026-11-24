# Lab 1: ROS 2 and Custom Robot Simulation

ROS 2 basics on turtlesim, then `diffdrive_bot`: a two-wheeled robot with a lidar and a camera,
described in URDF, simulated in Gazebo and driven by Python nodes that use topics, services and actions.

## Contents

- ROS 2 beginner tutorials on turtlesim, in their Python version:
  [Humble](https://docs.ros.org/en/humble/Tutorials.html), [Jazzy](https://docs.ros.org/en/jazzy/Tutorials.html)
- [diffdrive_bot](diffdrive_bot): the robot, its Gazebo world, launch files and nodes, with a walkthrough
  in its [README](diffdrive_bot/README.md)
- [lab_interfaces](lab_interfaces): `ObstacleInfo.msg`, `SetSpeed.srv` and `DriveDistance.action`
- [EXERCISE.md](EXERCISE.md): the exercise, handed in as a GitHub repository

## Requirements

The [course requirements](../README.md#requirements), and:

```bash
sudo apt install ros-humble-xacro ros-humble-joint-state-publisher-gui ros-humble-teleop-twist-keyboard
```

## Build

```bash
cd ~/ros2_ws
colcon build --symlink-install --packages-up-to diffdrive_bot
```

Usage is in the [diffdrive_bot README](diffdrive_bot/README.md#usage).
