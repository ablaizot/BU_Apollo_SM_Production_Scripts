from fabric import Connection
import time
import socket
import subprocess
import os
from threading import Thread
import glob
import csv
from getpass import getpass
import psutil
from sm_mgt_eyescan import CLOCK_DIR
from sm_mgt_eyescan import valid_connection
import time
import paramiko

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
            print("Running DTH_Flashy.py --fpga tcds, Wait 3 minutes and press enter to continue")
            result = conn.run('ablaizot/dth.sh')
            conn.run('tcds2_dth_driver id')
            conn.close()
    except Exception as e:
        print(f"Error running DTH_Flashy.py: {str(e)}")
        print("Reloading Driver")
        conn.run("tcds2_dth_driver reload")
        time.sleep(240)
        conn.run("tcds2_dth_driver links init")

        conn.close()


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

def blackplane_clocks(hostname, username='root', password=None, ):
    with Connection(
        host=hostname,
        user=username,
        connect_kwargs={"password": password}
    ) as conn:
        
        try:

            print("Programming clocks...")
            conn.run(f'{CLOCK_DIR}clock_sync_320M_LHC {CLOCK_DIR}CONFIGS/CONFIG.toml')

            print("Switch to backplane clocks in BUtool:")
            conn.run('echo \'w SERV.CLOCKING.HQ_SEL 0\' | BUTool.exe -a')
            conn.run('echo \'w SERV.CLOCKING.LHC_SEL 0\' | BUTool.exe -a')

            conn.close()
            print("Clocks should be scoped now.")


        except Exception as e:
            print(f"Error executing commands: {str(e)}")

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
        for proc in psutil.process_iter(['name']):
            try:
                # Check for both vivado and vivado_lab processes
                if proc.info['name'] == 'vivado_lab':
                    print(f"Terminating Vivado process: {proc.pid}")
                    proc.terminate()
                    proc.wait(timeout=5)  # Wait for process to terminate
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                pass
        run_dth_flashy('dth', username='DTH', password='userdth')
        hostname = input("Enter hostname or IP address: ")
        password = getpass("Enter password (leave empty for key-based auth): ")
        valid_connection(hostname, password)
        
        blackplane_clocks(hostname, username='root', password=password)


    else:
        print("Timeout waiting for PDF file generation")

    # Wait for Vivado thread to complete
    vivado_thread.join()

if __name__ == "__main__":
    main()
