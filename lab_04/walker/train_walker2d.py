"""
Train Walker2d, a two-legged robot, to walk forward.

Usage:
    python train_walker2d.py
    python train_walker2d.py --algo sac --timesteps 300000
    python train_walker2d.py --watch --timesteps 20000
"""

from trainer import main

if __name__ == "__main__":
    main("Walker2d-v5", "walker2d", __doc__)
