# Lab 3: Motion Planning and Control

Pick-and-place with a Franka FR3 arm and its Franka Hand. The arm picks three cubes from a table and
drops them into a basket, with MoveIt 2 planning every motion. It runs on mock hardware in RViz or in
Gazebo.

## Contents

- [fr3_pick_place](fr3_pick_place): the pick-and-place node, its launch files, the Gazebo world and the
  controller configuration, with a walkthrough in its [README](fr3_pick_place/README.md)

The FR3 model, its MoveIt configuration and its controllers come from Franka Robotics'
[franka_ros2](https://github.com/frankarobotics/franka_ros2). They are built once in their own
workspace, next to the course workspace from the [course installation](../README.md#installation):

```
~/
  franka_ros2_ws/                 Franka workspace, created in the steps below
    src/                          franka_ros2, its dependencies and gz_ros2_control
  ros2_ws/                        course workspace
    src/aau-msc-robotics-labs/    this repository
      lab_03/fr3_pick_place/      the lab package
```

## Requirements

The [course requirements](../README.md#requirements), and:

```bash
sudo apt install ros-humble-moveit ros-dev-tools
```

## Franka workspace

Set the Gazebo version:

```bash
echo 'export GZ_VERSION=harmonic' >> ~/.bashrc
source ~/.bashrc
```

Get the sources of `franka_ros2`, the packages it depends on, and `gz_ros2_control`:

```bash
source /opt/ros/humble/setup.bash
mkdir -p ~/franka_ros2_ws/src
cd ~/franka_ros2_ws
git clone -b humble https://github.com/frankarobotics/franka_ros2.git src
vcs import src < src/dependency.repos --recursive --skip-existing
git clone -b humble https://github.com/ros-controls/gz_ros2_control.git src/gz_ros2_control
```

Skip the packages the lab does not use, and install the dependencies:

```bash
cd ~/franka_ros2_ws
touch src/franka_gazebo/franka_gazebo_hardware/COLCON_IGNORE
touch src/franka_mobile/COLCON_IGNORE src/franka_mobile_sensors/COLCON_IGNORE
rosdep install --from-paths src --ignore-src --rosdistro humble -y \
  --skip-keys "ros_gz sdformat_urdf franka_gazebo_hardware franka_mobile franka_mobile_sensors"
```

Build it. This takes several minutes:

```bash
cd ~/franka_ros2_ws
PATH=/usr/bin:$PATH colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=OFF
source install/setup.bash
```

Test it:

```bash
ros2 launch franka_fr3_moveit_config moveit.launch.py robot_ip:=dont-care use_fake_hardware:=true
```

RViz opens with the FR3. To plan a motion, tick **MotionPlanning** in the Displays panel, drag the
marker at the gripper and click **Plan & Execute**: the arm moves to the new pose.

## Build

```bash
source /opt/ros/humble/setup.bash
source ~/franka_ros2_ws/install/setup.bash
cd ~/ros2_ws/src/aau-msc-robotics-labs
git pull
cd ~/ros2_ws
colcon build --symlink-install --packages-up-to fr3_pick_place
```

Before running anything, in each terminal:

```bash
source /opt/ros/humble/setup.bash
source ~/franka_ros2_ws/install/setup.bash
source ~/ros2_ws/install/setup.bash
```

Usage is in the [fr3_pick_place README](fr3_pick_place/README.md#usage).
