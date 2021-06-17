# coding=utf-8
import os
import platform
import typing

from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

if platform.system() == "Windows":
    from PyQt5 import sip
else:
    import sip
__current_folder_path__ = os.path.dirname(os.path.abspath(__file__))

from settings import DEFAULT_DEVELOPER, DEFAULT_VERSION, DEFAULT_CATEGORY, DEFAULT_SIZE

BUTTON_HEIGHT = 25


class CrawlerGUI(QWidget):
    # Main GUI for crawler module.

    def __init__(self):
        super(CrawlerGUI).__init__()
        self.root_layout_init()

    def root_layout_init(self):
        # 整体大小
        height = 890
        width = 1400
        self.setFixedSize(width, height)
        self.setWindowTitle("Crawler GUI")

        # 设置字体
        self.setFont(QFont("Microsoft YaHei", 8.5))

        # set layout
        root_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        body_widget = QGroupBox(title="Search Condition")
        bottom_widget = QGroupBox(title="File Database")
        root_layout.addLayout(top_layout)
        root_layout.addWidget(body_widget)
        root_layout.addWidget(bottom_widget)
        root_layout.setStretch(0, 12)
        root_layout.setStretch(1, 1)
        root_layout.setStretch(2, 15)

        # save the value
        self.root_layout = root_layout
        self.top_layout = top_layout
        self.body_widget = body_widget
        self.bottom_widget = bottom_widget

        # init the sub layout
        self.top_layout_init()
        self.body_widget_init()
        self.bottom_widget_init()

        # show
        self.setLayout(root_layout)

    def top_layout_init(self):
        # set layout
        crawler_widget = QGroupBox(title="APK Crawler")
        util_widget = QGroupBox(title="Crawler Util")
        self.top_layout.addWidget(crawler_widget)
        self.top_layout.addWidget(util_widget)
        self.top_layout.setStretch(0, 3)
        self.top_layout.setStretch(1, 2)

        # save the value
        self.crawler_widget = crawler_widget
        self.util_widget = util_widget

        # init the sub layout
        self.crawler_widget_init()
        self.util_widget_init()

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
        add_apk_layout = QVBoxLayout()
        util_layout.addLayout(add_apk_layout)
        self.util_widget.setLayout(util_layout)

        # save the value
        self.util_layout = util_layout
        self.util_button_layout = util_button_layout
        self.timer_table_widget = timer_table_widget
        self.add_apk_layout = add_apk_layout

        # init the sub layout
        self.util_button_layout_init()
        self.timer_table_widget_init()
        self.add_apk_layout_init()

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

    def body_widget_init(self):
        # set the layout
        search_condition_layout = QHBoxLayout()
        sdk_level_layout = QVBoxLayout()
        authority_layout = QVBoxLayout()
        type_layout = QVBoxLayout()
        search_button_layout = QVBoxLayout()

        search_condition_layout.addLayout(sdk_level_layout)
        search_condition_layout.addSpacing(20)
        search_condition_layout.addLayout(authority_layout)
        search_condition_layout.addSpacing(20)
        search_condition_layout.addLayout(type_layout)
        search_condition_layout.addSpacing(40)
        search_condition_layout.addLayout(search_button_layout)
        search_condition_layout.addStretch()
        self.body_widget.setLayout(search_condition_layout)

        # save the value
        self.search_condition_layout = search_condition_layout
        self.sdk_level_layout = sdk_level_layout
        self.authority_layout = authority_layout
        self.type_layout = type_layout
        self.search_button_layout = search_button_layout

        # init the sub layout
        self.sdk_level_layout_init()
        self.authority_layout_init()
        self.type_layout_init()
        self.search_button_layout_init()

    def sdk_level_layout_init(self):
        # set the layout
        sdk_label = QLabel("SDK Level :")
        sdk_combobox = ComboCheckBox()
        sdk_combobox.setFixedHeight(BUTTON_HEIGHT)
        self.sdk_level_layout.addWidget(sdk_label)
        self.sdk_level_layout.addWidget(sdk_combobox)

        # save the value
        self.sdk_label = sdk_label
        self.sdk_combobox = sdk_combobox

    def authority_layout_init(self):
        # set the layout
        authority_label = QLabel("Permission : ")
        authority_combobox = ComboCheckBox()
        authority_combobox.setFixedHeight(BUTTON_HEIGHT)
        self.authority_layout.addWidget(authority_label)
        self.authority_layout.addWidget(authority_combobox)

        # save the value
        self.authority_label = authority_label
        self.authority_combobox = authority_combobox

    def type_layout_init(self):
        # set the layout
        type_label = QLabel("APP Type : ")
        type_combobox = ComboCheckBox()
        type_combobox.setFixedHeight(BUTTON_HEIGHT)
        type_combobox.setFixedWidth(180)
        self.type_layout.addWidget(type_label)
        self.type_layout.addWidget(type_combobox)

        # save the value
        self.type_label = type_label
        self.type_combobox = type_combobox

    def search_button_layout_init(self):
        # set the layout
        search_button = QPushButton(
            QIcon(os.path.join(__current_folder_path__, "./images/search.png")), "Search"
        )
        search_button.setFixedHeight(BUTTON_HEIGHT)
        self.search_button_layout.addStretch()
        self.search_button_layout.addWidget(search_button)

        # save the value
        self.search_button = search_button

    def bottom_widget_init(self):
        # set layout
        file_system_layout = QHBoxLayout()
        first_file_tree = QListView()
        second_file_tree = QListView()
        third_file_layout = QVBoxLayout()
        apk_info_scroll_area = DragScrollArea()
        apk_info_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        file_system_layout.addWidget(first_file_tree)
        file_system_layout.addWidget(second_file_tree)
        file_system_layout.addLayout(third_file_layout)
        file_system_layout.addWidget(apk_info_scroll_area)
        file_system_layout.setStretch(0, 2)
        file_system_layout.setStretch(1, 8)
        file_system_layout.setStretch(2, 3)
        file_system_layout.setStretch(3, 12)
        self.bottom_widget.setLayout(file_system_layout)

        # save the value
        self.file_system_layout = file_system_layout
        self.first_file_tree = first_file_tree
        self.second_file_tree = second_file_tree
        self.third_file_layout = third_file_layout
        self.apk_info_scroll_area = apk_info_scroll_area

        # init the sub layout
        self.third_file_layout_init()
        self.apk_info_scroll_area_init()

    def third_file_layout_init(self):
        # set layout
        third_file_tree = QListView()
        delete_apk_button = QPushButton("Delete APK")
        delete_apk_button.setFixedHeight(BUTTON_HEIGHT)
        delete_from_folder_button = QPushButton("Delete APKs From Folder")
        delete_progress_bar = QProgressBar()
        delete_progress_bar.setObjectName("RedProgressBar")
        delete_progress_bar.setStyleSheet(ProgressBarStyleSheet)
        delete_progress_bar.setVisible(False)
        delete_from_folder_button.setFixedHeight(BUTTON_HEIGHT)
        self.third_file_layout.addWidget(third_file_tree)
        self.third_file_layout.addWidget(delete_apk_button)
        self.third_file_layout.addWidget(delete_from_folder_button)
        self.third_file_layout.addWidget(delete_progress_bar)

        # save the value
        self.third_file_tree = third_file_tree
        self.delete_apk_button = delete_apk_button
        self.delete_from_folder_button = delete_from_folder_button
        self.delete_progress_bar = delete_progress_bar

    def apk_info_scroll_area_init(self):
        # set the layout
        apk_info_widget = QWidget()
        apk_info_layout = QVBoxLayout()
        apk_info_widget.setLayout(apk_info_layout)
        widget_style = QPalette()
        widget_style.setColor(QPalette.Background, QtCore.Qt.white)
        apk_info_widget.setPalette(widget_style)
        apk_info_widget.setContentsMargins(0, 0, 0, 0)
        self.apk_info_scroll_area.setWidget(apk_info_widget)
        self.apk_info_scroll_area.setWidgetResizable(True)

        # save the value
        self.apk_info_widget = apk_info_widget
        self.apk_info_layout = apk_info_layout

    def clear_apk_info_layout(self):
        for _i_ in range(self.apk_info_layout.count()):
            tmp_widget = self.apk_info_layout.itemAt(_i_).widget()
            tmp_widget.deleteLater()
            sip.delete(tmp_widget)


