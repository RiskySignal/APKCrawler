# coding=utf-8
import platform
import sys
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from crontab import CronTab, CronItem
from PyQt5 import QtGui
from settings import ProgressBarStyleSheet
from ui_thread import *
from custom_ui import TimerGUI

BUTTON_HEIGHT = 25

__current_folder_path__ = os.path.dirname(os.path.abspath(__file__))


class CrawlerGUI(QWidget):
    # Main GUI for crawler module.

    def __init__(self):
        super(CrawlerGUI, self).__init__()
        self.layout_init()

    def layout_init(self):
        # 整体大小
        height = 800
        width = 700
        self.setFixedSize(width, height)
        self.setWindowTitle("Crawler GUI")

        # 设置字体
        self.setFont(QFont("Microsoft YaHei", 8.5))

        # set layout
        root_layout = QVBoxLayout()
        crawler_widget = QGroupBox(title="APK Crawler")
        util_widget = QGroupBox(title="Crawler Util")
        root_layout.addWidget(crawler_widget)
        root_layout.addWidget(util_widget)
        root_layout.setStretch(0, 3)
        root_layout.setStretch(1, 2)

        # save the widget value
        self.crawler_widget = crawler_widget
        self.util_widget = util_widget

        # init the sub layout
        self.util_widget_init()
        self.crawler_widget_init()

        # show
        self.setLayout(root_layout)

    def crawler_widget_init(self):
        # set layout
        crawler_layout = QVBoxLayout()
        crawler_top_layout = QHBoxLayout()
        crawler_layout.addLayout(crawler_top_layout)
        crawler_log_text = QTextBrowser()
        crawler_layout.addWidget(crawler_log_text)
        self.crawler_widget.setLayout(crawler_layout)

        # save the value
        self.crawler_layout = crawler_layout
        self.crawler_top_layout = crawler_top_layout
        self.crawler_log_text = crawler_log_text

        # init the sub layout
        self.crawler_top_layout_init()

    def crawler_top_layout_init(self):
        # set layout
        crawler_combobox = QComboBox()
        crawler_combobox.setFixedWidth(150)
        crawler_combobox.setFixedHeight(BUTTON_HEIGHT)
        start_crawl_button = QPushButton("Start")
        start_crawl_button.setFixedHeight(BUTTON_HEIGHT)
        stop_crawl_button = QPushButton("Stop")
        stop_crawl_button.setFixedHeight(BUTTON_HEIGHT)
        stop_crawl_button.setVisible(False)
        self.crawler_top_layout.addWidget(crawler_combobox)
        self.crawler_top_layout.addStretch()
        self.crawler_top_layout.addWidget(start_crawl_button)
        self.crawler_top_layout.addWidget(stop_crawl_button)

        # save the value
        self.crawler_combobox = crawler_combobox
        self.start_crawl_button = start_crawl_button
        self.stop_crawl_button = stop_crawl_button

    def util_widget_init(self):
        # set layout
        util_layout = QVBoxLayout()
        util_button_layout = QHBoxLayout()
        timer_table_widget = QTableWidget()
        util_layout.addLayout(util_button_layout)
        util_layout.addWidget(timer_table_widget)
        util_layout.addStretch()
        self.util_widget.setLayout(util_layout)

        # save the value
        self.util_layout = util_layout
        self.util_button_layout = util_button_layout
        self.timer_table_widget = timer_table_widget

        # init the sub layout
        self.util_button_layout_init()
        self.timer_table_widget_init()

    def util_button_layout_init(self):
        # set layout
        add_timer_button = QPushButton("Add Timer")
        add_timer_button.setFixedHeight(BUTTON_HEIGHT)
        delete_timer_button = QPushButton("Delete Timer")
        delete_timer_button.setFixedHeight(BUTTON_HEIGHT)
        self.util_button_layout.addStretch()
        self.util_button_layout.addWidget(add_timer_button)
        self.util_button_layout.addWidget(delete_timer_button)

        # save the value
        self.add_timer_button = add_timer_button
        self.delete_timer_button = delete_timer_button

    def timer_table_widget_init(self):
        # set layout
        self.timer_table_widget.setColumnCount(5)
        self.timer_table_widget.setHorizontalHeaderLabels(['Month', "Day", "Hour", "Minute", "Week Day", "Crawler"])
        self.timer_table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.timer_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.timer_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.timer_table_widget.horizontalHeader().setSectionsClickable(False)

    def add_apk_layout_init(self):
        # set layout
        add_apk_button = QPushButton(QIcon(os.path.join(__current_folder_path__, "./images/folder_import.png")), "Import APK From Folder")
        add_apk_button.setFixedHeight(BUTTON_HEIGHT)
        add_apk_progress_bar = QProgressBar()
        add_apk_progress_bar.setObjectName("BlueProgressBar")
        add_apk_progress_bar.setStyleSheet(ProgressBarStyleSheet)
        add_apk_progress_bar.setVisible(False)
        self.add_apk_layout.addWidget(add_apk_button)
        self.add_apk_layout.addWidget(add_apk_progress_bar)

        # save the value
        self.add_apk_button = add_apk_button
        self.add_apk_progress_bar = add_apk_progress_bar


