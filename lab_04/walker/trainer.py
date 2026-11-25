"""Training used by the train_<robot>.py scripts. Saves the policy in models/ and the curves in runs/."""

import argparse
import os

import numpy as np
import torch
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, VecNormalize

from algorithms import ALGORITHMS, NORMALIZED, model_name

HERE = os.path.dirname(os.path.abspath(__file__))


class ShowGrid(BaseCallback):
    """Shows all environments in one window, one tile each."""

    def _on_step(self):
        self.training_env.render(mode="human")
        return True


def parse_args(doc):
    parser = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--algo", choices=ALGORITHMS, default="ppo", help="algorithm (ppo)")
    parser.add_argument("--timesteps", type=int, default=1_000_000, help="training steps (1000000)")
    parser.add_argument("--name", help="name of the saved model (<robot> or <robot>_<algo>)")
    parser.add_argument("--forward-weight", type=float, default=1.0, help="weight of the forward speed (1.0)")
    parser.add_argument("--healthy-reward", type=float, default=1.0, help="reward per step while upright (1.0)")
    parser.add_argument("--ctrl-cost", type=float, default=0.001, help="weight of the torque cost (0.001)")
    parser.add_argument("--watch", action="store_true", help="show the robots while training; nothing is saved")
    parser.add_argument("--envs", type=int, default=1, help="environments run in parallel (1)")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu", help="device for the networks (cpu)")
    return parser.parse_args()


def make_env(env_id, args):
    env_kwargs = dict(forward_reward_weight=args.forward_weight,
                      healthy_reward=args.healthy_reward,
                      ctrl_cost_weight=args.ctrl_cost)
    if args.watch and args.envs == 1:
        env_kwargs["render_mode"] = "human"
    elif args.watch:
        env_kwargs.update(render_mode="rgb_array", width=320, height=320)

    vec_env_cls = SubprocVecEnv if args.envs > 1 else DummyVecEnv
    env = make_vec_env(env_id, n_envs=args.envs, env_kwargs=env_kwargs, vec_env_cls=vec_env_cls)
    if args.algo in NORMALIZED:
        env = VecNormalize(env)
    return env


def make_model(env, args):
    algorithm, settings = ALGORITHMS[args.algo]
    settings = dict(settings)
    if args.algo == "td3":
        n_actions = env.action_space.shape[0]
        settings["action_noise"] = NormalActionNoise(np.zeros(n_actions), 0.1 * np.ones(n_actions))

    log_dir = None if args.watch else os.path.join(HERE, "runs")
    return algorithm("MlpPolicy", env, tensorboard_log=log_dir, device=args.device, verbose=1, **settings)


def main(env_id, robot, doc=None):
    args = parse_args(doc)
    if args.device == "cuda" and not torch.cuda.is_available():
        raise SystemExit("PyTorch has no CUDA support. Install it with: ./setup.sh --gpu")

    name = model_name(robot, args.algo, args.name)
    env = make_env(env_id, args)
    model = make_model(env, args)
    callback = ShowGrid() if args.watch and args.envs > 1 else None
    model.learn(total_timesteps=args.timesteps, tb_log_name=name, callback=callback)

    if not args.watch:
        os.makedirs(os.path.join(HERE, "models"), exist_ok=True)
        model.save(os.path.join(HERE, "models", name))
        if args.algo in NORMALIZED:
            env.save(os.path.join(HERE, "models", f"{name}_vecnormalize.pkl"))
        print(f"Saved models/{name}")
    env.close()