class TimerGUI(QDialog):
    # Timer GUI for adding new timer
    timer_signal = QtCore.pyqtSignal(int, int, int, int, str)  # month, day, hour, minute, week_day, crawler

    def __init__(self):
        super(TimerGUI, self).__init__()

        self.jobs = []
        self.crawler_combobox = QComboBox()
        # self.crawler_combobox.setStyleSheet("QComboBox{background:white;border: 0.5px solid black}")
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setFixedHeight(BUTTON_HEIGHT)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedHeight(BUTTON_HEIGHT)
        self.minute_edit = QLineEdit()
        self.hour_edit = QLineEdit()
        self.day_edit = QLineEdit()
        self.month_edit = QLineEdit()

        self.edit_init()
        self.layout_init()
        self.reset_edit()
        self.event_init()

    def layout_init(self):
        width = 500
        height = 120
        self.setFixedSize(width, height)
        self.setWindowTitle("Add New Timer")

        # root layout, 上下布局
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()
        root_layout = QVBoxLayout()
        root_layout.addLayout(top_layout)
        root_layout.addStretch()
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
        top_layout.setStretch(4, 2)
        top_layout.setStretch(5, 3)

        ## bottom layout, 确定/取消
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.confirm_button)
        bottom_layout.addWidget(self.cancel_button)

        ## 设置高度
        self.crawler_combobox.setFixedHeight(25)
        self.month_edit.setFixedHeight(25)
        self.day_edit.setFixedHeight(25)
        self.hour_edit.setFixedHeight(25)
        self.minute_edit.setFixedHeight(25)

        self.setLayout(root_layout)

    def load_crawler(self, crawler_name_list):
        self.crawler_combobox.addItems(crawler_name_list)

    def emit(self):
        month = int(self.month_edit.text())
        if month < -1 or month > 12:
            QMessageBox().critical(self, "Wrong Month", "Invalid Month. Please set month as [1, 12], and 0/-1 means no setting for month.")
            return
        month = -1 if month <= 0 else month

        day = int(self.day_edit.text())
        if day < -1 or day > 31:
            QMessageBox().critical(self, "Wrong Day", "Invalid Day. Please set day as [1, 31], and 0/-1 means no setting for day.")
        day = -1 if day <= 0 else day

        hour = int(self.hour_edit.text())
        if hour < -1 or hour >= 24:
            QMessageBox().critical(self, "Wrong Hour", "Invalid Hour. Please set hour as [0, 23], and -1 means no setting for hour.")
        hour = -1 if day < 0 else hour

        minute = int(self.minute_edit.text())
        if minute < -1 or minute >= 60:
            QMessageBox().critical(self, "Wrong Minute", "Invalid Minute. Please set minute as [0, 59], and -1 means no setting for minute.")
        minute = -1 if minute < 0 else minute

        crawler = self.crawler_combobox.currentText()
        self.close()
        self.timer_signal.emit(month, day, hour, minute, crawler)

    def event_init(self):
        self.cancel_button.clicked.connect(self.reject)
        self.confirm_button.clicked.connect(self.emit)

    def reset_edit(self):
        self.month_edit.setText("-1")
        self.day_edit.setText("-1")
        self.hour_edit.setText("-1")
        self.minute_edit.setText("-1")

    def edit_init(self):
        self.month_edit.setValidator(QtGui.QIntValidator(-1, 12))  # 0 means no setting
        self.day_edit.setValidator(QtGui.QIntValidator(-1, 31))  # 0 means no setting
        self.hour_edit.setValidator(QtGui.QIntValidator(-1, 23))  # -1 means no setting
        self.minute_edit.setValidator(QtGui.QIntValidator(-1, 59))  # -1 means no setting


