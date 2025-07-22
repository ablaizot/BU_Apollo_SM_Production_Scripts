import serial
import csv

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
        with open('mac_addr.csv', 'r') as f:
            reader = csv.reader(f, delimiter=' ')
            for row in reader:
                print(f"Processing row: {row}")  # Debugging output
                if len(row) >= 4 and row[0] == serial_num and row[1] == 'eth0':
                    mac_cmd.append(row[9])
                
                
        return mac_cmd
    except Exception as e:
        print(f"Error reading MAC address: {str(e)}")
    return None

def send_command_to_ipmc(serial_number, port='/dev/ttyACM1', baudrate=115200):

    mac_cmds = get_mac_address(serial_number)

    with serial.Serial(port, baudrate, timeout=1) as ser:
        ser.write(b'eepromrd\n')
        s = ser.read(100)
        print(s.decode('utf-8'))

        ser.write(b'verwr 2\n')
        ser.write(b'revwr 3\n')
        ser.write(b'bootmode 3\n')
        ser.write(b'idwr {f"{serial_number}"}\n'.format(serial_number=serial_number))

        for mac_addr in mac_cmds:
            ser.write(mac_addr.encode('utf-8') + b'\n')

        s = ser.read(200)
        print(s.decode('utf-8'))
        ser.close()


if __name__ == "__main__":
    serial_num = input("Enter Apollo serial Number: ")
    send_command_to_ipmc(serial_number=serial_num, port='/dev/ttyACM1', baudrate=115200)