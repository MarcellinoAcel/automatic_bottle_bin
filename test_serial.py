import uart_com

firm = uart_com.Uart("/dev/serial/by-id/usb-STMicroelectronics_STM32_Virtual_ComPort_325730633331-if00",115200,10)

if __name__ == "__main__":
    try:
        while True:
            msg = input("1")
            if msg.lower() == "exit":
                break
            response = firm.send(msg)
    except:
        print("\n[INFO] Program interrupted by user.")
    finally:
        firm.close()