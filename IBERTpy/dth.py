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
            result = conn.open_shell('DTH_Flashy.py --fpga tcds --batch --command loadFPGA --start_adr s300')
            print(f"Command output:\n{result.stdout}")
            print()
    except Exception as e:
        print(f"Error running DTH_Flashy.py: {str(e)}")


def run_vivado(hostname='local', sleep_time=0):
    """Run Vivado in batch mode with eyescan.tcl after sourcing settings"""
    try:

        # Create command to source settings and run Vivado
        cmd = [
            'bash', 
            '-c', 
            ' source /home/tools/Xilinx/Vivado_Lab/2024.1/settings64.sh &&  vivado_lab -mode gui -source dth_eyescan.tcl'
        ]
        
        print("Starting Vivado...")
        subprocess.run(cmd, check=True)


    except Exception as e:
        print(f"Error running Vivado: {str(e)}")

def wait_for_pdf(timeout=500, interval=5):
    """Wait for PDF file to appear in current directory"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        pdf_files = glob.glob("*.pdf")
        if pdf_files:
            print(f"Found PDF file: {pdf_files[0]}")
            return True
        time.sleep(interval)
    return False

def main():
    """Main function to run Vivado and DTH_Flashy in sequence"""
    # Create and start Vivado thread
    vivado_thread = Thread(target=run_vivado)
    vivado_thread.daemon = True
    vivado_thread.start()
    
    # Wait for PDF generation
    if wait_for_pdf():
        # Prompt user to continue
        input("PDF file generated. Press Enter to continue with DTH_Flashy...")
        # Run DTH_Flashy
        run_dth_flashy('dth', username='DTH', password='userdth')
    else:
        print("Timeout waiting for PDF file generation")

    # Wait for Vivado thread to complete
    vivado_thread.join()

if __name__ == "__main__":
    main()
