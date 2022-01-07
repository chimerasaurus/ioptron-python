"""
Module for interfacing and communicating with stuff over serial.
@author - James Malone
"""

import time
import sys
import serial

class iotty:
    """Class for communicating with devices over serial."""
    def __init__(self, port = 'COM5', baud=115200):
        self.send_wait = 0.20 # Arbritrary waiting period to save flooding comms

        try:
            self.ser = serial.Serial(port, baud)
        except serial.SerialException:
            sys.stderr.write('ERROR: Could not open port: ' + port + '\n')
            sys.exit(1)

    def open(self):
        """Open the serial connection."""
        self.ser.isOpen()

    def send(self, data):
        """Send data over the serial connection."""
        bytes_to_send = data.encode('utf-8')
        self.ser.write(bytes_to_send)
        time.sleep(self.send_wait)

    def recv(self):
        """Receive the output."""
        output = ''
        while self.ser.inWaiting() > 0:
            output += self.ser.read(1).decode('utf-8')
        return output

    def close(self):
        """Close the connection."""
        self.ser.close()
