#!/usr/bin/env python3
"""
Recognize spoken commands from the microphone and publish them.

Uses Vosk offline, limited to the command words. If a sentence holds several, the last one is
published.

Topics:
    command (std_msgs/String)   out: forward, back, left, right or stop

Parameters:
    model_path   Vosk model folder (models/vosk-model-small-en-us-0.15 in this package)
    device       microphone, as a sounddevice index or name; empty for the default microphone

Usage:
    ros2 run robot_hri speech_commands.py
    python3 -m sounddevice      # list the microphones
"""

import json
import os
import queue

import rclpy
import sounddevice as sd
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from std_msgs.msg import String
from vosk import KaldiRecognizer, Model, SetLogLevel

WORDS = ["forward", "back", "left", "right", "stop"]
SAMPLE_RATE = 16000
BLOCK_SIZE = 4000


class SpeechCommands(Node):
    def __init__(self):
        super().__init__("speech_commands")
        default_model = os.path.join(get_package_share_directory("robot_hri"), "models",
                                     "vosk-model-small-en-us-0.15")
        self.declare_parameter("model_path", default_model)
        self.declare_parameter("device", "")

        SetLogLevel(-1)
        model = Model(self.get_parameter("model_path").value)
        # [unk] catches the words outside the list
        self.recognizer = KaldiRecognizer(model, SAMPLE_RATE, json.dumps(WORDS + ["[unk]"]))

        device = self.get_parameter("device").value
        device = int(device) if device.isdigit() else (device or None)
        self.audio = queue.Queue()
        self.stream = sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, dtype="int16",
                                        channels=1, device=device, callback=self.on_audio)
        self.stream.start()

        self.command_pub = self.create_publisher(String, "command", 10)
        self.create_timer(0.05, self.recognize)
        self.get_logger().info(f"Listening for: {', '.join(WORDS)}")

    def on_audio(self, data, frames, time, status):
        self.audio.put(bytes(data))

    def recognize(self):
        while not self.audio.empty():
            if not self.recognizer.AcceptWaveform(self.audio.get()):
                continue
            text = json.loads(self.recognizer.Result())["text"]
            commands = [word for word in text.split() if word in WORDS]
            if commands:
                self.get_logger().info(f"Heard: {' '.join(commands)}")
                self.command_pub.publish(String(data=commands[-1]))

    def close(self):
        self.stream.stop()
        self.stream.close()


def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = SpeechCommands()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
