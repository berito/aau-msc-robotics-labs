"""Playback used by the play_<robot>.py scripts."""

import argparse
import os

from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize

from algorithms import ALGORITHMS, NORMALIZED, model_name

HERE = os.path.dirname(os.path.abspath(__file__))


def parse_args(doc):
    parser = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--algo", choices=ALGORITHMS, default="ppo", help="algorithm of the model (ppo)")
    parser.add_argument("--name", help="name of the saved model (<robot> or <robot>_<algo>)")
    parser.add_argument("--episodes", type=int, default=3, help="episodes to play (3)")
    parser.add_argument("--no-render", action="store_true", help="run without the viewer")
    return parser.parse_args()


def main(env_id, robot, doc=None):
    args = parse_args(doc)
    name = model_name(robot, args.algo, args.name)
    path = os.path.join(HERE, "models", name)

    render_mode = None if args.no_render else "human"
    env = make_vec_env(env_id, env_kwargs=dict(render_mode=render_mode))
    if args.algo in NORMALIZED:
        env = VecNormalize.load(f"{path}_vecnormalize.pkl", env)
        env.training = False
        env.norm_reward = False

    algorithm, _ = ALGORITHMS[args.algo]
    model = algorithm.load(path, env=env)

    obs = env.reset()
    for episode in range(1, args.episodes + 1):
        done = [False]
        while not done[0]:
            action, _ = model.predict(obs, deterministic=True)
            obs, _, done, info = env.step(action)
        result = info[0]["episode"]
        print(f"Episode {episode}: return {result['r']:.0f}, {result['l']} steps")
    env.close()
