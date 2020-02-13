import queue
import threading
import serial
import serial.tools.list_ports_windows
import sys


class ComMonitorThread(threading.Thread):
    def __init__(self,
                 stringIO_q,
                 error_q,
                 port_num,
                 port_baud,
                 port_stopbits=serial.STOPBITS_ONE,
                 port_parity=serial.PARITY_NONE,
                 port_timeout=2):
        threading.Thread.__init__(self)

        self.serial_port = None
        self.serial_arg = dict(port=port_num,
                               baudrate=port_baud,
                               stopbits=port_stopbits,
                               parity=port_parity,
                               timeout=port_timeout)
        self.stringIO_q = stringIO_q
        self.error_q = error_q

        self.running = True

    def run(self):
        msg = ""
        try:
            if self.serial_port:
                self.serial_port.close()
            print("trying to connect")
            self.serial_port = serial.Serial(**self.serial_arg)
            print("got object: ", self.serial_port)
            self.error_q.put("connected")
            print("got queue")
        except:
            print("error")
            self.error_q.put("port error")

            return

        while self.running:
            new_data = self.serial_port.read(1).decode('utf-8')
            if new_data:
                if new_data == "\n":
                    msg += new_data
                    self.stringIO_q.put(msg)
                    msg = ""
                else:
                    msg += new_data

        if self.serial_port:
            self.serial_port.close()

    def join(self, timeout=None):
        self.running = False
        threading.Thread.join(self, timeout)


    def send(self, msg):
        if self.serial_port:
            self.serial_port.write(msg.encode('utf-8'))

    def stop(self):
        self.runing = False
        if self.serial_port:
            self.serial_port.close()