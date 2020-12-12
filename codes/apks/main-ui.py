# coding=utf-8
import sys
import platform

import os
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QVBoxLayout, QPushButton, QHBoxLayout, QTextBrowser, QGroupBox, QGridLayout, QProgressBar, QTableWidget, QDialog, QLabel, QLineEdit, QMessageBox, QAbstractItemView, QHeaderView, QTableWidgetItem, QListView
from crontab import CronTab
from crontab import CronItem
from database import Database

__current_folder_path__ = os.path.dirname(os.path.abspath(__file__))


class TimerGUI(QDialog):
    # Timer GUI for adding new timer
    timer_signal = QtCore.pyqtSignal(int, int, int, int, str)

    def __init__(self):
        super(TimerGUI, self).__init__()

        self.jobs = []
        self.crawler_combobox = QComboBox()
        self.confirm_button = QPushButton("Confirm")
        self.cancel_button = QPushButton("Cancel")
        self.minute_edit = QLineEdit()
        self.hour_edit = QLineEdit()
        self.day_edit = QLineEdit()
        self.month_edit = QLineEdit()

        self.combobox_init()
        self.edit_init()
        self.layout_init()
        self.event_init()

    def layout_init(self):
        width = 450
        height = 100
        self.setFixedSize(width, height)
        self.setWindowTitle("Add New Timer")

        # root layout, 上下布局
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()
        root_layout = QVBoxLayout()
        root_layout.addLayout(top_layout)
        root_layout.addLayout(bottom_layout)

        ## top layout, 选择日期和爬虫
        month_layout = QVBoxLayout()
        month_label = QLabel(text="Month: ")
        month_layout.addWidget(month_label)
        month_layout.addWidget(self.month_edit)
        top_layout.addLayout(month_layout)
        day_layout = QVBoxLayout()
        day_label = QLabel(text="Day: ")
        day_layout.addWidget(day_label)
        day_layout.addWidget(self.day_edit)
        top_layout.addLayout(day_layout)
        hour_layout = QVBoxLayout()
        hour_label = QLabel(text="Hour: ")
        hour_layout.addWidget(hour_label)
        hour_layout.addWidget(self.hour_edit)
        top_layout.addLayout(hour_layout)
        minute_layout = QVBoxLayout()
        minute_label = QLabel(text="Minute: ")
        minute_layout.addWidget(minute_label)
        minute_layout.addWidget(self.minute_edit)
        top_layout.addLayout(minute_layout)
        crawler_layout = QVBoxLayout()
        crawler_label = QLabel(text="Crawler: ")
        crawler_layout.addWidget(crawler_label)
        crawler_layout.addWidget(self.crawler_combobox)
        top_layout.addLayout(crawler_layout)
        top_layout.setStretch(0, 2)
        top_layout.setStretch(1, 2)
        top_layout.setStretch(2, 2)
        top_layout.setStretch(3, 2)
        top_layout.setStretch(4, 3)

        ## bottom layout, 确定/取消
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.confirm_button)
        bottom_layout.addWidget(self.cancel_button)

        ## 设置字体
        button_font = QtGui.QFont()
        button_font.setFamily("Roman times")
        button_font.setPointSize(10)
        self.confirm_button.setFont(button_font)
        self.cancel_button.setFont(button_font)
        combobox_font = QtGui.QFont()
        combobox_font.setFamily("微软雅黑")
        combobox_font.setPointSize(10)
        self.crawler_combobox.setFont(combobox_font)
        label_font = QtGui.QFont()
        label_font.setFamily("Roman times")
        label_font.setPointSize(9)
        month_label.setFont(label_font)
        day_label.setFont(label_font)
        hour_label.setFont(label_font)
        minute_label.setFont(label_font)
        crawler_label.setFont(label_font)

        ## 设置高度
        self.crawler_combobox.setFixedHeight(25)
        self.month_edit.setFixedHeight(25)
        self.day_edit.setFixedHeight(25)
        self.hour_edit.setFixedHeight(25)
        self.minute_edit.setFixedHeight(25)

        self.setLayout(root_layout)

    def combobox_init(self):
        self.crawler_combobox.addItems(['fossdroid', 'xiaomi', 'apkpure', 'github'])
        self.crawler_combobox.setStyleSheet("QComboBox{background:white;border: 0.5px solid black}")

    def emit(self):
        month = int(self.month_edit.text())
        month = -1 if month <= 0 or month > 12 else month
        day = int(self.day_edit.text())
        day = -1 if day <= 0 or day > 31 else day
        hour = int(self.hour_edit.text())
        hour = -1 if day < 0 or hour >= 24 else hour
        minute = int(self.minute_edit.text())
        minute = -1 if minute < 0 or minute >= 60 else minute
        crawler = self.crawler_combobox.currentText()
        self.close()
        self.timer_signal.emit(month, day, hour, minute, crawler)

    def event_init(self):
        self.cancel_button.clicked.connect(self.reject)
        self.confirm_button.clicked.connect(self.emit)

    def edit_init(self):
        self.month_edit.setText("0")
        self.day_edit.setText("0")
        self.hour_edit.setText("-1")
        self.minute_edit.setText("-1")
        self.month_edit.setValidator(QtGui.QIntValidator())  # 0 means no setting
        self.day_edit.setValidator(QtGui.QIntValidator())  # 0 means no setting
        self.hour_edit.setValidator(QtGui.QIntValidator())  # -1 means no setting
        self.minute_edit.setValidator((QtGui.QIntValidator()))  # -1 means no setting


