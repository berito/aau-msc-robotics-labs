# Lab 5: Human-Robot Interaction

`diffdrive_bot` from Lab 1 driven in Gazebo by voice and by hand. Spoken commands are recognized
offline with Vosk, and hand gestures on the webcam with MediaPipe. Both give the same five commands:
forward, back, left, right and stop.

Human-robot interaction (HRI) is the study of robots used by or with people: how they are
understood, designed and evaluated. A robot can interact with a person through four modalities:

- Vision: the person's body, face, pose, gestures and emotion, seen by a camera
- Auditory and language: speech recognition and dialogue
- Haptics: touch and force between the person and the robot
- Physiological sensing: signals from the body, such as EEG, EMG or IMUs

This lab uses two of them: language (spoken commands) and vision (hand gestures).

## Requirements

- The [course requirements](../README.md#requirements)
- `diffdrive_bot` from [Lab 1](../lab_01)
- A microphone and a webcam
- About 800 MB of disk space

## Installation

### 1. System packages

```bash
sudo apt install python3.10-venv libportaudio2
```

### 2. Python packages and models

```bash
cd ~/ros2_ws/src/aau-msc-robotics-labs
git pull
./lab_05/setup.sh
```

`setup.sh` installs Vosk, sounddevice, MediaPipe and OpenCV into `lab_05/.venv`, and downloads the
Vosk English model and the MediaPipe hand landmarker into `robot_hri/models/`.

### 3. Build

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
colcon build --symlink-install --packages-up-to robot_hri
```

Before running anything, in each terminal:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
source ~/ros2_ws/src/aau-msc-robotics-labs/lab_05/.venv/bin/activate
```

### 4. Choose the microphone and the webcam

List the microphones:

```bash
python3 -m sounddevice
```

The default input is marked with `>`. To use another microphone, pass its index: `microphone:=2`.

List the webcams:

```bash
ls /dev/video*
```

`/dev/video0` is camera `0`, the default. To use another camera, pass its number: `camera:=2`.

## Commands

| Command | Say | Show | Robot |
|---------|-----|------|-------|
| forward | "forward" | 1 finger | drives forward |
| back | "back" | 2 fingers | drives backward |
| left | "left" | 3 fingers | turns left |
| right | "right" | 4 fingers | turns right |
| stop | "stop" | open palm or fist | stops |

The robot keeps doing the last command until it gets the next one.

## Usage

### Speech

```bash
ros2 launch robot_hri hri.launch.py input:=speech
```

Starts Gazebo and RViz with the robot, the speech node and the driver. Say a command; the terminal
shows what was heard.

### Gestures

```bash
ros2 launch robot_hri hri.launch.py input:=gesture
```

Starts the simulation, the gesture node and the driver, and opens a camera window with the hand
landmarks and the finger count. Hold a gesture until the command shows in the terminal.

### Both

```bash
ros2 launch robot_hri hri.launch.py
```

The last command from either input wins.

### Running the nodes separately

```bash
ros2 launch diffdrive_bot gazebo.launch.py
```

then, each in its own terminal:

```bash
ros2 run robot_hri command_driver.py
ros2 run robot_hri speech_commands.py
ros2 run robot_hri gesture_commands.py
```

Send a command from the terminal:

```bash
ros2 topic pub --once /command std_msgs/msg/String "{data: left}"
```

Watch the commands:

```bash
ros2 topic echo /command
```

## How it works

| Node | Method |
|------|--------|
| `speech_commands.py` | Vosk speech recognizer (Kaldi), limited to the five command words |
| `gesture_commands.py` | MediaPipe hand landmarker (21 points on the hand); a finger is raised when its tip is farther from the wrist than its middle joint |
| `command_driver.py` | Sends the last command on `/command` as a velocity on `/cmd_vel`, at 10 Hz |

## Package layout

```
lab_05/
  setup.sh                 creates .venv and downloads the models
  requirements.txt
  EXERCISE.md
  robot_hri/
    models/                Vosk model and hand landmarker (created by setup.sh)
    launch/
      hri.launch.py        simulation, driver, and the speech and gesture nodes
    scripts/
      speech_commands.py   microphone to /command
      gesture_commands.py  webcam to /command
      command_driver.py    /command to /cmd_vel
```

## Launch arguments

| Argument | Default | Meaning |
|----------|---------|---------|
| `input` | `both` | What drives the robot: `speech`, `gesture` or `both` |
| `microphone` | default microphone | Microphone index or name, from `python3 -m sounddevice` |
| `camera` | `0` | Webcam index, or the path of a video file |

## Parameters

| Node | Parameter | Default | Meaning |
|------|-----------|---------|---------|
| command_driver | `linear_speed` | `0.2` | Forward and backward speed, m/s |
| | `angular_speed` | `0.5` | Turning speed, rad/s |
| speech_commands | `model_path` | `models/vosk-model-small-en-us-0.15` | Vosk model folder |
| | `device` | default microphone | Microphone index or name |
| gesture_commands | `camera` | `0` | Webcam index, or the path of a video file |
| | `model_path` | `models/hand_landmarker.task` | Hand landmarker model |
| | `hold_frames` | `5` | Frames a gesture must be held before it is sent |
| | `show` | `true` | Show the camera window |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `OSError: PortAudio library not found` | `sudo apt install libportaudio2` |
| `ModuleNotFoundError: No module named 'vosk'` or `'mediapipe'` | Activate `lab_05/.venv` |
| Nothing is heard | Check the microphone with `python3 -m sounddevice` and pass its index: `microphone:=2` |
| `Cannot open camera 0` | Try another index: `camera:=1` |
| The finger count is wrong | Hold the hand up, palm towards the camera, in good light |
| The robot does not move | Check `ros2 topic echo /command`; if commands arrive, check that only one node publishes on `/cmd_vel` |

## Exercise

[EXERCISE.md](EXERCISE.md)
