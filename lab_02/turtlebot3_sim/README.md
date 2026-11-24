# turtlebot3_sim

A TurtleBot3 Burger in `turtlebot3_world`, simulated in Gazebo Harmonic on ROS 2 Humble. The robot is
mapped with `slam_toolbox` and navigated on the saved map with Nav2.

## Requirements

The [course requirements](../../README.md#requirements).

## Installation

### 1. Install the packages

```bash
sudo apt install ros-humble-slam-toolbox ros-humble-navigation2 ros-humble-nav2-bringup \
  ros-humble-teleop-twist-keyboard
```

### 2. Build

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws/src/aau-msc-robotics-labs
git pull
cd ~/ros2_ws
colcon build --symlink-install --packages-up-to turtlebot3_sim
```

Before running anything, in each terminal:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

## Usage

### Simulation

```bash
ros2 launch turtlebot3_sim simulation.launch.py
```

Starts Gazebo with the robot in `turtlebot3_world`. The robot listens on `/cmd_vel` and publishes
`/scan`, `/odom`, `/imu` and `/tf`.

### Mapping

```bash
ros2 launch turtlebot3_sim mapping.launch.py
```

Starts the simulation, `slam_toolbox` and RViz. In a second terminal, drive the robot:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

`i` forward, `,` back, `j` and `l` turn, `k` stop. Keep the teleop terminal focused. Drive between the
pillars and along the outer wall until the whole world shows in RViz.

In a third terminal, save the map into the package's `maps` folder:

```bash
cd ~/ros2_ws/src/aau-msc-robotics-labs/lab_02/turtlebot3_sim/maps
ros2 run nav2_map_server map_saver_cli -f turtlebot3_world
```

This writes `turtlebot3_world.pgm` (the image) and `turtlebot3_world.yaml` (resolution and origin).
Build again to install the new map.

### Navigation

```bash
ros2 launch turtlebot3_sim navigation.launch.py
```

Starts the simulation, Nav2 with the map from `maps/turtlebot3_world.yaml`, and RViz.

1. Click **2D Pose Estimate**, then click on the robot's position in the map and drag in the direction
   it faces. The robot starts at the map origin, facing along x. The AMCL particles gather around the
   robot.
2. Click **Nav2 Goal**, then click a point in the map and drag to set the final heading. The robot
   plans a path around the pillars and drives to it.

Until the start pose is set, AMCL prints `Please set the initial pose...`.

To navigate on another map:

```bash
ros2 launch turtlebot3_sim navigation.launch.py map:=/path/to/map.yaml
```

## Launch arguments

| Launch file | Argument | Default | Meaning |
|-------------|----------|---------|---------|
| all | `gui` | `true` | Open the Gazebo window |
| simulation | `x`, `y` | `-2.0`, `-0.5` | Start position in the world (m) |
| navigation | `map` | `maps/turtlebot3_world.yaml` | Map to navigate on |

## Package layout

```
turtlebot3_sim/
  launch/
    simulation.launch.py   Gazebo, robot, robot_state_publisher and bridge
    mapping.launch.py      simulation, slam_toolbox and RViz
    navigation.launch.py   simulation, Nav2 and RViz
  config/bridge.yaml       topics bridged between Gazebo and ROS 2
  maps/                    saved maps
  models/                  Burger, its meshes, and turtlebot3_world
  rviz/mapping.rviz        map, scan and robot
  urdf/                    Burger URDF for robot_state_publisher
  worlds/                  turtlebot3_world.world
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Package 'slam_toolbox' not found` or `'nav2_bringup'` | Install the packages in step 1 |
| The robot does not move with teleop | Focus the teleop terminal |
| The map is empty in RViz | Wait a few seconds; `slam_toolbox` publishes the map every 5 s |
| The robot does not move to the goal | Set the start pose with **2D Pose Estimate** first |
| Gazebo will not start, or two robots appear | `pkill -f "gz sim"` |

## Credits

The robot model, meshes, world and URDF are from ROBOTIS
[turtlebot3_simulations](https://github.com/ROBOTIS-GIT/turtlebot3_simulations), under the Apache 2.0
license in [LICENSE](LICENSE).
