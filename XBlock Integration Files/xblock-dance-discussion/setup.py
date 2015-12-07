from setuptools import setup
import os

def package_data(pkg, root):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for dirname, _, files in os.walk(os.path.join(pkg, root)):
        for fname in files:
            data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}

setup(
    name='Discussion XBlock for DANCE',
    version='1.1',
    description='Prototype for the discussion XBlock',
    py_modules=['discussion_dance'],
    install_requires=['XBlock'],
    entry_points={
        'xblock.v1': [
            'discussion_dance = discussion_dance:DiscussionDance',
        ]
    }
)