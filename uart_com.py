import serial
import time

class Uart:
    def __init__(self, port, baudrate, timeout):
        self.firm = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    def send(self, msg):
        self.firm.write(bytes(msg, 'utf-8'))
    def read(self):
        data = self.firm.readline().decode('utf-8').strip()
        if data:
            print(f"[RECV] {data}")
        return data

    def close(self):
        if self.firm:
            self.firm.close()
            print("[INFO] Disconnected from microcontroller.")

    def read_int(self):
        data = self.read()
        try:
            return int(data)
        except ValueError:
            print(f"[ERROR] Failed to convert '{data}' to int.")
            return None
        
    def read_float(self):
        data = self.read()
        try:
            return float(data)
        except ValueError:
            print(f"[ERROR] Failed to convert '{data}' to float.")
            return None
    def read_str(self):
        return self.read()
    def read_char(self):
        data = self.read()
        if len(data) == 1:
            return data
        else:
            print(f"[ERROR] Received more than one character: '{data}'")
            return None