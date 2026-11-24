# Lab 6 Exercise: Localization, Obstacles and Patrols

In this exercise you watch AMCL recover from a wrong start pose, make Nav2 drive around an obstacle that
is not on the map, change the patrol, and navigate on a map of your own.

## Before you start

Run Lab 6 on your computer as its [README](README.md) describes: navigation with RViz goals and the
patrol node.

## Your project folder

Work in a folder of your own, `lab6_exercise`, in the `src` folder of your workspace. Copy
`robot_navigation` into it and make the lab's copy invisible to colcon:

```bash
cd ~/ros2_ws/src
mkdir lab6_exercise
cp -r aau-msc-robotics-labs/lab_06/robot_navigation lab6_exercise/
touch aau-msc-robotics-labs/lab_06/COLCON_IGNORE
cd ~/ros2_ws
colcon build --symlink-install --packages-up-to robot_navigation
```

## Step 1: Recover from a wrong start pose

Start `navigation.launch.py`. With **2D Pose Estimate**, set the start pose half a metre away from the
robot and turned by about 45 degrees. Watch the particle cloud and the laser scan in RViz, then send a
goal with **Nav2 Goal**.

**Check.** At first the scan does not line up with the walls of the map. After the robot has driven
about a metre, the particles gather around the robot and the scan lines up with the map.

## Step 2: An obstacle that is not on the map

Start the patrol. In Gazebo, add a box from the Shapes toolbar on the robot's path between two
waypoints.

**Check.** The box appears in the local costmap in RViz, and the robot drives around it and reaches the
next waypoint.

## Step 3: Change the patrol

1. Write a patrol of your own that goes around the outer ring of the world, between the outer pillars
   and the wall, and run it with the `waypoints` parameter, without changing the code.
2. Add a parameter, `wait`, the number of seconds the robot stands still at each waypoint before it
   drives on. Instead of `followWaypoints`, send one waypoint at a time with `goToPose` and wait in
   between.

**Check.** The robot drives your ring, stops at each waypoint for the time you set, and the log shows
each waypoint as it is reached.

## Step 4: Navigate on your own map

Map the world as in Lab 2, then save the map into your `lab6_exercise` folder:

```bash
cd ~/ros2_ws/src/lab6_exercise
ros2 run nav2_map_server map_saver_cli -f my_map
```

Start navigation on it and run your patrol:

```bash
ros2 launch turtlebot3_sim navigation.launch.py map:=$HOME/ros2_ws/src/lab6_exercise/my_map.yaml
```

**Check.** RViz shows your map, and the patrol from Step 3 runs on it.

## Hand in

Make your `lab6_exercise` folder a Git repository and push it to GitHub. It holds your copy of
`robot_navigation` and your map. Add a README that says how to run each step, a screenshot of RViz
for Step 1 before and after the particles gather, and a short video of the patrol driving around the
box. Write what did not work and why you think so. Share your exercise by sending the GitHub URL of
this repository.
