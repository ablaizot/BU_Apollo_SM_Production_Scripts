import serial
import csv
import time

def get_mac_address(serial_num):
    """
    Get MAC address from mac_addr.csv file based on serial number
    
    Args:
        serial_num (str): Serial number to look up
        
    Returns:
        str: MAC address if found, None otherwise
    """
    try:
        mac_cmd = []

        look = [f"apollo{serial_num}-0", f"apollo{serial_num}-1" , f"ipmc{serial_num}"]
        
        with open('../mac_addr.csv', 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if len(row) >= 4:
                    for key in look:
                        if key in row[4]:
                            print(f"Found matching row for {key}: {row}")
                            mac_cmd.append(row[9])
                            print(f"Added MAC command: {row[9]}")
                
                
        return mac_cmd
    except Exception as e:
        print(f"Error reading MAC address: {str(e)}")
    return None

def send_command_to_ipmc(serial_number, port='/dev/ttyACM1', baudrate=115200):

    mac_cmds = get_mac_address(serial_number)

    cmds = [
        'eepromrd\r\n',
        'verwr 2\r\n',
        'revwr 3\r\n',
        'bootmode 3\r\n',
        f'idwr {serial_number}\r\n'
    ]   
    for i in range(4):
        with serial.Serial(port, baudrate, timeout=2) as ser:

            for cmd in cmds:
                time.sleep(0.2)
                ser.write(cmd.encode('utf-8'))            
                s = ser.read(200)
                time.sleep(0.2)
                print(s.decode('utf-8'))

            for mac_addr in mac_cmds:
                ser.write((mac_addr+'\r\n').encode('utf-8'))
                s = ser.read(200)
                print(s.decode('utf-8'))
                time.sleep(0.2)


            s = ser.read(200)
            print(s.decode('utf-8'))
            time.sleep(1)

            ser.close()
            



if __name__ == "__main__":
    serial_num = input("Enter Apollo serial Number: ")
    send_command_to_ipmc(serial_number=serial_num, port='/dev/ttyACM1', baudrate=115200)