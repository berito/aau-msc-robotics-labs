from glob import glob

from setuptools import setup

package_name = 'fr3_pick_place'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/urdf', glob('urdf/*.xacro')),
        ('share/' + package_name + '/worlds', glob('worlds/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    description='Pick-and-drop task for the Franka FR3 with MoveIt 2 on simulated hardware.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'pick_place = fr3_pick_place.pick_place:main',
            'add_scene = fr3_pick_place.pick_place:add_scene',
        ],
    },
)
