# Lab 5 Exercise: Gestures, Voice and the Franka Arm

The exercise has three parts. In Part 1 you change which gestures give which commands and add gestures
for new tasks. In Part 2 you do the same for voice. In Part 3 you use both to control the Franka FR3
from [Lab 3](../lab_03).

Read each node before you change your copy of it.

## Before you start

Run Lab 5 on your computer as its [README](README.md) describes, with speech and with gestures. For
Part 3, also run `fr3_pick_place` from Lab 3 on mock hardware.

## Your project folder

Work in a folder of your own, `lab5_exercise`, in the `src` folder of your workspace. Copy `robot_hri`
into it and make the lab's copy invisible to colcon:

```bash
cd ~/ros2_ws/src
mkdir lab5_exercise
cp -r aau-msc-robotics-labs/lab_05/robot_hri lab5_exercise/
touch aau-msc-robotics-labs/lab_05/COLCON_IGNORE
cd ~/ros2_ws
rm -rf build install log
colcon build --symlink-install
```

## Part 1: Gestures

### Step 1: A different finger layout

The finger layout is fixed in `FINGER_COMMANDS` in `gesture_commands.py`. Make it a parameter,
`commands`: the list of six commands for 0 to 5 raised fingers, with the current list as its default.
Then run the node with this layout:

| Fingers | Command |
|---------|---------|
| 0 (fist) | stop |
| 1 | forward |
| 2 | left |
| 3 | right |
| 4 | back |
| 5 (open palm) | stop |

**Check.**

```bash
ros2 run robot_hri gesture_commands.py --ros-args \
  -p commands:="['stop', 'forward', 'left', 'right', 'back', 'stop']"
```

Two fingers turn the robot left, and four drive it backwards.

### Step 2: Gestures for new tasks

Add two commands to `command_driver.py`: `faster` raises `linear_speed` by 0.05 m/s and `slower`
lowers it by 0.05 m/s, within 0.05 to 0.5 m/s. The robot keeps doing what it did before, at the new
speed.

The finger count cannot tell these gestures apart from the others: one raised thumb and one raised
index finger both count as one. Change `count_fingers` so that it returns which fingers are raised, not
only how many, and use it to recognize:

| Gesture | Command |
|---------|---------|
| thumb only | faster |
| little finger only | slower |

All other gestures keep the layout of Step 1.

The node publishes a command only when it differs from the last one, so showing the thumb twice sends
`faster` once. Change it so that a command is sent again when the hand has left the view in between.

**Check.** While the robot drives forward, show the thumb three times: `ros2 topic echo /cmd_vel`
shows `linear.x` going from 0.2 to 0.35. Show the little finger and it goes down again.

## Part 2: Voice

### Step 3: Other words for the same commands

Make the speech node understand more than one word for a command:

| Words | Command |
|-------|---------|
| forward, go | forward |
| back, reverse | back |
| left | left |
| right | right |
| stop, halt | stop |

Every word must be in the recognizer's word list, and the node publishes the command, not the word.

**Check.** Say "go", then "halt": `ros2 topic echo /command` shows `forward`, then `stop`.

### Step 4: Voice for new tasks

Add three spoken commands:

| Say | Robot |
|-----|-------|
| "faster" | the `faster` command from Step 2 |
| "slower" | the `slower` command from Step 2 |
| "spin" | turns once on the spot and stops |

For `spin`, `command_driver.py` turns at `angular_speed` for the time one full turn takes, then
switches to `stop`. Another command during the spin ends it.

**Check.** Say "spin": the robot turns once and stops. Say "spin", then "stop" halfway: it stops at
once.

## Part 3: The Franka arm

Build your workspace with the Franka workspace sourced, as in Lab 3, so that `fr3_pick_place` is
found.

### Step 5: Words and gestures for the arm

Add the words `pick` and `home` to the speech node. Run the gesture node with a layout for the arm:

```
['stop', 'pick', 'home', 'stop', 'stop', 'stop']
```

**Check.** `ros2 topic echo /command` shows `pick` and `home` when you say them, and when you show one
and two fingers.

### Step 6: A node that drives the arm

Write a node, `arm_commands`, that subscribes to `/command` and drives the arm:

| Command | Arm |
|---------|-----|
| `pick` | Runs the pick-and-place task of `fr3_pick_place` |
| `home` | Moves to the ready pose |
| `stop` | Stops the task after the step it is doing |

`fr3_pick_place/pick_place.py` builds the task as a list of steps in `run()`. Run the steps one at a
time and check for a `stop` between them. The node waits for MoveIt while a step runs, so commands that
arrive meanwhile need a second thread: look at how the Lab 1 action server uses a
`MultiThreadedExecutor`.

**Check.** Start the arm on mock hardware (`ros2 launch fr3_pick_place sim.launch.py`) and your nodes.
Say "pick": the arm places the cubes in the basket. Say "pick" again and show an open palm while the
arm moves: it stops after the current step.

### Step 7: A launch file

Write `arm_hri.launch.py`. It starts the arm on mock hardware, the speech and gesture nodes with the arm
layout, and `arm_commands`.

**Check.** One command starts everything, and the arm can be run by voice and by hand.
