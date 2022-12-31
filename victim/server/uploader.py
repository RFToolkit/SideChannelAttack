
import serial

with serial.Serial() as ser:
    ser.baudrate = 9600
    ser.port = '/dev/ttyACM0'
    ser.open()
    while True:
        print(ser.read(10).decode('utf-8', 'ignore'))