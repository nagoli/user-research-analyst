# pip install -e .

from setuptools import setup, find_packages

setup(
    name="user-research-analyst",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pandas",
        # add other dependencies here
    ],
) 