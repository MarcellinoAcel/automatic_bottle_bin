import serial
import time

class Uart:
    def __init__(self, port, baudrate, timeout):
        self.firm = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        # self.port = port
        # self.baudrate = baudrate
        # self.timeout = timeout
        print(f"[INFO] Connected to {port} at {baudrate} baud.")

    def send(self, msg):
        """
        Send message to firmware.
        """
        self.firm.write(bytes(msg, 'utf-8'))
        print(f"[SEND] {msg}")

    def read(self):
        """
        Read message from firmware.
        """
        data = self.firm.readline().decode('utf-8').strip()
        if data:
            print(f"[RECV] {data}")
        return data

    def write_and_read(self, msg):
        """
        Send message and read response.
        """
        self.send(msg)
        time.sleep(0.05)
        return self.read()

    def close(self):
        """
        Close serial connection.
        """
        if self.firm:
            self.firm.close()
            print("[INFO] Disconnected from microcontroller.")


# # Example Usage
# if __name__ == "__main__":
#     micro = Uart(port="/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0", baudrate=115200, timeout=10)

#     try:
#         while True:
#             msg = input("Enter a command: ")
#             if msg.lower() == "exit":
#                 break
#             response = micro.write_and_read(msg)
#             print("Arduino Response:", response)
#     except KeyboardInterrupt:
#         print("\n[INFO] Program interrupted by user.")
#     finally:
#         micro.close()

    
    # def digitalWrite(self, pin, value):
    #     pass
    # def analogWrite(self, pin, value):
    #     pass
    # def digitalRead(self, pin):
    #     return 

# import serial
# import curses
# port = "/dev/serial/by-id/usb-STMicroelectronics_STM32_Virtual_ComPort_325730633331-if00"
# ser = serial.Serial(port,115200,timeout=0)

# screen = curses.initscr()

# row = 0
# col = 0
# screen.addstr(row,col,"Value")
# screen.refresh()

# while 1:
#     data = ser.readline()

#     data_sensor = data.decode('utf8')

#     # screen.addstr(row,8, "      ")
#     # print("value = :",data_sensor,"\r\n")
#     screen.addstr(row,64, data_sensor)
#     screen.refresh()
#     # print(data_sensor)