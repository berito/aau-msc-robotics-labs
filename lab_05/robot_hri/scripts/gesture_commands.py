#!/usr/bin/env python3
"""
Recognize hand gestures on the webcam and publish them as commands.

Uses the MediaPipe hand landmarker. A finger is raised when its tip is farther from the wrist than its
middle joint; the thumb, when its tip is farther from the palm than its last joint. The number of
raised fingers gives the command:

    0  fist        stop
    1              forward
    2              back
    3              left
    4              right
    5  open palm   stop

A command is published when it is held for hold_frames frames and differs from the last one.

Topics:
    command (std_msgs/String)   out: forward, back, left, right or stop

Parameters:
    camera        webcam index, or the path of a video file ("0")
    model_path    hand landmarker model (models/hand_landmarker.task in this package)
    hold_frames   frames a gesture must be held before it is published (5)
    show          show the camera image with the landmarks and the command (true)

Usage:
    ros2 run robot_hri gesture_commands.py
    ros2 run robot_hri gesture_commands.py --ros-args -p camera:=1
"""

import math
import os

import cv2
import mediapipe as mp
import rclpy
from ament_index_python.packages import get_package_share_directory
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from std_msgs.msg import String

FRAME_RATE_HZ = 30.0
FINGER_COMMANDS = ["stop", "forward", "back", "left", "right", "stop"]

# Landmark indices, see the MediaPipe hand landmarker documentation
WRIST = 0
THUMB_IP, THUMB_TIP = 3, 4
MIDDLE_MCP = 9
FINGER_PIPS = [6, 10, 14, 18]
FINGER_TIPS = [8, 12, 16, 20]


def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def count_fingers(hand):
    wrist = hand[WRIST]
    count = sum(distance(hand[tip], wrist) > distance(hand[pip], wrist)
                for tip, pip in zip(FINGER_TIPS, FINGER_PIPS))
    palm = hand[MIDDLE_MCP]
    if distance(hand[THUMB_TIP], palm) > distance(hand[THUMB_IP], palm):
        count += 1
    return count


class GestureCommands(Node):
    def __init__(self):
        super().__init__("gesture_commands")
        default_model = os.path.join(get_package_share_directory("robot_hri"), "models",
                                     "hand_landmarker.task")
        self.declare_parameter("camera", "0")
        self.declare_parameter("model_path", default_model)
        self.declare_parameter("hold_frames", 5)
        self.declare_parameter("show", True)

        camera = self.get_parameter("camera").value
        self.capture = cv2.VideoCapture(int(camera) if camera.isdigit() else camera)
        if not self.capture.isOpened():
            raise RuntimeError(f"Cannot open camera {camera}")

        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self.get_parameter("model_path").value),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self.hold_frames = self.get_parameter("hold_frames").value
        self.show = self.get_parameter("show").value

        self.candidate = None
        self.candidate_frames = 0
        self.published = None
        self.timestamp_ms = 0

        self.command_pub = self.create_publisher(String, "command", 10)
        self.create_timer(1.0 / FRAME_RATE_HZ, self.process_frame)
        self.get_logger().info("Show your hand to the camera")

    def process_frame(self):
        ok, frame = self.capture.read()
        if not ok:
            return
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # VIDEO mode needs increasing timestamps
        self.timestamp_ms += int(1000 / FRAME_RATE_HZ)
        result = self.landmarker.detect_for_video(
            mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), self.timestamp_ms)

        command = None
        if result.hand_landmarks:
            hand = result.hand_landmarks[0]
            fingers = count_fingers(hand)
            command = FINGER_COMMANDS[fingers]
            if self.show:
                self.draw(frame, hand, f"{fingers} fingers: {command}")
        self.update(command)

        if self.show:
            cv2.imshow("gestures", frame)
            cv2.waitKey(1)

    def update(self, command):
        if command is None or command != self.candidate:
            self.candidate = command
            self.candidate_frames = 1
            return
        self.candidate_frames += 1
        if self.candidate_frames >= self.hold_frames and command != self.published:
            self.command_pub.publish(String(data=command))
            self.published = command
            self.get_logger().info(f"Gesture: {command}")

    @staticmethod
    def draw(frame, hand, label):
        height, width = frame.shape[:2]
        for point in hand:
            cv2.circle(frame, (int(point.x * width), int(point.y * height)), 4, (0, 255, 0), -1)
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

    def close(self):
        self.capture.release()
        self.landmarker.close()
        cv2.destroyAllWindows()


def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = GestureCommands()
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
