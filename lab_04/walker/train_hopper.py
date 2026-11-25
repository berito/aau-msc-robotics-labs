"""
Train the Hopper, a one-legged robot, to hop forward.

Usage:
    python train_hopper.py
    python train_hopper.py --algo sac --timesteps 300000
    python train_hopper.py --timesteps 200000 --name short_run
    python train_hopper.py --forward-weight 2.0 --ctrl-cost 0.01 --name my_reward
    python train_hopper.py --watch --timesteps 20000
"""

from trainer import main

if __name__ == "__main__":
    main("Hopper-v5", "hopper", __doc__)
