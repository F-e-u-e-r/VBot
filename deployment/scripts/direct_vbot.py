#!/usr/bin/env python3
import os
import sys
import subprocess

os.chdir('/home/ec2-user/VBot')
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.executable}")

# Try to run with flask
try:
    from flask.cli import FlaskGroup
    print("Flask module found!")
except ImportError:
    print("Flask module not found")

try:
    import gunicorn
    print("Gunicorn module found!")
except ImportError:
    print("Gunicorn module not found")

# Run the commands directly
cmd = 'cd /home/ec2-user/VBot && python3 -m flask db upgrade && python3 -m gunicorn.app.wsgiapp --bind 0.0.0.0:5001 --workers 4 --timeout 120 "app:create_app(\'production\')"'
print(f"Running command: {cmd}")
subprocess.call(cmd, shell=True)
