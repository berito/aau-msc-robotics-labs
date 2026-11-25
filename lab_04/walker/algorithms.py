"""The Stable-Baselines3 algorithms and their settings."""

import torch
from stable_baselines3 import A2C, PPO, SAC, TD3

ALGORITHMS = {
    "ppo": (PPO, dict(
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        learning_rate=3e-4,
        ent_coef=0.0,
        clip_range=0.2,
        policy_kwargs=dict(activation_fn=torch.nn.Tanh, net_arch=dict(pi=[64, 64], vf=[64, 64])),
    )),
    "a2c": (A2C, dict()),
    "sac": (SAC, dict(learning_starts=10_000)),
    "td3": (TD3, dict(learning_starts=10_000)),
}

# Trained on normalized observations and rewards
NORMALIZED = {"ppo", "a2c"}


def model_name(robot, algo, name):
    if name:
        return name
    return robot if algo == "ppo" else f"{robot}_{algo}"