class CrawlerGUI(QWidget):
    # Main GUI for crawler module.

    def __init__(self):
        super().__init__()
        self.third_tree = QListView()
        self.second_tree = QListView()
        self.first_tree = QListView()
        self._keep_the_end_ = True
        self.database_thread = DatabaseThread()
        self.markets = None
        self.apps = None
        self.updates = None

        self.root_layout = None
        self.crawler_combobox = QComboBox()
        self.start_crawl_button = QPushButton("Start")
        self.stop_crawl_button = QPushButton("Stop")
        self.add_timer_button = QPushButton("Add Timer")
        self.delete_timer_button = QPushButton("Del Timer")
        self.crawler_log_text = QTextBrowser()
        self.timer_table = QTableWidget()
        self.apk_info_text = QTextBrowser()
        self.add_apk_button = QPushButton("Import APK From Folder ...")
        self.add_apk_progress_bar = QProgressBar()
        self.delete_apk_button = QPushButton("Delete")
        self.delete_from_folder_button = QPushButton("")

        # scrapy
        self.scrapy_worker = ScrapyWorker()

        # timer window
        self.timer_window = TimerGUI()

        self.layout_init()
        self.combobox_init()
        self.event_init()
        self.table_init()

    @QtCore.pyqtSlot(str)
    def parse_log(self, text):
        pre_cursor = self.crawler_log_text.textCursor()
        self.crawler_log_text.moveCursor(QtGui.QTextCursor.End)
        self.crawler_log_text.insertPlainText(text)
        if self._keep_the_end_:
            pre_cursor.movePosition(QtGui.QTextCursor.End)
        self.crawler_log_text.setTextCursor(pre_cursor)

    def scrapy_finish(self):
        self.parse_log("Scrapy Worker Done!")
        self.start_crawl_button.setVisible(True)
        self.stop_crawl_button.setVisible(False)

    def layout_init(self):
        # 整体大小
        height = 850
        width = 1400
        self.setFixedSize(width, height)
        self.setWindowTitle("Crawler GUI")

        # 组件布局
        ## 顶层上下布局
        root_layout = QVBoxLayout()
        top_layout = QGridLayout()
        bottom_layout = QHBoxLayout()
        root_layout.addLayout(top_layout)
        root_layout.addLayout(bottom_layout)

        ## top_layout 左右分别布局爬虫模块和 util模块
        crawler_group_box = QGroupBox(title="APK Crawler")
        crawler_layout = QVBoxLayout()
        crawler_layout.setObjectName("crawler layout")
        util_group_box = QGroupBox(title="Crawler Util")
        util_layout = QVBoxLayout()
        util_layout.setObjectName("util layout")
        crawler_group_box.setLayout(crawler_layout)
        util_group_box.setLayout(util_layout)
        top_layout.addWidget(crawler_group_box, 0, 0)
        top_layout.addWidget(util_group_box, 0, 1)
        top_layout.setColumnStretch(0, 3)
        top_layout.setColumnStretch(1, 2)

        ## bottom_layout 左右布局: 平台、软件、版本，详情描述
        file_system_group_box = QGroupBox(title="APK Dataset")
        file_system_layout = QHBoxLayout()
        file_system_group_box.setLayout(file_system_layout)
        file_system_layout.addWidget(self.first_tree)
        file_system_layout.addWidget(self.second_tree)
        file_system_layout.addWidget(self.third_tree)
        file_system_layout.addWidget(self.apk_info_text)
        file_system_layout.setStretch(0, 2)
        file_system_layout.setStretch(1, 8)
        file_system_layout.setStretch(2, 3)
        file_system_layout.setStretch(3, 12)
        bottom_layout.addWidget(file_system_group_box)

        ### 爬虫模块布局 上下布局
        crawler_top_layout = QHBoxLayout()
        crawler_top_layout.addWidget(self.crawler_combobox)
        crawler_top_layout.addStretch()
        crawler_top_layout.addWidget(self.start_crawl_button)
        crawler_top_layout.addWidget(self.stop_crawl_button)
        crawler_layout.addLayout(crawler_top_layout)
        crawler_layout.addWidget(self.crawler_log_text)

        ### util 模块上下分别布局 按钮模组、计时器列表、添加apk按钮
        util_button_layout = QHBoxLayout()
        util_button_layout.addWidget(self.add_timer_button)
        util_button_layout.addWidget(self.delete_timer_button)
        util_button_layout.addStretch()
        util_layout.addLayout(util_button_layout)
        util_layout.addWidget(self.timer_table)
        util_layout.addStretch()
        util_layout.addWidget(self.add_apk_button)
        util_layout.addWidget(self.add_apk_progress_bar)

        # 组件字体
        component_font = QtGui.QFont()
        component_font.setFamily("Roman times")
        component_font.setPointSize(11)
        self.crawler_combobox.setFont(component_font)
        self.start_crawl_button.setFont(component_font)
        self.stop_crawl_button.setFont(component_font)
        self.add_timer_button.setFont(component_font)
        self.delete_timer_button.setFont(component_font)
        self.add_apk_button.setFont(component_font)

        # crawler combobox 设置
        self.crawler_combobox.setStyleSheet("QComboBox{padding:5px}")

        # 隐藏stop button
        self.stop_crawl_button.setVisible(False)

        # 设置进度条
        self.add_apk_progress_bar.setVisible(False)
        self.add_apk_progress_bar.setFixedHeight(20)

        # QGroupBox 标题大小
        group_box_font = QtGui.QFont()
        group_box_font.setFamily("微软雅黑")
        group_box_font.setPointSize(9)
        crawler_group_box.setFont(group_box_font)
        util_group_box.setFont(group_box_font)

        # log, progress 字体
        log_font = QtGui.QFont()
        log_font.setFamily("Consolas")
        log_font.setPointSize(9)
        self.crawler_log_text.setFont(log_font)
        self.add_apk_progress_bar.setFont(log_font)

        # button大小
        button_size_1 = (80, 25)
        self.start_crawl_button.setFixedSize(*button_size_1)
        self.stop_crawl_button.setFixedSize(*button_size_1)
        button_size_2 = (112, 25)
        self.add_timer_button.setFixedSize(*button_size_2)
        self.delete_timer_button.setFixedSize(*button_size_2)

        # 爬虫选择框大小
        self.crawler_combobox.setFixedSize(200, 25)

        self.setLayout(root_layout)
        self.root_layout = root_layout

    def first_tree_click(self):
        current_row_index = self.first_tree.currentIndex().row()
        self.database_thread.get_app(self.markets[current_row_index]["market_id"])

    def second_tree_click(self):
        current_row_index = self.second_tree.currentIndex().row()
        self.database_thread.get_updates(self.apps[current_row_index]["app_id"])

    def third_tree_click(self):
        current_row_index = self.third_tree.currentIndex().row()
        self.database_thread.get_information_from_update_id(self.updates[current_row_index]['update_id'])

    def update_platform(self, markets):
        platform_model = QStandardItemModel()
        icon_path = os.path.join(__current_folder_path__, "./images/folder.png")
        for market in markets:
            platform_model.appendRow(QStandardItem(QIcon(icon_path), market['market_name']))
        self.markets = markets
        self.first_tree.setModel(platform_model)

    def update_apps(self, apps):
        app_model = QStandardItemModel()
        icon_path = os.path.join(__current_folder_path__, "./images/android.png")
        for app in apps:
            app_model.appendRow(QStandardItem(QIcon(icon_path), app['app_title']))
        self.apps = apps
        self.second_tree.setModel(app_model)
        self.second_tree.scrollTo(app_model.index(0, 0))

    def update_updates(self, updates):
        update_model = QStandardItemModel()
        icon_path = os.path.join(__current_folder_path__, "./images/version.png")
        for update in updates:
            version = update['version'].split('.apk')[0] if update['version'].endswith('.apk') else update['version']
            version = update['version'].split('.xapk')[0] if update['version'].endswith('.xapk') else version
            update_model.appendRow(QStandardItem(QIcon(icon_path), version))
        self.updates = updates
        self.third_tree.setModel(update_model)
        self.third_tree.scrollTo(update_model.index(0, 0))

    def update_information(self, information):
        print(information)

    def event_init(self):
        # crawler
        self.start_crawl_button.clicked.connect(self.start_on_click)
        self.stop_crawl_button.clicked.connect(self.stop_on_click)

        # scrapy worker
        self.scrapy_worker.logChanged.connect(self.parse_log)
        self.scrapy_worker.started.connect(self.crawler_log_text.clear)
        self.scrapy_worker.finished.connect(self.scrapy_finish)

        # timer
        self.timer_window.setWindowModality(QtCore.Qt.ApplicationModal)
        self.timer_window.timer_signal.connect(self.add_new_timer)
        self.add_timer_button.clicked.connect(self.add_timer_click)

        # file system
        self.database_thread.platform_signal.connect(self.update_platform)
        self.database_thread.get_platform()
        self.first_tree.clicked.connect(self.first_tree_click)
        self.database_thread.app_signal.connect(self.update_apps)
        self.second_tree.clicked.connect(self.second_tree_click)
        self.database_thread.update_signal.connect(self.update_updates)
        self.third_tree.clicked.connect(self.third_tree_click)
        self.database_thread.information_signal.connect(self.update_information)
        self.first_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.second_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.third_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def add_timer_click(self):
        self.timer_window.show()
        self.timer_window.exec_()

    def start_on_click(self):
        platform = self.crawler_combobox.currentText()
        self.stop_crawl_button.setVisible(True)
        self.start_crawl_button.setVisible(False)
        # start scrapy
        self.scrapy_worker.run(platform)

    def stop_on_click(self):
        self.stop_crawl_button.setVisible(False)
        self.start_crawl_button.setVisible(True)
        # stop scrapy
        self.scrapy_worker.stop()

    def combobox_init(self):
        self.crawler_combobox.addItems(["fossdroid", "xiaomi", "apkpure", "github"])
        self.crawler_combobox.setStyleSheet("ComboBox{background: white; border: 0.5px solid black;}")

    def table_init(self):
        self.timer_table.setColumnCount(5)
        self.timer_table.setHorizontalHeaderLabels(['Month', "Day", "Hour", "Minute", "Crawler"])
        self.timer_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.timer_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.timer_table.verticalHeader().setVisible(False)
        self.timer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.show_timer()

    def show_timer(self):
        # todo: 如何更新界面
        if platform.system() == "Windows":
            print("Not imply in windows.")
        else:
            user_crontab = CronTab(user=True)
            job_iter = user_crontab.find_comment("apk merge crawler")
            jobs = []
            table_data = [
                ["12", "31", "23", "11", "huawei"],
                ["12", "31", "23", "22", "github"]
            ]
            for job in job_iter:  # type: CronItem
                month = job.month
                day = job.day
                hour = job.hour
                minute = job.minute
                command = job.command  # type: str
                crawler = command.split("--market_name")[1].strip()
                jobs.append(job)
                table_data.append([month, day, hour, minute, crawler])

            self.timer_table.setRowCount(0)
            for _x_item_ in table_data:
                row = self.timer_table.rowCount()
                self.timer_table.insertRow(row)
                for _column_ in range(5):
                    item = QTableWidgetItem(str(_x_item_[_column_]))
                    self.timer_table.setItem(row, _column_, item)

    def add_new_timer(self, month, day, hour, minute, crawler_name):
        # todo: 修改这个逻辑
        if month == -1 and day == -1 and hour == -1 and minute == -1:
            QMessageBox.warning(self, "Wrong Timer Setting", "You set a wrong timer, please check it carefully.", QMessageBox.Ok, QMessageBox.Ok)
            return
        # todo: 添加新的定时任务
        if month != -1:
            month = "*"
        if day != -1:
            day = "*"
        if hour != -1:
            hour = "*"
        if minute == -1:
            minute = "*"

        if platform.system() == "Windows":
            print("Not imply in windows.")
        else:
            crawler_script_path = os.path.join(__current_folder_path__, "main.py")
            crontab_command = "python3 {} --market_name {}".format(minute, hour, day, month, crawler_script_path, crawler_name)
            crontab_time = "{} {} {} {} *".format(minute, hour, day, month)
            comment = "apk merge crawler"
            user_crontab = CronTab(user=True)
            job = user_crontab.new(command=crontab_command, comment=comment)
            job.setall(crontab_time)
            job.enable()
            user_crontab.write()


class DatabaseThread(QThread):
    platform_signal = QtCore.pyqtSignal(list)
    app_signal = QtCore.pyqtSignal(list)
    update_signal = QtCore.pyqtSignal(list)
    information_signal = QtCore.pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.db = Database()

    def get_platform(self) -> None:
        markets = self.db.get_all_market()
        self.platform_signal.emit(markets)

    def get_app(self, market_id) -> None:
        apps = self.db.get_all_app(market_id)
        self.app_signal.emit(apps)

    def get_updates(self, app_id) -> None:
        updates = self.db.get_all_updates(app_id)
        self.update_signal.emit(updates)

    def get_information_from_update_id(self, update_id) -> None:
        information = self.db.get_information_from_update_id(update_id)
        self.information_signal.emit(information)


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
    crawler_gui = CrawlerGUI()
    crawler_gui.show()
    sys.exit(app.exec_())
