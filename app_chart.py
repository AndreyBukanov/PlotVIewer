import math
from builtins import bool

from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QPainter, QFont

import numpy as np

class ChartViewSet:

    count = 0
    charts = list()
    chart_views = list()
    series = list()
    axis_x = list()
    axis_y = list()
    time = list()
    data = list()

    period = 20

    def __init__(self, n):

        self.count = n

        for _ in range(0, self.count):

            self.data.append(list())

            chart = QChart()
            self.charts.append(chart)

            chart_view = QChartView(chart)
            self.chart_views.append(chart_view)

            series = QLineSeries()
            self.series.append(series)

            chart.addSeries(series)

            axis_x = QValueAxis()
            axis_x.setRange(0, 10)
            chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(axis_x)
            self.axis_x.append(axis_x)

            axis_y = QValueAxis()
            axis_y.setRange(-110, 110)
            chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            series.attachAxis(axis_y)
            self.axis_y.append(axis_y)

            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)

            chart.setTitleFont(title_font)
            chart.legend().hide()
            chart.layout().setContentsMargins(0, 0, 0, 0)
            chart.setBackgroundRoundness(0)
            chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

    def get_chart_view(self, n):

        if n < len(self.chart_views):
            return self.chart_views[n]
        else:
            return QChartView()

    def add_data(self, data, time):

        if len(data) < self.count:
            return

        right_border = time
        left_border = right_border - self.period

        self.time.append(time)

        while self.time[0] < left_border:
             self.time.pop(0)

        for i in range(0, self.count):

            self.series[i] << QPointF(time, data[i])
            self.data[i].append(data[i])

            while self.series[i].count() > len(self.time):
                self.series[i].remove(0)
                self.data[i].pop(0)

            top_border = max(self.data[i]) + 1
            bottom_border = min(self.data[i]) - 1

            self.axis_x[i].setRange(left_border, right_border)
            self.axis_y[i].setRange(bottom_border, top_border)

            chart = self.charts[i]
            chart.setTitle(str(np.median(self.data[i][-10:])) + " Pressure Parrots")