class TextLabel(QLabel):
    def __init__(self, text):
        super(TextLabel, self).__init__(text)
        self.setStyleSheet("border: 0px; margin-right: 5px; font-weight: bold; font-size: 12px;")
        self.setFixedWidth(95)
        self.setFixedHeight(30)
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(QtCore.Qt.AlignBottom)


class TextSpan(QLabel):
    def __init__(self, text):
        super(TextSpan, self).__init__(text)
        self.setStyleSheet("border: 0px; font-weight: normal; margin-right: 5px; border-bottom: 1px solid #888; font-size: 12px;")
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFixedWidth(195)
        self.setFixedHeight(30)
        self.setContentsMargins(0, 0, 0, 0)


class TextHash(QLabel):
    def __init__(self, text):
        super(TextHash, self).__init__(text)
        self.setStyleSheet("border: 0px; font-weight: normal; margin-right: 5px; border-bottom: 1px solid #888; color: green; font-weight: bold; font-size: 12px;")
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFixedHeight(30)
        self.setContentsMargins(0, 0, 0, 0)


class TextHref(QLabel):
    def __init__(self, text, href):
        super(TextHref, self).__init__('<a href="{}">{}</a>'.format(href, text))
        self.setStyleSheet("border: 0px; font-weight: normal; margin-right: 5px; font-size: 12px;")
        self.setOpenExternalLinks(True)
        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)
        self.setFixedWidth(195)
        self.setFixedHeight(30)
        self.setContentsMargins(0, 0, 0, 0)


