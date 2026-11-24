# fr3_pick_place

Pick-and-place for the Franka FR3 with MoveIt 2. The arm picks three cubes from a table one by one and
drops each into a basket, on mock hardware in RViz (kinematic, MoveIt attaches the cubes to the hand) or
in Gazebo Harmonic (the fingers hold the cubes by friction and the cubes fall into the basket).

Build and requirements: [Lab 3 README](../README.md).

## Usage

### Mock hardware

```bash
ros2 launch fr3_pick_place sim.launch.py
```

Starts the FR3 on mock hardware, its controllers, `move_group` and RViz, with the table, basket and
cubes in the planning scene. Run the task from another terminal:

```bash
ros2 run fr3_pick_place pick_place
```

The task can be run again at any time; it resets the planning scene first. To start the cubes and the
basket somewhere else:

```bash
ros2 run fr3_pick_place pick_place --ros-args \
  -p cube_positions:="[0.45, -0.3, 0.6, -0.25, 0.5, -0.1]" -p basket_xy:="[0.5, 0.3]"
```

### Gazebo

```bash
ros2 launch fr3_pick_place gazebo.launch.py
```

Starts Gazebo with [worlds/pick_place.sdf](worlds/pick_place.sdf), spawns the FR3, and starts its
controllers, `move_group` and RViz. Run the task from another terminal:

```bash
ros2 run fr3_pick_place pick_place
```

The cubes stay in the basket: restart `gazebo.launch.py` before running the task again.

### Planning scene only

```bash
ros2 run fr3_pick_place add_scene
```

Adds the table, basket and cubes to the planning scene without running the task.

## Package layout

```
fr3_pick_place/
  fr3_pick_place/
    pick_place.py             the pick-and-place node
    moveit_config.py          MoveIt parameters used by both launch files
  launch/
    sim.launch.py             mock hardware, controllers, move_group and RViz
    gazebo.launch.py          Gazebo, robot spawn, controllers, move_group and RViz
  urdf/
    fr3_sim.urdf.xacro        FR3 with Franka Hand on mock hardware
    fr3_gazebo.urdf.xacro     FR3 with Franka Hand in Gazebo through gz_ros2_control
  config/
    ros2_controllers.yaml     trajectory controllers for the arm and the fingers
    moveit_controllers.yaml   controllers MoveIt sends trajectories to
  worlds/pick_place.sdf       table, basket and three cubes
```

## Task steps

Joint and pose goals are planned with OMPL's RRT-Connect, using the LMA inverse kinematics solver for
the pose goals. Approach and lift are straight-line Cartesian paths.

| Step | Motion |
|------|--------|
| Clear planning scene | Remove objects left from an earlier run |
| Move to ready pose | Joint-space goal, planned with OMPL |
| Place table, basket and cubes | Add collision objects to the planning scene |
| Open gripper | Finger goal on the `fr3_hand` group |

Then for each cube:

| Step | Motion |
|------|--------|
| Move above cube | Pose goal for `fr3_hand_tcp`, gripper pointing down |
| Approach cube | Straight-line Cartesian path down |
| Attach cube to gripper | The cube moves with the hand from now on |
| Close gripper | Fingers close on the cube |
| Lift cube | Straight-line Cartesian path up |
| Move over basket | Pose goal just above the rim, planned around the table, basket and cubes |
| Open gripper | The cube drops into the basket |
| Release cube into basket | The cube is placed on the basket floor in the planning scene |

The task ends with a joint-space move back to the ready pose.

## Launch arguments

| Launch file | Argument | Default | Meaning |
|-------------|----------|---------|---------|
| both | `use_rviz` | `true` | Start RViz |
| gazebo | `gui` | `true` | Open the Gazebo window |

## Parameters

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `cube_positions` | `[0.45, -0.3, 0.62, -0.3, 0.53, -0.12]` | x, y of each cube on the table, up to three cubes (m, in `fr3_link0`) |
| `basket_xy` | `[0.55, 0.25]` | Basket centre on the table (m, in `fr3_link0`) |
| `table_height` | `0.2` | Height of the table top (m) |
| `cube_size` | `0.04` | Cube edge length (m) |
| `approach_height` | `0.12` | Height above the cube for approach and lift (m) |
| `velocity_scaling` | `0.3` | Velocity and acceleration scaling for planned motions |

In Gazebo the cubes and the basket are placed by the world, so keep the defaults.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Package 'fr3_pick_place' not found` | Source the terminal |
| `Package 'franka_description' not found` | Source `~/franka_ros2_ws/install/setup.bash` before `~/ros2_ws/install/setup.bash` |
| `Python executable has not been found` while building `libfranka` | Run `rm -rf build install log` in `~/franka_ros2_ws` and build it again with `PATH=/usr/bin:$PATH` |
| The arm does not appear in Gazebo, or `gz_ros2_control-system` is not found | Check that `echo $GZ_VERSION` prints `harmonic` and `~/franka_ros2_ws/src/gz_ros2_control` exists, then build the Franka workspace again |
| Gazebo will not start, or two robots appear | `pkill -f "gz sim"` |
