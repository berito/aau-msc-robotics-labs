# Lab 6: Localization and Navigation

The TurtleBot3 Burger from Lab 2 localizes itself on the map of `turtlebot3_world` with AMCL and drives
to goals with Nav2, first from RViz and then from a patrol node.

## Contents

- [turtlebot3_sim](../lab_02/turtlebot3_sim) from Lab 2: the robot, the world, the saved map and the
  launch files
- [robot_navigation](robot_navigation): `patrol.py`, a node that drives the robot through a list of
  waypoints with Nav2 Simple Commander
- [EXERCISE.md](EXERCISE.md): the exercise, handed in as a GitHub repository

## Requirements

- The [course requirements](../README.md#requirements)
- The SLAM part of [Lab 2](../lab_02/README.md#slam): `turtlebot3_sim` installed as in its
  [README](../lab_02/turtlebot3_sim/README.md#installation). Lab 6 uses its robot, world, launch files
  and the map in `maps/`.

## Build

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws/src/aau-msc-robotics-labs
git pull
cd ~/ros2_ws
colcon build --symlink-install --packages-up-to robot_navigation
```

Before running anything, in each terminal:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

## Usage

### Navigation from RViz

```bash
ros2 launch turtlebot3_sim navigation.launch.py
```

Starts the simulation, Nav2 with the map from Lab 2, and RViz.

1. Click **2D Pose Estimate**, then click on the robot's position in the map and drag in the direction
   it faces. The robot starts at the map origin, facing along x.
2. Click **Nav2 Goal**, then click a point in the map and drag to set the final heading.

### Patrol

With `navigation.launch.py` running, in a second terminal:

```bash
ros2 run robot_navigation patrol.py
```

The node sets the start pose itself, then drives the robot in a square around the centre pillar until
stopped with Ctrl+C. For one round:

```bash
ros2 run robot_navigation patrol.py --ros-args -p rounds:=1
```

For other waypoints, as x, y pairs in the map frame:

```bash
ros2 run robot_navigation patrol.py --ros-args -p waypoints:="[1.45, -0.05, 2.55, -0.05, 2.55, 1.05]"
```

## Parameters

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `initial_pose` | `[0.0, 0.0, 0.0]` | x, y, yaw of the robot at start, in the map frame |
| `waypoints` | square around the centre pillar | x, y of each waypoint in the map frame, as one list |
| `rounds` | `0` | Rounds to drive; `0` patrols until stopped |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named 'nav2_simple_commander'` | `sudo apt install ros-humble-navigation2` |
| The robot does not move to the goal | Set the start pose with **2D Pose Estimate** first |
| The patrol waits and the robot does not move | Start `navigation.launch.py` first |
| `Patrol stopped` in the log | A waypoint is inside an obstacle or outside the map; choose another |