class ComboCheckBox(QComboBox):
    def __init__(self, parent=None):
        super(ComboCheckBox, self).__init__(parent)
        self.setFixedWidth(150)
        self.row_num = 0

    def addItems(self, texts: typing.Iterable[str]) -> None:
        self.items = list(texts)
        self.items.insert(0, 'Select ALL')
        self.row_num = len(self.items)
        self.selected_row_num = 0
        self.qCheckBox = []
        self.qLineEdit = QLineEdit()
        self.qLineEdit.setReadOnly(True)
        self.qListWidget = QListWidget()
        self.addQCheckBox(0)
        self.qCheckBox[0].stateChanged.connect(self.All)
        for i in range(1, self.row_num):
            self.addQCheckBox(i)
            self.qCheckBox[i].stateChanged.connect(self.show)
        self.setModel(self.qListWidget.model())
        self.setView(self.qListWidget)
        self.setLineEdit(self.qLineEdit)

    def addQCheckBox(self, i):
        self.qCheckBox.append(QCheckBox())
        qItem = QListWidgetItem(self.qListWidget)
        self.qCheckBox[i].setText(self.items[i])
        self.qListWidget.setItemWidget(qItem, self.qCheckBox[i])

    def get_select_text(self):
        text_list = []
        for i in range(1, self.row_num):
            if self.qCheckBox[i].isChecked():
                text_list.append(self.qCheckBox[i].text())
        self.selected_row_num = len(text_list)
        return text_list

    def get_select_index(self):
        index_list = []
        for i in range(1, self.row_num):
            if self.qCheckBox[i].isChecked():
                index_list.append(i - 1)
        return index_list

    def show(self):
        show = ''
        text_list = self.get_select_text()
        self.qLineEdit.setReadOnly(False)
        self.qLineEdit.clear()
        for i in text_list:
            show += i + ' ; '
        if self.selected_row_num == 0:
            self.qCheckBox[0].setCheckState(0)
        elif self.selected_row_num == self.row_num - 1:
            self.qCheckBox[0].setCheckState(2)
        else:
            self.qCheckBox[0].setCheckState(1)
        self.qLineEdit.setText(show)
        self.qLineEdit.setReadOnly(True)

    def All(self, status):
        if status == 2:
            for i in range(1, self.row_num):
                self.qCheckBox[i].setChecked(True)
        elif status == 1:
            if self.selected_row_num == 0:
                self.qCheckBox[0].setCheckState(2)
        elif status == 0:
            self.clear()

    def clear(self):
        for i in range(self.row_num):
            self.qCheckBox[i].setChecked(False)


