#!/usr/bin/env bash
# Create .venv (with access to the ROS 2 packages), install requirements.txt and download the
# speech and hand models into robot_hri/models/. Safe to run again.
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
    echo "Creating the virtual environment in .venv"
    python3 -m venv --system-site-packages .venv
fi
# keep colcon out of the venv
touch .venv/COLCON_IGNORE

.venv/bin/pip install --quiet --upgrade pip
echo "Installing the Python packages"
.venv/bin/pip install --progress-bar on -r requirements.txt

echo "Downloading the models into robot_hri/models/"
.venv/bin/python - <<'PYTHON'
import os
import urllib.request
import zipfile

models = "robot_hri/models"
os.makedirs(models, exist_ok=True)
vosk = "vosk-model-small-en-us-0.15"
if not os.path.isdir(os.path.join(models, vosk)):
    archive = os.path.join(models, vosk + ".zip")
    urllib.request.urlretrieve(f"https://alphacephei.com/vosk/models/{vosk}.zip", archive)
    with zipfile.ZipFile(archive) as z:
        z.extractall(models)
    os.remove(archive)
print(f"  {models}/{vosk}")

hand = os.path.join(models, "hand_landmarker.task")
if not os.path.isfile(hand):
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/"
        "hand_landmarker.task", hand)
print(f"  {hand}")
PYTHON

.venv/bin/python -c "import vosk, mediapipe; print('vosk and mediapipe', mediapipe.__version__, 'work')"
echo "Done. In every terminal: source $(pwd)/.venv/bin/activate"
