# skel/py3

This is a skeleton for a python3 CLI app. It uses a virtualenv to encapsulate
any dependencies, and sets up a nice logger so you can log debug information
right from the start.

The makefile is "self-documenting", so "make help" will show you the options.

# Installation

To set up the virtualenv, run `make`.

To clean up local virtualenv, run `make clean`.

# Usage

To run the program from the virtualenv, run:
```
./venv/bin/python foo.py
```
