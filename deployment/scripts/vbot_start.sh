#!/bin/bash
   
# Print environment information for debugging
echo "Starting VBot service at $(date)"
echo "PATH=$PATH"
   
# Change to project directory
cd /home/ec2-user/VBot
   
# Run the application
flask db upgrade && gunicorn --bind 0.0.0.0:5001 --workers 4 --timeout 120 'app:create_app("production")'
