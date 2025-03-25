   #!/bin/bash
   echo "==== Environment Debugging ===="
   echo "Current user: $(whoami)"
   echo "Current directory: $(pwd)"
   echo "PATH: $PATH"
   echo "Python version: $(python3 --version 2>&1)"
   echo "Python3 location: $(which python3 2>&1)"
   echo "=== Python module search ==="
   python3 -c "import sys; print(sys.path)"
   echo "=== Looking for flask/gunicorn modules ==="
   python3 -c "import importlib.util; print('Flask found:', importlib.util.find_spec('flask') is not None)" 2>/dev/null || echo "Error checking for flask"
   python3 -c "import importlib.util; print('Gunicorn found:', importlib.util.find_spec('gunicorn') is not None)" 2>/dev/null || echo "Error checking for gunicorn"
   echo "=== Process check ==="
   ps aux | grep -E "(flask|gunicorn)" | grep -v grep
