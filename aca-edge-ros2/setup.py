from setuptools import find_packages, setup


package_name = "aca_edge_ros2"

setup(
    name=package_name,
    version="1.3.2",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],
    zip_safe=True,
    maintainer="ghalangwh.official",
    maintainer_email="ghalangwh.official@gmail.com",
    description="ACA edge ROS 2 stack for telemetry bridging and safety gating.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "telemetry_bridge = telemetry_bridge.node:main",
            "safety_gate = safety_gate.node:main",
        ],
    },
)

