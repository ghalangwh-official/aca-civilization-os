from __future__ import annotations

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    robot_id = LaunchConfiguration("robot_id")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "robot_id",
                default_value="ROBOT-001",
                description="Stable robot identifier used by telemetry_bridge",
            ),
            Node(
                package="aca-edge-ros2",
                executable="telemetry_bridge",
                name="telemetry_bridge",
                output="screen",
                parameters=[{"robot_id": robot_id}],
            ),
        ]
    )

