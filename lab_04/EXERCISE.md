# Lab 4 Exercise: Rewards, Exploration and Other Robots

In this exercise you change the Hopper's reward and see how its gait changes, add an exploration
setting to the training script, and train a second robot.

Training for one million steps takes about 12 minutes on a laptop CPU. Start a run, then work on the
next step while it trains.

## Before you start

Run Lab 4 on your computer as its [README](README.md) describes: watch the trained Hopper, train a short
run and open its learning curve in TensorBoard.

## Your project folder

Work in a folder of your own, `lab4_exercise`, with a copy of the `walker` folder:

```bash
mkdir -p ~/lab4_exercise
cp -r ~/ros2_ws/src/aau-msc-robotics-labs/lab_04/walker ~/lab4_exercise/
cd ~/lab4_exercise/walker
```

Use the Lab 4 environment: `source ~/ros2_ws/src/aau-msc-robotics-labs/lab_04/.venv/bin/activate`.

## Step 1: Change the reward

Train three Hoppers, each with one reward weight changed:

```bash
python train_hopper.py --name fast --forward-weight 3.0
python train_hopper.py --name gentle --ctrl-cost 0.1
python train_hopper.py --name no_health --healthy-reward 0.0
```

**Check.** Watch each one with `play_hopper.py --name <name>` and compare them with `hopper`. In TensorBoard
the four runs show side by side. Describe how each gait differs and which reward term causes it.

## Step 2: Exploration

PPO keeps exploring by adding entropy to its loss, weighted by `ent_coef`. Add an option
`--ent-coef` to `trainer.py` that sets it, with `0.0` as its default. Train with `0.01` and with `0.05`.

**Check.** Compare `rollout/ep_rew_mean` and `train/entropy_loss` of the two runs and `hopper` in TensorBoard, and
explain the difference.

## Step 3: Another robot

Choose one robot from the table in the README (Other robots in Gymnasium), other than the Hopper and
the Walker2d. Write `train_<robot>.py` and `play_<robot>.py` the way `train_walker2d.py` and
`play_walker2d.py` are written, and train it. `trainer.py` must pass only the reward options your robot
accepts; the table lists them.

**Check.** `python play_<robot>.py` shows your robot doing its task. Compare it with the Hopper and
the Walker2d in a table:

| Robot | Observations | Actions | Training steps | Training time | Final `ep_rew_mean` | Final `ep_len_mean` |
|-------|--------------|---------|----------------|---------------|---------------------|---------------------|

Explain why the results differ between the robots.
