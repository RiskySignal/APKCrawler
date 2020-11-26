# coding=utf-8
import sys

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QVBoxLayout, QPushButton, QHBoxLayout, QTextBrowser


class Crawler_UI(QWidget):
    # Main UI function for crawler module.

    def __init__(self):
        super().__init__()
        self._keep_the_end_ = True
        self.root_layout = QVBoxLayout()
        self.top_layout = QHBoxLayout()
        self.bottom_layout = QVBoxLayout()
        self.combobox = QComboBox()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.log_area = QTextBrowser()

        self.layout_init()
        self.combobox_init()
        self.event_init()

        # scrapy
        self.scrapy_worker = ScrapyWorker()
        self.scrapy_worker.logChanged.connect(self.parse_log)
        self.scrapy_worker.started.connect(self.log_area.clear)
        self.scrapy_worker.finished.connect(self.scrapy_finish)

    @QtCore.pyqtSlot(str)
    def parse_log(self, text):
        pre_cursor = self.log_area.textCursor()
        self.log_area.moveCursor(QtGui.QTextCursor.End)
        self.log_area.insertPlainText(text)
        if self._keep_the_end_:
            pre_cursor.movePosition(QtGui.QTextCursor.End)
        self.log_area.setTextCursor(pre_cursor)

    def scrapy_finish(self):
        self.parse_log("Scrapy Worker Done!")
        self.start_button.setVisible(True)
        self.stop_button.setVisible(False)

    def layout_init(self):
        # 整体大小
        self.setFixedSize(894, 600)
        self.setWindowTitle("Crawler GUI")

        # 组件字体
        component_font = QtGui.QFont()
        component_font.setFamily("Arial")
        component_font.setPointSize(11)
        self.combobox.setFont(component_font)
        self.start_button.setFont(component_font)
        self.stop_button.setFont(component_font)

        # 隐藏stop button
        self.stop_button.setVisible(False)

        # log 字体
        log_font = QtGui.QFont()
        log_font.setFamily("Consolas")
        log_font.setPointSize(9)
        self.log_area.setFont(log_font)

        # button大小
        button_size = (158, 30)
        self.start_button.setFixedSize(*button_size)
        self.stop_button.setFixedSize(*button_size)

        # 组件布局
        self.top_layout.addSpacing(20)
        self.top_layout.addWidget(self.combobox)
        self.top_layout.addSpacing(100)
        self.top_layout.addWidget(self.start_button)
        self.top_layout.addWidget(self.stop_button)
        self.top_layout.addSpacing(20)
        self.bottom_layout.addWidget(self.log_area)

        self.root_layout.addLayout(self.top_layout)
        self.root_layout.addLayout(self.bottom_layout)
        self.setLayout(self.root_layout)

    def event_init(self):
        self.start_button.clicked.connect(self.start_on_click)
        self.stop_button.clicked.connect(self.stop_on_click)

    def start_on_click(self):
        platform = self.combobox.currentText()
        self.stop_button.setVisible(True)
        self.start_button.setVisible(False)
        # start scrapy
        self.scrapy_worker.run(platform)

    def stop_on_click(self):
        self.stop_button.setVisible(False)
        self.start_button.setVisible(True)
        # stop scrapy
        self.scrapy_worker.stop()

    def combobox_init(self):
        self.combobox.addItems(["fossdroid", "xiaomi", "apkpure"])


class ScrapyWorker(QtCore.QObject):
    logChanged = QtCore.pyqtSignal(str)
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process = QtCore.QProcess(self)
        self._process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self._process.readyReadStandardOutput.connect(self.on_readyReadStandardOutput)
        self._process.setProgram("python")
        self._process.started.connect(self.started)
        self._process.finished.connect(self.finished)

    def run(self, platform):
        self._process.setWorkingDirectory('./')
        self._process.setArguments(['./main.py', "--market_name", platform])
        self._process.start()

    @QtCore.pyqtSlot()
    def on_readyReadStandardOutput(self):
        data = self._process.readAllStandardOutput().data().decode()
        self.logChanged.emit(data)

    @QtCore.pyqtSlot()
    def stop(self):
        self._process.kill()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    crawler_ui = Crawler_UI()
    crawler_ui.show()
    sys.exit(app.exec_())
