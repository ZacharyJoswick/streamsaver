Stream Saver
============

A tool to automatically download streams live and avoid muted VODs

Goals

 - Easy to use twitch (and other stream) downloader system
 - Leverage streamlink and ffmpeg
 - Cross platform for windows and linux (maybe arm / bsd / others)

## Building

This project uses poetry for dependency management and briefcase for cross platform builds. To get started setup a python 3.8 environment (through pyenv, conda, or some other method). Then you will need to run the following:
1. `poetry install` to setup all dependencies
2. `poetry run briefcase create` to setup the build environment
3. `poetry run briefcase build` to create the completed executable
4. `poetry run briefcase package` to create the installer (if applicable)

A platform's installer can only be created on that platform, so 