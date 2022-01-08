"""
Module for interfacing and communicating with stuff over serial.
@author - James Malone
"""

import logging
import sys
import time
import serial

class iotty:
    """Class for communicating with devices over serial."""
    def __init__(self, port = 'COM5', baud = 115200, log_level = logging.INFO):
        self.send_wait = 0.20 # Arbritrary waiting period to save flooding comms
        logging.basicConfig(filename='iotty.log', format='%(asctime)s - %(message)s',\
            level=log_level)
        try:
            self.ser = serial.Serial(port, baud)
        except serial.SerialException:
            logging.critical("Could not open port '%s'", port)
            sys.exit(1)

    def open(self):
        """Open the serial connection."""
        self.ser.isOpen()
        logging.debug("Opened serial port successfully")

    def send(self, data):
        """Send data over the serial connection."""
        bytes_to_send = data.encode('utf-8')
        logging.debug("Sending -> %s", str(data))
        self.ser.write(bytes_to_send)
        time.sleep(self.send_wait)

    def recv(self):
        """Receive the output."""
        output = ''
        while self.ser.inWaiting() > 0:
            output += self.ser.read(1).decode('utf-8')
        logging.debug("Received <- %s", str(output))
        return output

    def close(self):
        """Close the connection."""
        self.ser.close()
        logging.debug("Closed serial port successfully")
