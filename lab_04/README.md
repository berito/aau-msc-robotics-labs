# Lab 4: Reinforcement Learning

Two MuJoCo robots, the one-legged Hopper and the two-legged Walker2d, learn to move forward with
reinforcement learning (PPO from Stable-Baselines3). Training runs on a laptop CPU, the learning
curves are shown in TensorBoard, and the trained policies are played in the MuJoCo viewer.

## Requirements

- Ubuntu 22.04 with Python 3.10
- About 1.2 GB of disk space for the Python environment, about 6 GB with `--gpu`
- Optional: an NVIDIA GPU with driver 580 or newer

## Installation

```bash
sudo apt install python3.10-venv
cd ~/ros2_ws/src/aau-msc-robotics-labs
git pull
./lab_04/setup.sh
```

`setup.sh` installs PyTorch, Gymnasium with MuJoCo, Stable-Baselines3, TensorBoard and OpenCV into
`lab_04/.venv`. `./lab_04/setup.sh --gpu` installs the CUDA build of PyTorch in place of the CPU
build.

Before running anything, in each terminal:

```bash
source ~/ros2_ws/src/aau-msc-robotics-labs/lab_04/.venv/bin/activate
cd ~/ros2_ws/src/aau-msc-robotics-labs/lab_04/walker
```

## Usage

### Watch the trained Hopper

```bash
python play_hopper.py
```

Plays the policy in `models/hopper.zip`, trained for one million steps, and prints the return of each
episode.

### Train

```bash
python train_hopper.py
```

Trains for one million steps, about 12 minutes on a laptop CPU, and replaces `models/hopper.zip`. A
short run under another name:

```bash
python train_hopper.py --timesteps 200000 --name short_run
python play_hopper.py --name short_run
```

### Walker2d

```bash
python play_walker2d.py
python train_walker2d.py
```

Same options as the Hopper scripts. `models/walker2d.zip` is trained for one million steps.

### Watch it learn

```bash
python train_hopper.py --watch --timesteps 20000
```

Shows the Hopper in the viewer while it trains. Training is about 25 times slower, this run takes
about 6 minutes and saves nothing.

Several robots at once, one tile each:

```bash
python train_walker2d.py --watch --envs 4 --timesteps 20000
```

### Parallel environments and GPU

```bash
python train_hopper.py --envs 4
```

Runs 4 environments in parallel, one process each. Use at most the number of CPU cores.

`--device cuda` trains the networks on the GPU and needs `setup.sh --gpu`. The simulation stays on the
CPU, and for networks this small the GPU is slower than the CPU: about 950 against 1500 steps per
second for the Hopper.

## Reinforcement learning in this lab

In reinforcement learning an agent learns by trial and error: it acts, sees what happens, and is
given a number, the reward, that says how good that was. Nobody shows it the right action. Over many
attempts it learns which actions lead to high reward.

### The tools

| Tool | What it is | Used for |
|------|------------|----------|
| MuJoCo | A physics engine for robots: bodies, joints, contacts and motors | Simulating the Hopper and showing it in the viewer |
| Gymnasium | A Python library of RL environments with one interface: `reset()` starts an episode, `step(action)` returns the next observation and the reward | The `Hopper-v5` environment, built on MuJoCo |
| Stable-Baselines3 | A Python library of tested RL algorithms, built on PyTorch, that train on any Gymnasium environment | The PPO algorithm, saving and loading the policy |
| PyTorch | A deep learning library | The policy and value networks inside Stable-Baselines3 |
| TensorBoard | A viewer for training curves | Following the return while training |
| OpenCV | An image library | Showing several robots in one window with `--watch --envs` |

### The concepts

