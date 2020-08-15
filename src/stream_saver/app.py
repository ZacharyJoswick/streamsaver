"""
A tool to automatically download streams live and avoid muted VODs
"""

import os
import code
from os.path import dirname, abspath


def main():
    # This should start and launch your app!
    print("Hello World")
    print(os.path.realpath(__file__))

    print(f"Appdir is: {os.getenv('APPDIR', 'APPDIR not found')}")

    d = dirname(abspath(__file__))
    print(f"contents of directory: {os.listdir(d)}")
    code.InteractiveConsole(locals=globals()).interact()