class CrawlerProcess(CrawlerGUI):
    scrapy_log_signal = pyqtSignal(str)
    scrapy_start_signal = pyqtSignal()
    scrapy_finish_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    crawler_list = ["fossdroid", "xiaomi", "apkpure", "github", "github_opensource"]
    timer_list = []
    timer_model = None
    user_crontab = None

    def __init__(self):
        super(CrawlerProcess, self).__init__()
        self.thread_pool = QThreadPool()
        self.thread_pool.globalInstance()
        self.thread_pool.setMaxThreadCount(8)

        self.bind_error()
        self.load_data()
        self.bind_scrapy()
        self.bind_timer()
        self.check_value()

    """
    加载ComboBox数据
    """

    def load_data(self):
        # crawler combobox
        self.crawler_combobox.addItems(self.crawler_list)

    """
    设置scrapy
    """

    def bind_scrapy(self):
        self.scrapy_worker = ScrapyWorker(self)
        self.scrapy_start_signal.connect(self.crawler_log_text.clear)
        self.scrapy_finish_signal.connect(self.scrapy_finish)
        self.scrapy_log_signal.connect(self.parse_log)
        self.start_crawl_button.clicked.connect(self.start_scrapy)
        self.stop_crawl_button.clicked.connect(self.stop_scrapy)

    def parse_log(self, text):
        pre_cursor = self.crawler_log_text.textCursor()
        self.crawler_log_text.moveCursor(QtGui.QTextCursor.End)
        self.crawler_log_text.insertPlainText(text)
        if self._keep_log_end_:
            pre_cursor.movePosition(QtGui.QTextCursor.End)
        self.crawler_log_text.setTextCursor(pre_cursor)

    def start_scrapy(self):
        if not self.check_value():
            return

        platform = self.crawler_combobox.currentText()
        self.start_crawl_button.setVisible(False)
        self.stop_crawl_button.setVisible(True)
        self.scrapy_worker.run(platform)
        self._keep_log_end_ = True

    def stop_scrapy(self):
        self.scrapy_worker.stop()
        self.stop_crawl_button.setVisible(False)
        self.start_crawl_button.setVisible(True)

    def scrapy_finish(self):
        self.parse_log("\n\n\n Scrapy Worker Done!")
        self.start_crawl_button.setVisible(True)
        self.stop_crawl_button.setVisible(False)

    """
    定时器
    """

    def bind_timer(self):
        self.timer_window = TimerGUI()
        self.timer_window.load_crawler(self.crawler_list)
        self.timer_window.setWindowModality(QtCore.Qt.ApplicationModal)
        self.timer_window.timer_signal.connect(self.add_new_timer)
        self.add_timer_button.clicked.connect(self.add_timer_button_click)
        self.delete_timer_button.clicked.connect(self.delete_timer_button_click)

        self.update_timer()

    def add_timer_button_click(self):
        if not self.check_value():
            return

        self.timer_window.reset_edit()
        self.timer_window.show()
        self.timer_window.exec_()

    def add_new_timer(self, month, day, hour, minute, crawler_name):
        if month == -1 and day == -1 and hour == -1 and minute == -1:
            return

        if month == -1:
            month = "*"
        if day == -1:
            day = "*"
        if hour == -1:
            hour = "*"
        if minute == -1:
            minute = "*"

        if platform.system() == "Windows":
            print("Not imply in windows.")
        else:
            crawler_script_path = os.path.join(__current_folder_path__, "main.py")
            crontab_command = "{} {} --market_name {}".format(python_interface, crawler_script_path, crawler_name)
            crontab_time = "{} {} {} {} *".format(minute, hour, day, month)
            comment = "apk crawler job"
            user_crontab = CronTab(user=True)
            job = user_crontab.new(command=crontab_command, comment=comment)
            job.setall(crontab_time)
            job.enable()
            user_crontab.write()

            self.update_timer()

    def update_timer(self):
        if platform.system() == "Windows":
            print("Not imply in windows.")
        else:
            user_crontab = CronTab(user=True)  # todo: 检查一下
            job_iter = user_crontab.find_comment("apk crawler job")
            self.user_crontab = user_crontab
            self.timer_list = list(job_iter)
            timer_data_list = []
            for job in self.timer_list:  # type: CronItem
                month, day, hour, minute = job.month, job.dom, job.hour, job.minute
                crawler = job.command.split('--market_name')[1].strip()
                timer_data_list.append([month, day, hour, minute, crawler])

            self.timer_table_widget.clear()
            self.timer_table_widget.setRowCount(len(timer_data_list))
            _row_ = 0
            for timer_data in timer_data_list:
                for _column_ in range(self.timer_table_widget.columnCount()):
                    q_table_widget_item = QTableWidgetItem(str(timer_data[_column_]))
                    q_table_widget_item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    self.timer_table_widget.setItem(_row_, _column_, q_table_widget_item)
                _row_ += 1

    def delete_timer_button_click(self):
        timer_index = self.timer_table_widget.currentIndex().row()
        if timer_index == -1:
            return

        timer_job = self.timer_list[timer_index]  # type: CronItem
        self.user_crontab.remove(timer_job)
        self.user_crontab.write()
        self.update_timer()

    """
    错误
    """

    def bind_error(self):
        self.error_signal.connect(self.catch_error)

    def catch_error(self, _err_: str):
        log_file = os.path.join(__current_folder_path__, "../../log/main_gui.{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d-%H")))
        with open(log_file, 'a') as _file_:
            _file_.write(_err_)

    def check_value(self):
        enviro = True
        if python_interface is None:
            QMessageBox.warning(self, "Python Interface Error", "Please set the 'python_interface' in setting.py.", QMessageBox.Ok, QMessageBox.Ok)
            enviro = False
        return enviro


if __name__ == '__main__':
    app = QApplication(sys.argv)
    crawler_gui = CrawlerProcess()
    crawler_gui.show()
    sys.exit(app.exec_())
