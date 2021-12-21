import os
import sys
import time

import argparse
import serial

def main():
    print("Starting program...")

    parser = argparse.ArgumentParser(description="Mojo V3 Loader Arguments")
    parser.add_argument('-p', "--port", required=True, type=str, help="select a serial port to upload to")
    parser.add_argument('-b', "--file", required=True, type=str, help="select the binary file to upload")
    
    args = parser.parse_args()

    try:
        port = args.port
    except Exception:
        print("Port not defined! Please select a port with -p [port]")
        sys.exit(-1)
    try:
        binary = args.file
    except Exception:
        print("Binary path not defined! Please select a binary path with -b [path]")
        sys.exit(-1)

    print("Reading bin file...")
    file = open(str(binary), "rb")
    binary_data = file.read()
    file_len = len(binary_data)
    file.close()
    print("Successfully read file: "+str(binary))

    ser = serial.Serial(port, 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout=2) # 9600 baud, 2 second timeout
    ser.open()

    print("Restarting Mojo board...")
    ser.setDTR(False)
    time.sleep(5/1000)
    for i in range(0,5):
        ser.setDTR(False)
        time.sleep(5/1000)
        ser.setDTR(True)
        time.sleep(5/1000)
    # Mojo should be rebooted by now!

    ser.flushInput()
    ser.flushOutput()
    print("Done.")

    ser.write(b'F') # F for flash
    if(ser.read(1)[0] != b'R'):
        print("Mojo did not respond! Make sure the port is set correctly!")
        sys.exit(-1)

    ser.write(file_len.to_bytes(4,'big'))

    if(ser.read(1)[0] != 'O'):
        print("Mojo did not acknowledge transfer size!")
        sys.exit(-1)

    print("Uploading...")
    byte_arr = bytearray(binary_data)
    ser.write(byte_arr)

    if(ser.read(1)[0] != 'D'):
        print("Mojo did not acknowledge the transfer! This means that your code has likely not been uploaded! Try running this program again.")
        sys.exit(-1)

    print("Program finished!")

    ser.close()



if __name__ == "__main__":
    main()