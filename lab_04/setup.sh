#!/usr/bin/env bash
# Create .venv, install PyTorch and requirements.txt. Safe to run again.
# Usage: ./setup.sh          PyTorch CPU build
#        ./setup.sh --gpu    PyTorch CUDA build, for an NVIDIA GPU
set -euo pipefail

TORCH_INDEX=https://download.pytorch.org/whl/cpu
BUILD="CPU build"
CUDA=False
if [ "${1:-}" = "--gpu" ]; then
    TORCH_INDEX=https://download.pytorch.org/whl/cu130
    BUILD="CUDA build"
    CUDA=True
fi

cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
    echo "Creating the virtual environment in .venv"
    python3 -m venv .venv
fi
touch .venv/COLCON_IGNORE

.venv/bin/pip install --quiet --upgrade pip
INSTALLED=$(.venv/bin/python -c "import torch; print(torch.version.cuda is not None)" 2>/dev/null || echo none)
if [ "$INSTALLED" != none ] && [ "$INSTALLED" != "$CUDA" ]; then
    .venv/bin/pip uninstall --yes torch
fi
echo "Installing PyTorch ($BUILD)"
.venv/bin/pip install --progress-bar on torch --index-url "$TORCH_INDEX"
echo "Installing the other Python packages"
.venv/bin/pip install --progress-bar on -r requirements.txt

.venv/bin/python -c "import gymnasium, mujoco, stable_baselines3; print('gymnasium', gymnasium.__version__, 'mujoco', mujoco.__version__, 'stable-baselines3', stable_baselines3.__version__)"
.venv/bin/python -c "import torch; print('torch', torch.__version__, 'CUDA available:', torch.cuda.is_available())"
echo "Done. In every terminal: source $(pwd)/.venv/bin/activate"