class InformationWidget(QWidget):
    def __init__(self):
        super(InformationWidget, self).__init__()
        self.information_layout = QVBoxLayout()
        self.information_layout.setContentsMargins(0, 0, 0, 0)
        self.setObjectName("information_layout")
        self.setStyleSheet("information_layout{border-bottom: 2px solid black;}")
        self.setLayout(self.information_layout)
        self.setContentsMargins(0, 0, 0, 0)

    def load_data(self, information):
        layout_1 = QHBoxLayout()
        text_label = QLabel("APK Information")
        text_label.setFont(QFont("Arial", 14))
        text_label.setFixedHeight(40)
        layout_1.addWidget(text_label)
        self.information_layout.addLayout(layout_1)

        layout_2 = QHBoxLayout()
        text_label = TextLabel("App Title : ")
        text_line = TextSpan(information['app_title'])
        layout_2.addWidget(text_label)
        layout_2.addWidget(text_line)
        layout_2.addStretch()
        text_label = TextLabel("Apk Name : ")
        layout_2.addWidget(text_label)
        text_line = TextSpan(information['apk_name'])
        layout_2.addWidget(text_line)
        self.information_layout.addLayout(layout_2)
        self.information_layout.addSpacing(5)

        layout_3 = QHBoxLayout()
        text_label = TextLabel("Market : ")
        text_line = TextSpan(information['market_name'])
        layout_3.addWidget(text_label)
        layout_3.addWidget(text_line)
        layout_3.addStretch()
        text_label = TextLabel("Developer : ")
        text_line = TextSpan(information['developer_name'])
        if information['developer_name'] == DEFAULT_DEVELOPER:
            text_line.setStyleSheet(text_line.styleSheet() + "color: grey;")
        layout_3.addWidget(text_label)
        layout_3.addWidget(text_line)
        self.information_layout.addLayout(layout_3)
        self.information_layout.addSpacing(5)

        layout_4 = QHBoxLayout()
        text_label = TextLabel("Version : ")
        text_line = TextSpan(information['version'] or DEFAULT_VERSION)
        if not text_line or information['version'] == DEFAULT_VERSION:
            text_line.setStyleSheet(text_line.styleSheet() + "color: grey;")
        layout_4.addWidget(text_label)
        layout_4.addWidget(text_line)
        layout_4.addStretch()
        text_label = TextLabel("Update Date : ")
        text_line = TextSpan(information['update_date'] or "UNKNOWN_DATE")
        if not information['update_date']:
            text_line.setStyleSheet(text_line.styleSheet() + "color: grey;")
        layout_4.addWidget(text_label)
        layout_4.addWidget(text_line)
        self.information_layout.addLayout(layout_4)
        self.information_layout.addSpacing(5)

        layout41 = QHBoxLayout()
        text_label = TextLabel("Type : ")
        text_line = TextSpan(information['type_name'] or DEFAULT_CATEGORY)
        if information['type_name'] is None or information['type_name'] == DEFAULT_CATEGORY:
            text_line.setStyleSheet(text_line.styleSheet() + "color: grey;")
        layout41.addWidget(text_label)
        layout41.addWidget(text_line)
        layout41.addStretch()
        text_label = TextLabel("Delete : ")
        text_line = TextSpan("Not Deleted" if not information['is_delete'] else "Deleted")
        if information['is_delete']:
            text_line.setStyleSheet(text_line.styleSheet() + "color: red;")
        else:
            text_line.setStyleSheet(text_line.styleSheet() + "color: green;")
        layout41.addWidget(text_label)
        layout41.addWidget(text_line)
        self.information_layout.addLayout(layout41)
        self.information_layout.addSpacing(5)

        layout42 = QHBoxLayout()
        text_label = TextLabel("SDK Level : ")
        text_line = TextSpan(information['sdk_level'] if information['sdk_level'] else "UNKNOWN_SDK")
        if not information['sdk_level']:
            text_line.setStyleSheet(text_line.styleSheet() + "color: grey;")
        layout42.addWidget(text_label)
        layout42.addWidget(text_line)
        layout42.addStretch()
        text_label = TextLabel("Malware : ")
        text_line = TextSpan("Malware" if information['malware'] else "UNKNOWN")
        if information['malware']:
            text_line.setStyleSheet(text_line.styleSheet() + "color: red;")
        else:
            text_line.setStyleSheet(text_line.styleSheet() + "color: grey;")
        layout42.addWidget(text_label)
        layout42.addWidget(text_line)
        self.information_layout.addLayout(layout42)
        self.information_layout.addSpacing(5)

        layout43 = QHBoxLayout()
        text_label = TextLabel("Download : ")
        text_line = TextSpan("Downloaded" if information['is_download'] else "Not Downloaded")
        if information['is_download']:
            text_line.setStyleSheet(text_line.styleSheet() + "color: green;")
        else:
            text_line.setStyleSheet(text_line.styleSheet() + "color: red;")
        layout43.addWidget(text_label)
        layout43.addWidget(text_line)
        layout43.addStretch()
        text_label = TextLabel("Size : ")
        text_line = TextSpan(information['size'] if information['size'] else DEFAULT_SIZE)
        if not information['size'] or information['size'] == DEFAULT_SIZE:
            text_line.setStyleSheet(text_line.styleSheet() + "color: grey;")
        layout43.addWidget(text_label)
        layout43.addWidget(text_line)
        self.information_layout.addLayout(layout43)
        self.information_layout.addSpacing(5)

        layout44 = QHBoxLayout()
        text_label = TextLabel("APK Hash : ")
        if not information['hash']:
            text_line = TextSpan("UNKNOWN_HASH")
            text_line.setStyleSheet(text_line.styleSheet() + "color: grey;")
        else:
            text_line = TextHash(information['hash'])
        layout44.addWidget(text_label)
        layout44.addWidget(text_line)
        if not information['hash']:
            layout44.addStretch()
        self.information_layout.addLayout(layout44)
        self.information_layout.addSpacing(5)

        layout_5 = QHBoxLayout()
        text_label = TextLabel("App Link : ")
        text_line = TextHref("Open Link", information['app_href'])
        layout_5.addWidget(text_label)
        layout_5.addWidget(text_line)
        layout_5.addStretch()
        text_label = TextLabel("Download Link : ")
        text_line = TextHref("Open Link", information['download_href'])
        layout_5.addWidget(text_label)
        layout_5.addWidget(text_line)
        self.information_layout.addLayout(layout_5)
        self.information_layout.addSpacing(5)

        if information.get('image_file_list') and len(information['image_file_list']):
            layout_6 = QVBoxLayout()
            text_label = TextLabel("Images : ")
            layout_6.addWidget(text_label)

            image_list_scroll_area = QScrollArea()
            image_list_widget = QWidget()
            image_list_layout = QHBoxLayout()
            image_list_scroll_area.setWidget(image_list_widget)
            image_list_scroll_area.setWidgetResizable(True)
            image_list_widget.setLayout(image_list_layout)
            for image_file in information['image_file_list']:
                image_label = QLabel()
                image_pixmap = QPixmap(image_file)
                image_pixmap.scaledToHeight(200)
                image_label.setPixmap(image_pixmap)
                image_list_layout.addWidget(image_label)
            image_list_scroll_area.setMinimumHeight(374)
            image_list_scroll_area.setContentsMargins(0, 0, 0, 0)
            image_list_layout.setContentsMargins(0, 0, 0, 0)
            layout_6.addWidget(image_list_scroll_area)

            self.information_layout.addLayout(layout_6)
            self.information_layout.addSpacing(5)

        if information.get("description") and information['description'] != "":
            layout_7 = QVBoxLayout()
            text_label = TextLabel("Description : ")
            text_browser = QTextBrowser()
            text_browser.setFont(QFont("Consolas", 10))
            text_browser.setText(information['description'])
            text_browser.document().adjustSize()
            text_browser.setFixedHeight(text_browser.document().size().height())
            layout_7.addWidget(text_label)
            layout_7.addWidget(text_browser)

            self.information_layout.addLayout(layout_7)
            self.information_layout.addSpacing(5)

        self.information_layout.addSpacing(15)


