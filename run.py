#!/usr/bin/env python3
"""
Application runner script with enhanced error handling and port management.
This script starts the Flask application with improved stability for development.
"""
import os
import sys
import socket
import logging
import time
import argparse
import signal
from subprocess import Popen
from datetime import datetime
from app import create_app
from models import db
from models.user import User
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run")

def check_port_in_use(port, host='127.0.0.1'):
    """
    Check if a port is in use.
    
    Args:
        port (int): Port number to check
        host (str): Host address to check
        
    Returns:
        bool: True if port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True

def kill_process_on_port(port, host='127.0.0.1'):
    """
    Attempt to kill any process using the specified port.
    
    Args:
        port (int): Port number
        host (str): Host address
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # This is platform specific and works better on Linux/Mac
        if sys.platform.startswith('win'):
            # Windows: use netstat and taskkill
            import subprocess
            result = subprocess.run(f"netstat -ano | findstr :{port}", shell=True, capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                            logger.info(f"Killed process {pid} using port {port}")
                        except Exception as e:
                            logger.error(f"Failed to kill process {pid}: {e}")
        else:
            # Unix: use lsof and kill
            import subprocess
            result = subprocess.run(f"lsof -i :{port} -t", shell=True, capture_output=True, text=True)
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid.strip():
                    try:
                        subprocess.run(f"kill -9 {pid}", shell=True)
                        logger.info(f"Killed process {pid} using port {port}")
                    except Exception as e:
                        logger.error(f"Failed to kill process {pid}: {e}")
        return True
    except Exception as e:
        logger.error(f"Error killing process on port {port}: {e}")
        return False

def start_app(port=5001, debug=True, auto_restart=True, max_retries=3):
    """
    Start the Flask application with error handling and auto-restart.
    
    Args:
        port (int): Port to run the application on
        debug (bool): Whether to run in debug mode
        auto_restart (bool): Whether to automatically restart on crash
        max_retries (int): Maximum number of restart attempts
    """
    # Check if port is already in use
    if check_port_in_use(port):
        logger.warning(f"Port {port} is already in use")
        try:
            user_input = input(f"Port {port} is already in use. Kill the process? (y/n): ")
            if user_input.lower().startswith('y'):
                if kill_process_on_port(port):
                    logger.info(f"Successfully freed port {port}")
                else:
                    logger.error(f"Failed to free port {port}. Please check manually.")
                    sys.exit(1)
            else:
                alternative_port = port + 1
                while check_port_in_use(alternative_port) and alternative_port < port + 10:
                    alternative_port += 1
                
                if alternative_port < port + 10:
                    user_input = input(f"Would you like to use port {alternative_port} instead? (y/n): ")
                    if user_input.lower().startswith('y'):
                        port = alternative_port
                    else:
                        logger.info("Exiting as requested.")
                        sys.exit(1)
                else:
                    logger.error("Could not find an available port. Please free a port manually.")
                    sys.exit(1)
        except KeyboardInterrupt:
            logger.info("Operation cancelled by user")
            sys.exit(1)
    
    # Import the Flask app here to avoid circular imports
    try:
        from app import app
        logger.info(f"Starting Flask application on port {port} with debug={debug}")
        
        # Register signal handlers for clean shutdown
        def signal_handler(sig, frame):
            logger.info("Received signal to shut down")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if auto_restart:
            retries = 0
            while retries < max_retries:
                try:
                    app.run(host='0.0.0.0', port=port, debug=debug)
                    break  # If app.run() exits normally, break the loop
                except Exception as e:
                    retries += 1
                    logger.error(f"Application crashed: {e}")
                    if retries < max_retries:
                        logger.info(f"Restarting in 2 seconds... (Attempt {retries}/{max_retries})")
                        time.sleep(2)
                    else:
                        logger.error("Maximum restart attempts reached. Giving up.")
                        raise
        else:
            # Run without auto-restart
            app.run(host='0.0.0.0', port=port, debug=debug)
            
    except ImportError as e:
        logger.error(f"Failed to import Flask application: {e}")
        logger.error("Make sure you're running this script from the correct directory")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Run the Flask application')
    parser.add_argument('--port', type=int, default=5001, 
                        help='Port to run the application on (default: 5001)')
    parser.add_argument('--debug', action='store_true', default=True,
                        help='Run the application in debug mode')
    parser.add_argument('--no-auto-restart', action='store_true',
                        help='Disable automatic restart on crash')
    parser.add_argument('--max-retries', type=int, default=3,
                        help='Maximum number of restart attempts (default: 3)')
    
    return parser.parse_args()

def main():
    """Main entry point for the application"""
    start_time = datetime.now()
    args = parse_arguments()
    
    logger.info(f"Starting application at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        start_app(
            port=args.port, 
            debug=args.debug, 
            auto_restart=not args.no_auto_restart,
            max_retries=args.max_retries
        )
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
    finally:
        end_time = datetime.now()
        runtime = end_time - start_time
        logger.info(f"Application stopped at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Total runtime: {runtime}")

if __name__ == '__main__':
    main() 