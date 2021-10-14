#!/usr/bin/env python3

"""
Simple stub that calls the 'real' deploy.py in the git submodule without an
additional path prefix. Passes along any parameters without modification.
For usage, optional arguments, syntax, etc. please refer to the RoboLab Docs
which are accessible at https://robolab.inf.tu-dresden.de.

This module: https://bitbucket.org/tudrobolab/robolab-template
The submodule: https://bitbucket.org/tudrobolab/robolab-deploy

Part of the RoboLab Project
Systems Engineering Group, Faculty of Computer Science, TU Dresden
Copyright (c) 2017-2019 by Lutz Thies, Samuel Knobloch
Released under the MIT License
"""

import subprocess
import sys

# Store path to executable
DEPLOY_EXECUTABLE = "./robolab-deploy/deploy.py"
# Windows-Fix: Get the full executable path, windows can't handle our shebang
PYTHON_EXECUTABLE = sys.executable

# Check if the "robolab-deploy" submodule is available
try:
    with open(DEPLOY_EXECUTABLE) as f:
        f.close()
except FileNotFoundError:
    print("You forgot to use the --recursive flag while cloning this repository!")
    print("Please run: git submodule update --init --recursive")
except IOError:
    print("Submodule found but not accessible; please check for correct permissions!")

subprocess.call([PYTHON_EXECUTABLE, DEPLOY_EXECUTABLE] + sys.argv[1:])