class DragScrollArea(QScrollArea):
    file_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(DragScrollArea, self).__init__(parent)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
        if a0.mimeData().hasUrls():
            a0.accept()
        else:
            a0.ignore()

    def dragMoveEvent(self, a0: QtGui.QDragMoveEvent) -> None:
        if a0.mimeData().hasUrls() and len(a0.mimeData().urls()) == 1 and os.path.isfile(a0.mimeData().urls()[0].toLocalFile()):
            a0.setDropAction(QtCore.Qt.CopyAction)
            a0.accept()
        else:
            a0.ignore()

    def dropEvent(self, a0: QtGui.QDropEvent) -> None:
        if a0.mimeData().hasUrls() and len(a0.mimeData().urls()) == 1 and os.path.isfile(a0.mimeData().urls()[0].toLocalFile()):
            a0.setDropAction(QtCore.Qt.CopyAction)
            a0.accept()
            self.file_signal.emit(a0.mimeData().urls()[0].toLocalFile())
        else:
            a0.ignore()


ProgressBarStyleSheet = '''
/*设置红色进度条*/
#RedProgressBar {
    text-align: center; /*进度值居中*/
}
#RedProgressBar::chunk {
    background-color: #F44336;
}

#BlueProgressBar {
    text-align: center; /*进度值居中*/
}
#BlueProgressBar::chunk {
    background-color: #2196F3;
}
'''
