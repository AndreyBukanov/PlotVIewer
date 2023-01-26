
from PyQt6.QtCore import QObject, QThread, pyqtSignal

import serial
import sys
import glob
import time

import struct


def serial_ports():

    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []

    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class ComRunner(QObject):

    data = pyqtSignal(bytes)
    finished = pyqtSignal()
    running = False
    thread = None
    worker = None
    com = None

    def __init__(self):
        super(QObject, self).__init__()

    def connect(self, port_name, baud_rate):

        self.com = serial.Serial(port_name, baud_rate, timeout=1)

        return self.com.isOpen()

    def refuse(self):
        self.com.close()

    def start(self):

        self.thread = QThread()
        self.worker = ComWorker(self.com)

        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.data.connect(self.data)

        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.finished)

        self.thread.start()

        self.running = True
        return self.is_running()

    def stop(self):

        self.worker.stop()

        self.running = False
        return self.is_running()

    def is_running(self):
        return self.running


class ComWorker(QObject):

    timeout_wait = 0.1
    timeout_read = 0.010

    data = pyqtSignal(bytes)
    finished = pyqtSignal()
    running = False
    buffer = bytes
    com = None

    def __init__(self, com):
        super(QObject, self).__init__()
        self.com = com

    def run(self):

        print("Started...")
        self.running = True

        request = bytearray(b'\x01\x04\x00\x20\x00\x01\x30\x00')
        answer = bytearray()
        answer_len = 7

        prev_time = 0.0
        value = 0.0

        try:
            while self.running:

                current_time = time.thread_time()

                if(current_time - prev_time) < 0.1:
                    continue

                prev_time = current_time

                print("Running...")

                self.com.write(request)

                answer = self.com.read(7)

                value = float(int.from_bytes(answer[3:5], byteorder='big', signed=False))
                value = value * 500 / 60000

                self.buffer = struct.pack("f", value)
                self.data.emit(self.buffer)



        except serial.serialutil.SerialException:
            print("COM port is dead...")
            while self.running:
                print("COM port dead cycle...")
                time.sleep(1)

        print("Stopped...")
        self.finished.emit()

    def stop(self):
        self.running = False
