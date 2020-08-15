#!/usr/bin/env python
import io
import re
from setuptools import setup, find_packages
import sys

with io.open("./stream_saver/__init__.py", encoding="utf8") as version_file:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")


with io.open("README.md", encoding="utf8") as readme:
    long_description = readme.read()


setup(
    name="stream_saver",
    version=version,
    description="A tool to automatically download streams live and avoid muted VODs",
    long_description=long_description,
    author="Zachary Joswick",
    author_email="<zjoswick@gmail.com>",
    license="MIT license",
    packages=find_packages(
        exclude=["docs", "tests", "windows", "macOS", "linux", "iOS", "android", "django"]
    ),
    classifiers=["Development Status :: 1 - Planning", "License :: OSI Approved :: MIT license"],
    install_requires=[],
    options={
        "app": {"formal_name": "Stream Saver", "bundle": "com.zacharyjoswick"},
        # Desktop/laptop deployments
        "macos": {"app_requires": []},
        "linux": {"app_requires": []},
        "windows": {"app_requires": []},
        # Mobile deployments
        "ios": {"app_requires": []},
        "android": {"app_requires": []},
        # Web deployments
        "django": {"app_requires": []},
    },
)
