from __future__ import annotations

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    profile_path = LaunchConfiguration("profile_path")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "profile_path",
                default_value="config/robot_profile.yaml",
                description="Robot profile file with hard safety limits",
            ),
            Node(
                package="aca-edge-ros2",
                executable="safety_gate",
                name="safety_gate",
                output="screen",
                parameters=[{"profile_path": profile_path}],
            ),
        ]
    )

