import uart_com

firm = uart_com.Uart("/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0",115200,10)

if __name__ == "__main__":
    try:
        while True:
            msg = input("Enter a command: ")
            if msg.lower() == "exit":
                break
            response = firm.send(msg)
    except:
        print("\n[INFO] Program interrupted by user.")
    finally:
        firm.close()