| Concept | Meaning | In this lab |
|---------|---------|-------------|
| Environment | The world the agent acts in | `Hopper-v5`: the Hopper simulated in MuJoCo |
| Agent | The learner that chooses the actions | A PPO model from Stable-Baselines3, created in `trainer.py` |
| Observation (state) | What the agent sees at each step | 11 numbers: body height and angle, joint angles, and their velocities |
| Action | What the agent does at each step | 3 torques, at the thigh, leg and foot joints |
| Reward | The score for one step | Forward speed + 1 for staying upright - a small cost for large torques |
| Episode | One attempt, from start to end | Ends when the Hopper falls, or after 1000 steps |
| Return | The sum of the rewards of an episode | What training tries to make as large as possible |
| Policy | The rule that maps an observation to an action | A neural network with two layers of 64 units |
| Value function | The return expected from a state | A second network of the same size, used to judge the actions |
| Exploration | Trying actions that are not yet known to be good | The policy outputs a distribution and actions are sampled from it; `play_hopper.py` uses its mean |

### How PPO learns

PPO (Proximal Policy Optimization) repeats two phases until the step budget is used:

1. **Collect:** run the current policy for 2048 steps and store what it saw, did and was given.
2. **Improve:** for each step, compare the return that followed with what the value function
   predicted. Actions that did better become more likely, actions that did worse less likely. Each
   change is kept small (clipped) so one bad batch cannot ruin the policy. The value function is
   updated to predict better.

One million steps are about 490 of these rounds.

### Other algorithms in Stable-Baselines3

PPO is one of several algorithms in Stable-Baselines3. The train and play scripts take the algorithm
as an option:

```bash
python train_hopper.py --algo sac --timesteps 300000
python play_hopper.py --algo sac
```

Each algorithm is saved under its own name, `hopper_<algo>`.

| Algorithm | Type | Actions | Notes |
|-----------|------|---------|-------|
| PPO | On-policy | Continuous or discrete | Learns from the latest rollout only, then discards it; stable and fast per step |
| A2C | On-policy | Continuous or discrete | A simpler version of the same idea; usually learns less well than PPO |
| SAC | Off-policy | Continuous | Keeps past experience in a replay buffer and reuses it; needs fewer steps, but each step is slower |
| TD3 | Off-policy | Continuous | A deterministic policy with added noise for exploration; similar to SAC |
| DQN | Off-policy | Discrete only | Cannot control the Hopper, whose actions are continuous torques; not offered |

On-policy algorithms learn only from data collected by the current policy; off-policy algorithms
also learn from data collected by earlier versions of it.

### Other robots in Gymnasium

Gymnasium comes with more MuJoCo robots, all installed with this lab. The reward options of
the train scripts work only where the environment has the same weights.

| Environment | Robot | Observations | Actions | Reward options it accepts |
|-------------|-------|--------------|---------|---------------------------|
| `Hopper-v5` | One leg, hops | 11 | 3 | all three |
| `Walker2d-v5` | Two legs, walks | 17 | 6 | all three |
| `HalfCheetah-v5` | Cheetah-like, runs | 17 | 6 | `forward-weight`, `ctrl-cost` |
| `Ant-v5` | Four legs, walks | 105 | 8 | all three |
| `Swimmer-v5` | Snake-like, swims | 8 | 2 | `forward-weight`, `ctrl-cost` |
| `Humanoid-v5` | Human, walks | 348 | 17 | all three |
| `HumanoidStandup-v5` | Human, stands up from lying | 348 | 17 | `ctrl-cost` |
| `Reacher-v5` | 2-joint arm, reaches a target | 10 | 2 | none |
| `Pusher-v5` | 7-joint arm, pushes an object | 23 | 7 | none |
| `InvertedPendulum-v5` | Cart balancing a pole | 4 | 1 | none |
| `InvertedDoublePendulum-v5` | Cart balancing two poles | 9 | 1 | `healthy-reward` |

Each robot has a pair of scripts, `train_<robot>.py` and `play_<robot>.py`, that call `main()` in
`trainer.py` and `player.py` with the robot's environment. Another robot needs its own pair, and
`env_kwargs` in `trainer.py` limited to the reward options it accepts. This is Step 3 of the exercise.

### The learning curve

The train scripts write the curves to `walker/runs/<name>_1`. To see them:

```bash
tensorboard --logdir runs
```

Open http://localhost:6006. The two curves to follow:

| Curve | Meaning | Default run |
|-------|---------|-------------|
| `rollout/ep_rew_mean` | Mean return per episode | Rises to about 1000 by 300000 steps and passes 2000 from about 550000 |
| `rollout/ep_len_mean` | Mean episode length in steps, 1000 at most | Rises from under 100 to 600-700: the Hopper stays up longer |

Both are averages over the last 100 episodes, so they keep moving up and down after the policy has
learned to hop.

### Settings

The settings of each algorithm are in `walker/algorithms.py`.

| Algorithm | Settings |
|-----------|----------|
| PPO | Rollouts of 2048 steps, 10 epochs, batch 64, learning rate 3e-4, clip range 0.2, gamma 0.99, GAE lambda 0.95; policy and value networks with two hidden layers of 64 units, tanh |
| A2C | Stable-Baselines3 defaults |
| SAC | Stable-Baselines3 defaults; learning starts after 10000 random steps |
| TD3 | Stable-Baselines3 defaults; learning starts after 10000 random steps; Gaussian action noise with standard deviation 0.1 |

PPO and A2C train on observations and rewards scaled to a running mean and variance (`VecNormalize`),
saved with the policy as `<name>_vecnormalize.pkl`.

## Options

| Script | Option | Default | Meaning |
|--------|--------|---------|---------|
| train_hopper.py, train_walker2d.py | `--algo` | `ppo` | Algorithm: `ppo`, `a2c`, `sac` or `td3` |
| | `--timesteps` | `1000000` | Training steps |
| | `--name` | `<robot>`, or `<robot>_<algo>` | Name of the saved policy and the TensorBoard run |
| | `--forward-weight` | `1.0` | Weight of the forward speed in the reward |
| | `--healthy-reward` | `1.0` | Reward per step while the Hopper is upright |
| | `--ctrl-cost` | `0.001` | Weight of the torque cost in the reward |
| | `--watch` | off | Show the robot in the viewer while it trains; nothing is saved |
| | `--envs` | `1` | Environments run in parallel; with `--watch`, all are shown in one window |
| | `--device` | `cpu` | `cpu` or `cuda` for the networks |
| play_hopper.py, play_walker2d.py | `--algo` | `ppo` | Algorithm the policy was trained with |
| | `--name` | `<robot>`, or `<robot>_<algo>` | Policy to load from `models/` |
| | `--episodes` | `3` | Episodes to play |
| | `--no-render` | off | Run without the viewer |

## Layout

```
lab_04/
  setup.sh                 creates .venv
  requirements.txt
  EXERCISE.md
  walker/
    algorithms.py          the algorithms and their settings
    trainer.py             training shared by the train scripts
    player.py              playback shared by the play scripts
    train_hopper.py        trains the Hopper
    play_hopper.py         plays a trained Hopper in the viewer
    train_walker2d.py      trains the Walker2d
    play_walker2d.py       plays a trained Walker2d in the viewer
    models/                trained policies and their normalization
    runs/                  TensorBoard logs (created by the train scripts)
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'gymnasium'` | Activate `lab_04/.venv` |
| `FileNotFoundError` for `models/...` | Run from the `walker` folder, or check `--algo` and `--name` |
| The viewer does not open | Check that a display is available; `--no-render` plays without it |
| The Hopper falls after a few hops after your own training | Train longer; below about 500000 steps it has not learned to hop |
| The Hopper stands still, with a return near 1000 over 1000 steps | It collects the reward for staying upright without moving; train again, or lower `--healthy-reward` |
| `PyTorch has no CUDA support` | Run `./lab_04/setup.sh --gpu`, or train without `--device cuda` |

## Exercise

[EXERCISE.md](EXERCISE.md) has three steps:

| Step | Task | What it shows |
|------|------|---------------|
| 1 | Train three Hoppers, each with one reward weight changed | How the reward decides the behaviour the agent learns |
| 2 | Add an `--ent-coef` option and train with more exploration | How exploration changes learning |
| 3 | Train another Gymnasium robot and compare it with the Hopper and the Walker2d | The same algorithm learning different robots |
