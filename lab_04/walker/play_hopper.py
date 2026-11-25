"""
Watch a trained Hopper in the MuJoCo viewer and print the return of each episode.

Usage:
    python play_hopper.py
    python play_hopper.py --algo sac
    python play_hopper.py --name my_reward --episodes 5
"""

from player import main

if __name__ == "__main__":
    main("Hopper-v5", "hopper", __doc__)
