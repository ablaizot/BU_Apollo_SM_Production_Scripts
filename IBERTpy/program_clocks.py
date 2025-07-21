from fabric import Connection
import time
import socket
import subprocess
from getpass import getpass  # Add this import at the top

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

def program_clocks(hostname, username='root', password=None):
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
            except Exception as e:  
                print(f"Error during reboot: {str(e)}")

        print("Waiting for device to come back online...")
        time.sleep(10) #wait for reboot
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
                
                try:
                    print("Rebooting system...")
                    conn.run('reboot')
                except Exception as e:  
                    print(f"Error during reboot: {str(e)}")
        time.sleep(10)
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
                
                
            print("All commands executed successfully")
        else:
            print("Timeout waiting for device to come back online")
            
    except Exception as e:
        print(f"Error executing commands: {str(e)}")

if __name__ == "__main__":
    # Get hostname from user input
    hostname = input("Enter hostname or IP address: ")
    password = getpass("Enter password (leave empty for key-based auth): ")
    
    # Call function with user-provided hostname
    program_clocks(hostname, password=password if password else None)