import struct
import time
from datetime import datetime

from PyQt6.QtWidgets import QMainWindow, QFileDialog

from app_chart import *
from app_ui import *
from com_worker import *


class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()

        self.file = None
        self.file_started = False
        self.file_path = ""
        self.file_name = ""

        # Remember start time
        self.start_time = time.time_ns()

        # Port runner
        self.port_runner = ComRunner()
        self.port_runner.finished.connect(self.on_com_port_stopped)
        self.port_runner.data.connect(self.on_data)

        # Charts
        self.chart_number = 1
        self.charts = ChartViewSet(self.chart_number)

        # Ui setup
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.button_scan.released.connect(self.on_scan_released)
        self.ui.button_connect.released.connect(self.on_connect_released)
        self.ui.button_browse.released.connect(self.on_browse_released)
        self.ui.button_start.released.connect(self.on_start_released)

        self.create_charts()

    def log_values(self, values, receive_time):

        if not self.file_started:
            return

        out = str(receive_time)

        for value in values:
            out += "\t" + str(value)

        out += "\n"

        self.file.write(out)

    def on_browse_released(self):

        self.file_path = QFileDialog.getExistingDirectory()

        if len(self.file_path) == 0:
            return

        self.ui.lineEdit.setText(self.file_path)

    def on_start_released(self):

        if not self.file_started:

            if not len(self.file_path):
                return

            self.file_started = True

            self.file_name = str(datetime.now().strftime("%d_%m_%y_%H_%M_%S")) + ".log"
            self.file = open(self.file_path + "/" + self.file_name, 'w+')

            self.ui.button_start.setText("STOP")
            self.ui.button_browse.setEnabled(False)
            self.ui.lineEdit.setEnabled(False)

        else:
            self.file_started = False

            self.file.close()
            self.ui.button_start.setText("START")
            self.ui.button_browse.setEnabled(True)
            self.ui.lineEdit.setEnabled(True)

    def on_data(self, payload):

        receive_time = (time.time_ns() - self.start_time) / 1000000000

        float_values = []
        float_bytes = 4

        chunks = [payload[i:i + float_bytes] for i in range(0, len(payload), float_bytes)]

        for chunk in chunks:

            if len(chunk) < float_bytes:
                break
                
            float_values += (struct.unpack("f", chunk))

        self.log_values(float_values, receive_time)
        self.draw_data(float_values, receive_time)

    def draw_data(self, values, receive_time):
        self.charts.add_data(values, receive_time)

    def on_scan_released(self):

        names = serial_ports()

        self.ui.comboBox.clear()

        for port_name in names:
            self.ui.comboBox.addItem(port_name)

    def on_connect_released(self):

        is_running = self.port_runner.is_running()

        if not is_running:
            port_name = self.ui.comboBox.currentText()
            baud_rate = int(self.ui.comboBox_2.currentText())
            connected = self.port_runner.connect(port_name, baud_rate)

            if not connected:
                return

        if self.port_runner.is_running():
            self.ui.button_connect.setText("CONNECT")
            self.ui.button_connect.setEnabled(False)
            self.port_runner.stop()
        else:
            self.ui.button_connect.setText("STOP")
            self.ui.button_scan.setEnabled(False)
            self.ui.comboBox.setEnabled(False)
            self.ui.comboBox_2.setEnabled(False)
            self.port_runner.start()

    def on_com_port_stopped(self):

        self.port_runner.refuse()

        self.ui.button_scan.setEnabled(True)
        self.ui.comboBox.setEnabled(True)
        self.ui.comboBox_2.setEnabled(True)
        self.ui.button_connect.setEnabled(True)

    def create_charts(self):

        params = [[0, 0, 1, 1], [1, 0, 1, 1], [2, 0, 1, 1],
                  [0, 1, 1, 1], [1, 1, 1, 1], [2, 1, 1, 1],
                  [0, 2, 1, 1], [1, 2, 1, 1], [2, 2, 1, 1],
                  [0, 3, 1, 1], [1, 3, 1, 1], [2, 3, 1, 1]]

        chart_Layout = QtWidgets.QGridLayout(self.ui.widget_plots)
        chart_Layout.setContentsMargins(0, 0, 0, 0)

        for n in range(0, self.chart_number):
            param = params[n]
            chart_view = self.charts.get_chart_view(n)
            chart_Layout.addWidget(chart_view, param[0], param[1], param[2], param[3])

