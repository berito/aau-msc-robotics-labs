#!/usr/bin/env python3
"""
Drive the robot from word commands: forward, back, left, right and stop.

The last command is sent as a velocity at 10 Hz until the next one arrives.

Topics:
    command (std_msgs/String)   in, from speech_commands.py or gesture_commands.py
    cmd_vel (geometry_msgs/Twist)   out

Parameters:
    linear_speed    forward and backward speed, m/s (0.2)
    angular_speed   turning speed, rad/s (0.5)

Usage:
    ros2 run robot_hri command_driver.py
    ros2 topic pub --once /command std_msgs/msg/String "{data: forward}"
"""

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from std_msgs.msg import String

RATE_HZ = 10.0

# (linear, angular) direction of each command
COMMANDS = {
    "forward": (1.0, 0.0),
    "back": (-1.0, 0.0),
    "left": (0.0, 1.0),
    "right": (0.0, -1.0),
    "stop": (0.0, 0.0),
}


class CommandDriver(Node):
    def __init__(self):
        super().__init__("command_driver")
        self.declare_parameter("linear_speed", 0.2)
        self.declare_parameter("angular_speed", 0.5)
        self.command = "stop"

        self.create_subscription(String, "command", self.on_command, 10)
        self.cmd_pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.create_timer(1.0 / RATE_HZ, self.publish_velocity)
        self.get_logger().info(f"Waiting for commands: {', '.join(COMMANDS)}")

    def on_command(self, msg):
        command = msg.data.strip().lower()
        if command not in COMMANDS:
            self.get_logger().warn(f"Unknown command: {msg.data}")
            return
        if command != self.command:
            self.get_logger().info(f"Command: {command}")
        self.command = command

    def publish_velocity(self):
        linear, angular = COMMANDS[self.command]
        twist = Twist()
        twist.linear.x = linear * self.get_parameter("linear_speed").value
        twist.angular.z = angular * self.get_parameter("angular_speed").value
        self.cmd_pub.publish(twist)

    def stop(self):
        self.cmd_pub.publish(Twist())


def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = CommandDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
