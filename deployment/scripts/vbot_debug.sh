#!/bin/bash

# Log file for debugging
LOGFILE="/home/ec2-user/vbot_debug.log"

# Clear log file
echo "=== VBot Debug Log $(date) ===" > $LOGFILE

# Check if Python 3.10 exists
echo "Checking for Python 3.10..." >> $LOGFILE
if [ -f /usr/local/bin/python3.10 ]; then
    echo "Found Python 3.10 at /usr/local/bin/python3.10" >> $LOGFILE
else
    echo "ERROR: Python 3.10 not found at /usr/local/bin/python3.10" >> $LOGFILE
    ls -la /usr/local/bin/python* >> $LOGFILE 2>&1
fi

# Check if gunicorn exists
echo "Checking for gunicorn..." >> $LOGFILE
if [ -f /usr/local/bin/gunicorn ]; then
    echo "Found gunicorn at /usr/local/bin/gunicorn" >> $LOGFILE
else
    echo "ERROR: gunicorn not found at /usr/local/bin/gunicorn" >> $LOGFILE
    ls -la /usr/local/bin/gunicorn* >> $LOGFILE 2>&1
fi

# Try to find them using find
echo "Searching for Python 3.10..." >> $LOGFILE
find /usr -name "python3.10" -type f 2>/dev/null >> $LOGFILE

echo "Searching for gunicorn..." >> $LOGFILE
find /usr -name "gunicorn" -type f 2>/dev/null >> $LOGFILE

# Try to start with the command
echo "Attempting to start VBot..." >> $LOGFILE
cd /home/ec2-user/VBot
/usr/local/bin/python3.10 /usr/local/bin/gunicorn --bind 0.0.0.0:5001 --workers 4 --timeout 120 app:create_app\(\"production\"\) >> $LOGFILE 2>&1

echo "Script completed with exit code $?" >> $LOGFILE
