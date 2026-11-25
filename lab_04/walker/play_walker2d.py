"""
Watch a trained Walker2d in the MuJoCo viewer and print the return of each episode.

Usage:
    python play_walker2d.py
    python play_walker2d.py --algo sac
"""

from player import main

if __name__ == "__main__":
    main("Walker2d-v5", "walker2d", __doc__)
