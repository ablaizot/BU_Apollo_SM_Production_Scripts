import serial

def send_command_to_ipmc(serial_number, port='/dev/ttyACM1', baudrate=115200):

    with serial.Serial(port, baudrate, timeout=1) as ser:
        ser.write(b'eepromrd')
        s = ser.read(100)
        print(s.decode('utf-8'))
        ser.write(b'verwr 2')
        ser.write(b'revwr 3')
        ser.write(b'bootmode 3')
        ser.close()


if __name__ == "__main__":
    send_command_to_ipmc(serial_number='CM01', port='/dev/ttyACM1', baudrate=115200)