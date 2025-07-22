import serial

def send_command_to_ipmc(serial_number, port='/dev/ttyACM1', baudrate=115200):

    with serial.Serial(port, baudrate, timeout=1) as ser:
        ser.write(b'eepromrd\n')
        s = ser.read(100)
        print(s.decode('utf-8'))

        ser.write(b'verwr 2\n')
        ser.write(b'revwr 3\n')
        ser.write(b'bootmode 3\n')
        ser.write(b'bootmode 2\n')

        s = ser.read(200)
        ser.close()


if __name__ == "__main__":
    send_command_to_ipmc(serial_number='CM01', port='/dev/ttyACM1', baudrate=115200)