# Robotics and Intelligent Systems Labs

[![Addis Ababa University](https://img.shields.io/badge/Addis_Ababa_University-aau.edu.et-2A7CBD)](https://www.aau.edu.et)
![ROS 2 Humble](https://img.shields.io/badge/ROS_2-Humble-22314E?logo=ros)
![Gazebo Harmonic](https://img.shields.io/badge/Gazebo-Harmonic-F58113)
![License: MIT](https://img.shields.io/badge/License-MIT-blue)

ROS 2 and Gazebo labs for **Robotics and Intelligent Systems**, a course in the MSc in Artificial
Intelligence at Addis Ababa University, academic year 2026. Lecturer: Adane Letta (PhD). Lab
assistant: Mohammed Sraj.

## Labs

- [Lab 1: ROS 2 and custom robot simulation](lab_01)
   - ROS 2 concepts on turtlesim: nodes, topics, services, parameters, actions, launch files
   - A differential-drive robot with a lidar and a camera, described in URDF and simulated in Gazebo
   - Python nodes that use a custom message, service and action
- [Lab 2: Perception, sensor fusion and SLAM](lab_02)
   - Object detection and segmentation with pretrained YOLOv8 models on the robot's camera
   - Detections and masks published as ROS 2 messages and shown in RViz
   - A safety stop that halts the robot when an object is in its path
   - A TurtleBot3 Burger mapping a world with slam_toolbox
- [Lab 3: Motion planning and control](lab_03)
   - Pick-and-place with a Franka FR3 arm and MoveIt 2, on mock hardware and in Gazebo
   - Joint-space goals, pose goals, Cartesian paths and attached collision objects
- [Lab 4: Reinforcement learning](lab_04)
   - MuJoCo Hopper and Walker2d robots trained to move forward with PPO from Stable-Baselines3
   - Other Stable-Baselines3 algorithms and parallel environments, chosen by option
   - Learning curves in TensorBoard and the trained policies in the MuJoCo viewer

     <a href="https://youtu.be/8dkFIp1XXiU"><img src="https://img.youtube.com/vi/8dkFIp1XXiU/maxresdefault.jpg" alt="Lab 4 demo" width="400"></a>
- [Lab 5: Human-robot interaction](lab_05) (under development)
   - Spoken commands recognized offline with Vosk
   - Hand gestures recognized on the webcam with MediaPipe
   - The Lab 1 robot driven in Gazebo by voice and by hand
- [Lab 6: Localization and navigation](lab_06)
   - AMCL localization on the map from Lab 2
   - Navigation to goals with Nav2, from RViz and from a waypoint patrol node

## Prerequisites

- Python programming basics
- Linux command line basics

## Requirements

- Ubuntu 22.04 with ROS 2 Humble (`ros-humble-desktop`)
- Gazebo Harmonic and its ROS 2 packages, from the Gazebo apt repository:

```bash
sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt update
sudo apt install ros-humble-ros-gzharmonic
```

Install with apt, not `rosdep install`: rosdep pulls in `ros-humble-ros-gz`, which conflicts with
Harmonic.

Each lab's README lists the packages it adds.

## Installation

```bash
source /opt/ros/humble/setup.bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone https://github.com/berito/aau-msc-robotics-labs.git
```

A folder is added for each new lab. To get it:

```bash
cd ~/ros2_ws/src/aau-msc-robotics-labs
git pull
```

## Usage

Each lab folder has a `README.md` (what the lab covers, what it needs, how to run it), an
`EXERCISE.md` where the lab has one, and its ROS 2 packages.

Build only the lab you are working on; its README names the package:

```bash
cd ~/ros2_ws
colcon build --symlink-install --packages-up-to <package>
```

In every new terminal:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

## Getting help

Questions and problems with the labs go to [GitHub Issues](https://github.com/berito/aau-msc-robotics-labs/issues).

## License

[MIT](LICENSE)
