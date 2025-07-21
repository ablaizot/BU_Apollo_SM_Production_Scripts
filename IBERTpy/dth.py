from fabric import Connection
import time
import socket
import subprocess
import os
from threading import Thread
import glob
import csv
from getpass import getpass

def run_dth_flashy(hostname, username='root', password=None):
    """
    Run DTH_Flashy.py --fpga tcds on remote machine
    
    Args:
        hostname (str): The hostname or IP address to connect to
        username (str): SSH username (defaults to 'root')
        password (str): SSH password (optional if using key-based auth)
    """
    try:
        with Connection(
            host=hostname,
            user=username,
            connect_kwargs={"password": password}
        ) as conn:
            print("Running DTH_Flashy.py --fpga tcds...")
            result = conn.run('python3 DTH_Flashy.py --fpga tcds', hide=False)
            print(f"Command output:\n{result.stdout}")
            
    except Exception as e:
        print(f"Error running DTH_Flashy.py: {str(e)}")

if __name__ == "__main__":
    
    # Run DTH_Flashy
    run_dth_flashy('dth',username='DTH' password='userdth')
