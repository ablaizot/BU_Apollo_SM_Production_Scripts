from fabric import Connection
import time
import socket
import subprocess
from getpass import getpass
import os
from threading import Thread
import glob
import csv

CLOCK_DIR = '/root/soft/clocks/'

def wait_for_device(hostname, timeout=300, interval=5):
    """Wait for device to respond to ping"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # On Windows, ping command is different
            result = subprocess.run(['ping','-c' ,'1', hostname], 
                                 capture_output=True, text=True)
            print(f"Pinging {hostname}... Result: {result.stdout.strip() if result.stdout else result.stderr.strip()}")
            if result.returncode == 0:
                return True
        except:
            pass
        time.sleep(interval)
    return False

def program_clocks(hostname, username='root', password=None, ):
    """
    Execute clock programming and reboot commands over SSH using Fabric
    
    Args:
        hostname (str): The hostname or IP address to connect to
        username (str): SSH username (defaults to 'root')
        password (str): SSH password (optional if using key-based auth)
    """
    try:
        # Create SSH connection
        with Connection(
            host=hostname,
            user=username,
            connect_kwargs={"password": password}
        ) as conn:
            
            print("Changing directory and copying boot files...")
            conn.run('cd /fw/SM/boot_regular_2025-04-28/ && cp BOOT.BIN boot.scr image.ub ../')
            
            try:
                print("Rebooting system...")
                conn.run('reboot')
                conn.close()
            except Exception as e:  
                print(f"Error during reboot: {str(e)}")

        print("Waiting for device to come back online...")
        time.sleep(15) #wait for reboot
        if wait_for_device(hostname):
            print(f"Device {hostname} is back online")
            
            # Create new connection after reboot
            time.sleep(10)  # Additional wait to ensure services are up
            with Connection(
                host=hostname,
                user=username,
                connect_kwargs={"password": password}
            ) as conn:

                # Execute initial commands
                print("Programming clocks...")
                conn.run(f'{CLOCK_DIR}clock_sync_320M_LHC {CLOCK_DIR}CONFIGS/CONFIG.toml')
                
                print("Changing directory and copying boot files...")
                conn.run('cd /fw/SM/boot_loopback && cp BOOT.BIN boot.scr image.ub ../')
                
                conn.close()
    except Exception as e:
        print(f"Error executing commands: {str(e)}")
    
def start_xvcserver(hostname, username='root', password=None):
    try:
        with Connection(
                host=hostname,
                user=username,
                connect_kwargs={"password": password}
            ) as conn:
            try:
                print("Rebooting system...")
                conn.run('reboot')
                conn.close()
            except Exception as e:  
                print(f"Error during reboot: {str(e)}")

        time.sleep(15)

        print("Waiting for device to come back online...")
        if wait_for_device(hostname):
            print(f"Device {hostname} is back online")
            
            # Create new connection after reboot
            time.sleep(10)  # Additional wait to ensure services are up
            with Connection(
                host=hostname,
                user=username,
                connect_kwargs={"password": password}
            ) as conn:
                print("Stopping services...")
                conn.run('systemctl stop xvc_cm1.service xvc_cm2.service xvc_CPLD.service')

                print("Getting IP address...")
                result = conn.run('hostname -I | awk \'{print $1}\'')
                ip_address = result.stdout.strip()
                print(f"Device IP address: {ip_address}")
                ## Write to ip.dat file
                with open('ip.dat', 'w') as f:
                    f.write(ip_address + '\n')
                    f.close()

                print("Starting xvcserver...")
                conn.run('soft/xvcserver &')
                conn.close()
                print("xvcserver started successfully")
                
                
            print("All commands executed successfully")
        else:
            print("Timeout waiting for device to come back online")
            
    except Exception as e:
        print(f"Error executing commands: {str(e)}")

def write_pygen_tcl(hostname, sleep_time):
    """Create pygen.tcl file with required settings"""
    try:
        with open('pygen.tcl', 'w') as f:
            f.write(f'set sleep_time {sleep_time}\n')
            f.write(f'set ip {hostname}\n')
            f.write('source eyescan.tcl\n')
        print("Created pygen.tcl file")
    except Exception as e:
        print(f"Error creating pygen.tcl: {str(e)}")

def run_vivado(hostname='local', sleep_time=0):
    """Run Vivado in batch mode with eyescan.tcl after sourcing settings"""
    try:
        # Wait for ip.dat to exist and contain an IP
        while not os.path.exists('ip.dat'):
            time.sleep(1)
            
        # Read the IP address
        with open('ip.dat', 'r') as f:
            ip = f.read().strip()
        
        # Create pygen.tcl file
        write_pygen_tcl(ip, sleep_time)
            
        # Wait a bit for xvcserver to start
        time.sleep(5)
        
        # Create command to source settings and run Vivado
        cmd = [
            'bash', 
            '-c', 
            'source /tools/Xilinx/Vivado/2023.2/settings64.sh && vivado -mode gui -source pygen.tcl'
        ]
        
        print("Starting Vivado with pygen.tcl...")
        subprocess.run(cmd, check=True)
        
    except Exception as e:
        print(f"Error running Vivado: {str(e)}")

def monitor_scans(hostname, password=None):
    """Monitor directory for PDFs and check CSV files for Open Area"""
    try:
        while True:
            # Check for PDF count
            pdf_files = glob.glob("*.pdf")
            if len(pdf_files) >= 5:
                print("Found 5 or more PDFs, checking CSV files...")
                
                # Check all CSV files
                csv_files = glob.glob("*.csv")
                restart_needed = False
                
                for csv_file in csv_files:
                    with open(csv_file, 'r') as f:
                        # Read file content
                        content = f.read()
                        
                        # Check if this is a scan results file
                        if 'Open Area' in content:
                            # Reset file pointer and create CSV reader
                            f.seek(0)
                            reader = csv.reader(f)
                            
                            # Find Open Area value
                            for row in reader:
                                if len(row) > 1 and row[0].strip() == 'Open Area':
                                    open_area = int(row[1])
                                    print(f"Found Open Area in {csv_file}: {open_area}")
                                    
                                    if open_area == 0:
                                        print(f"Found zero Open Area in {csv_file}")
                                        restart_needed = True
                                        break
                
                if restart_needed:
                    print("Restarting xvcserver and Vivado...")
                    
                    # Stop existing Vivado thread if running
                    if 'vivado_thread' in globals() and vivado_thread.is_alive():
                        vivado_thread.join(timeout=1)
                    
                    # Delete ip.dat to force clean start
                    if os.path.exists('ip.dat'):
                        os.remove('ip.dat')
                    
                    # Start new xvcserver
                    start_xvcserver(hostname, password=password)
                    
                    # Create and start new Vivado thread
                    vivado_thread = Thread(target=run_vivado(sleep_time=0))
                    vivado_thread.daemon = True
                    vivado_thread.start()
                    
                    print("Services restarted")
                    
                break  # Exit monitoring loop after checking files
                
            time.sleep(5)  # Wait before checking again
            
    except Exception as e:
        print(f"Error in monitor_scans: {str(e)}")

if __name__ == "__main__":
    # Start Vivado process in separate thread
    # delete ip.dat file
    if os.path.exists('ip.dat'):
        os.remove('ip.dat')

    vivado_thread = Thread(target=run_vivado)
    vivado_thread.daemon = True
    vivado_thread.start()
    
    # Get hostname from user input
    hostname = input("Enter hostname or IP address: ")
    password = getpass("Enter password (leave empty for key-based auth): ")
    change_fw = input ("Change to Loopback FW? (yes/no): ").strip().lower()
    change_fw = change_fw == 'yes'  # Convert to boolean
    
    # Call function with user-provided hostname
    if not change_fw:
        program_clocks(hostname, password=password if password else None)

    # Start xvcserver
    start_xvcserver(hostname, password=password if password else None)
    
    # Start monitoring in separate thread
    monitor_thread = Thread(target=monitor_scans, args=(hostname, password if password else None))
    monitor_thread.daemon = True
    monitor_thread.start()
