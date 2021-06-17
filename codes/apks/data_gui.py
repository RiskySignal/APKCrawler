# coding=utf-8
import datetime
import platform
import sys

from PyQt5.QtCore import QThreadPool
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pipelines.folder_path import get_app_folder
from settings import ProgressBarStyleSheet
from ui_thread import *
from custom_ui import InformationWidget

from custom_ui import ComboCheckBox, DragScrollArea

if platform.system() == "Windows":
    from PyQt5 import sip
else:
    import sip

__current_folder_path__ = os.path.dirname(os.path.abspath(__file__))
BUTTON_HEIGHT = 25


class DataGUI(QWidget):
    # Main GUI for data module.

    def __init__(self):
        super(DataGUI, self).__init__()
        self.layout_init()

    def layout_init(self):
        # 整体大小
        height = 600
        width = 1400
        self.setFixedSize(width, height)
        self.setWindowTitle("Data GUI")

        # 设置字体
        self.setFont(QFont("Microsoft Yahei", 8.5))

        # set layout
        root_layout = QVBoxLayout()
        body_widget = QGroupBox(title="Search Condition")
        bottom_widget = QGroupBox(title="File Database")
        root_layout.addWidget(body_widget)
        root_layout.addWidget(bottom_widget)
        root_layout.setStretch(0, 1)
        root_layout.setStretch(1, 15)

        # save the value
        self.body_widget = body_widget
        self.bottom_widget = bottom_widget

        # init the sub layout
        self.body_widget_init()
        self.bottom_widget_init()

        # show
        self.setLayout(root_layout)

    def body_widget_init(self):
        # set the layout
        search_condition_layout = QHBoxLayout()
        sdk_level_layout = QVBoxLayout()
        authority_layout = QVBoxLayout()
        type_layout = QVBoxLayout()
        search_button_layout = QVBoxLayout()
        add_apk_layout = QVBoxLayout()

        search_condition_layout.addLayout(sdk_level_layout)
        search_condition_layout.addSpacing(20)
        search_condition_layout.addLayout(authority_layout)
        search_condition_layout.addSpacing(20)
        search_condition_layout.addLayout(type_layout)
        search_condition_layout.addSpacing(40)
        search_condition_layout.addLayout(search_button_layout)
        search_condition_layout.addStretch()
        search_condition_layout.addLayout(add_apk_layout)
        self.body_widget.setLayout(search_condition_layout)

        # save the value
        self.search_condition_layout = search_condition_layout
        self.sdk_level_layout = sdk_level_layout
        self.authority_layout = authority_layout
        self.type_layout = type_layout
        self.search_button_layout = search_button_layout
        self.add_apk_layout = add_apk_layout

        # init the sub layout
        self.sdk_level_layout_init()
        self.authority_layout_init()
        self.type_layout_init()
        self.search_button_layout_init()
        self.add_apk_layout_init()

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
        self.add_apk_layout.addStretch()

        # save the value
        self.add_apk_button = add_apk_button
        self.add_apk_progress_bar = add_apk_progress_bar

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


class DataProcess(DataGUI):
    # Main GUI for data module
    sdk_level_signal = QtCore.pyqtSignal(list)
    authority_signal = QtCore.pyqtSignal(list)
    type_signal = QtCore.pyqtSignal(list)
    add_apk_signal = pyqtSignal(int, int, int)
    add_progress_signal = pyqtSignal(float)
    market_signal = pyqtSignal(list)
    app_signal = pyqtSignal(list)
    update_signal = pyqtSignal(list)
    update_information_signal = pyqtSignal(list)
    delete_apk_signal = pyqtSignal()
    delete_progress_signal = pyqtSignal(float)
    error_signal = pyqtSignal(str)

    market_model = None
    app_model = None
    update_model = None

    search_app_thread = None
    search_platform_thread = None
    search_update_thread = None
    search_update_info_thread = None

    inbox_update_id_list = []

    def __init__(self):
        super(DataProcess, self).__init__()
        self.thread_pool = QThreadPool()
        self.thread_pool.globalInstance()
        self.thread_pool.setMaxThreadCount(8)

        self.bind_error()
        self.load_data()
        self.bind_add_apk()
        self.bind_search()
        self.bind_delete()
        self.check_value()

    """
    加载ComboBox数据
    """

    def load_data(self):
        # sdk level combobox
        sdk_thread = SDKLevelThread()
        sdk_thread.transfer(self)
        self.sdk_level_signal.connect(self.update_sdk)
        self.thread_pool.start(sdk_thread)

        # authority combobox
        authority_thread = AuthorityThread()
        authority_thread.transfer(self)
        self.authority_signal.connect(self.update_authority)
        self.thread_pool.start(authority_thread)

        # type combobox
        type_thread = TypeThread()
        type_thread.transfer(self)
        self.type_signal.connect(self.update_type)
        self.thread_pool.start(type_thread)

    def update_sdk(self, sdk_list):
        sdk_list = ["UNKNOWN"] + sdk_list
        self.sdk_list = sdk_list
        self.sdk_combobox.addItems(sdk_list)

    def update_authority(self, authority_list):
        if not authority_list:
            return
        authority_index_list, authority_name_list = zip(*authority_list)
        authority_name_list = list(authority_name_list)
        self.authority_id_list = list(authority_index_list)
        self.authority_combobox.addItems(authority_name_list)

    def update_type(self, type_list):
        if not type_list:
            return
        type_index_list, type_name_list = zip(*type_list)
        self.type_id_list = list(type_index_list)
        self.type_combobox.addItems(type_name_list)

    """
    查找
    """

    def bind_search(self):
        self.search_button.clicked.connect(self.search_click)

        self.market_signal.connect(self.update_market)
        self.first_file_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.first_file_tree.clicked.connect(self.first_tree_click)

        self.app_signal.connect(self.update_app)
        self.second_file_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.second_file_tree.clicked.connect(self.second_tree_click)

        self.update_signal.connect(self.update_update)
        self.third_file_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.third_file_tree.clicked.connect(self.third_tree_click)

        self.update_information_signal.connect(self.update_information)

        self.bind_drag_search()

    def search_click(self):
        # get the combobox value
        sdk_name_list = self.sdk_combobox.get_select_text()
        authority_select_list = self.authority_combobox.get_select_index()
        app_type_select_list = self.type_combobox.get_select_index()

        # 选中全部sdk 或 未选中任何sdk时,无需筛选
        if len(sdk_name_list) == len(self.sdk_list) or len(sdk_name_list) == 0:
            sdk_name_list = None
        self.selected_sdk_name_list = sdk_name_list

        # 未选中任何authority时,无需筛选
        if len(authority_select_list) == 0:
            authority_id_list = None
        else:
            authority_id_list = [self.authority_id_list[_index_] for _index_ in authority_select_list]
        self.selected_authority_id_list = authority_id_list

        # 未选中任何type 或 选中全部type时, 无需筛选
        if len(app_type_select_list) == 0 or len(app_type_select_list) == len(self.type_id_list):
            type_id_list = None
        else:
            type_id_list = [self.type_id_list[_index_] for _index_ in app_type_select_list]
        self.selected_type_id_list = type_id_list

        search_platform_thread = SearchPlatformThread()
        search_platform_thread.transfer(self, sdk_name_list, authority_id_list, type_id_list)
        if self.search_platform_thread:
            # 取消上一个请求
            try:
                self.thread_pool.cancel(self.search_platform_thread)
            except RuntimeError:
                pass
        self.search_platform_thread = search_platform_thread
        self.thread_pool.start(search_platform_thread)

    def update_market(self, market_list):
        platform_model = QStandardItemModel()
        icon_path = os.path.join(__current_folder_path__, "./images/folder.png")
        for market in market_list:
            platform_model.appendRow(QStandardItem(QIcon(icon_path), market['market_name']))
        self.market_list = market_list
        if self.market_model:
            self.market_model.deleteLater()
        self.market_model = platform_model
        self.first_file_tree.setModel(platform_model)
        self.first_file_tree.scrollTo(platform_model.index(0, 0))

        # clear the second tree
        app_model = QStandardItemModel()
        self.app_list = []
        if self.app_model:
            self.app_model.deleteLater()
        self.app_model = app_model
        self.second_file_tree.setModel(app_model)

        # clear the third tree
        update_model = QStandardItemModel()
        self.update_list = []
        if self.update_model:
            self.update_model.deleteLater()
        self.update_model = update_model
        self.third_file_tree.setModel(update_model)

        # clear the information box
        self.clear_apk_info_layout()
        self.inbox_update_id_list = []

        # not find any data
        if len(market_list) == 0:
            QMessageBox().warning(self, "Not Found", "Not found any apk in database.", QMessageBox.Ok)

    def first_tree_click(self):
        current_row_index = self.first_file_tree.currentIndex().row()

        search_app_thread = SearchAppThread()
        search_app_thread.transfer(self, self.market_list[current_row_index]['market_id'], self.selected_sdk_name_list, self.selected_authority_id_list, self.selected_type_id_list)
        if self.search_app_thread:
            # 取消上一个请求
            try:
                self.thread_pool.cancel(self.search_app_thread)
            except RuntimeError:
                pass
        self.search_app_thread = search_app_thread
        self.thread_pool.start(search_app_thread)

    def update_app(self, app_list):
        app_model = QStandardItemModel()
        icon_path = os.path.join(__current_folder_path__, "./images/android.png")
        for app in app_list:
            app_model.appendRow(QStandardItem(QIcon(icon_path), app['app_title']))
        self.app_list = app_list
        if self.app_model:
            self.app_model.deleteLater()
        self.app_model = app_model
        self.second_file_tree.setModel(app_model)
        self.second_file_tree.scrollTo(app_model.index(0, 0))

    def second_tree_click(self):
        current_row_index = self.second_file_tree.currentIndex().row()

        search_update_thread = SearchUpdateThread()
        search_update_thread.transfer(self, self.app_list[current_row_index]['app_id'], self.selected_sdk_name_list, self.selected_authority_id_list, self.selected_type_id_list)
        if self.search_update_thread:
            # 取消上一个请求
            try:
                self.thread_pool.cancel(self.search_update_thread)
            except RuntimeError:
                pass
        self.search_update_thread = search_update_thread
        self.thread_pool.start(search_update_thread)

    def update_update(self, update_list):
        update_model = QStandardItemModel()
        icon_path = os.path.join(__current_folder_path__, "./images/version.png")
        for update in update_list:
            version = update['version'].split('.apk')[0] if update['version'].endswith('.apk') else update['version']
            version = update['version'].split('.xapk')[0] if update['version'].endswith('.xapk') else version
            update_model.appendRow(QStandardItem(QIcon(icon_path), version))
        self.update_list = update_list
        if self.update_model:
            self.update_model.deleteLater()
        self.update_model = update_model
        self.third_file_tree.setModel(update_model)
        self.third_file_tree.scrollTo(update_model.index(0, 0))

    def third_tree_click(self):
        current_third_tree_row_index = self.third_file_tree.currentIndex().row()

        search_apk_info_by_update_id_thread = SearchApkInfoByUpdateIdThread()
        search_apk_info_by_update_id_thread.transfer(self, self.update_list[current_third_tree_row_index]['update_id'])
        if self.search_update_info_thread:
            # 取消上一个请求
            try:
                self.thread_pool.cancel(self.search_update_info_thread)
            except RuntimeError:
                pass
        self.search_update_info_thread = search_apk_info_by_update_id_thread
        self.thread_pool.start(search_apk_info_by_update_id_thread)

        # clear the information box
        self.clear_apk_info_layout()
        self.inbox_update_id_list = []

    def update_information(self, information_list):
        self.clear_apk_info_layout()
        inbox_update_id_list = []
        for information in information_list:  # add the new information widget
            information['market'] = information['market_name']
            update_folder = get_app_folder(information)
            image_file_list = glob.glob(os.path.join(update_folder, "*.jpg"))
            description_file = os.path.join(update_folder, "description.txt")
            if os.path.exists(description_file):
                with open(description_file, 'r') as _file_:
                    description = _file_.read().strip()
                    if description != "":
                        information['description'] = description
            information['image_file_list'] = image_file_list
            new_information_widget = InformationWidget()
            new_information_widget.load_data(information)
            self.apk_info_layout.addWidget(new_information_widget)
            inbox_update_id_list.append(information['update_id'])
        self.inbox_update_id_list = inbox_update_id_list

    """
    拖动查找
    """

    def bind_drag_search(self):
        self.apk_info_scroll_area.file_signal.connect(self.drag_search)

    def drag_search(self, file_url):
        drag_search_thread = DragSearchThread()
        drag_search_thread.transfer(self, file_url)
        if self.search_app_thread:
            #  取消上一个进程
            try:
                self.thread_pool.cancel(self.search_app_thread)
            except RuntimeError:
                pass
        self.search_app_thread = drag_search_thread
        self.thread_pool.start(drag_search_thread)

        # uncheck the third tree
        row_index = self.third_file_tree.currentIndex().row()
        if row_index != -1:
            self.third_file_tree.setCurrentIndex(self.update_model.index(-1, -1))

        # clear the information box
        self.clear_apk_info_layout()
        self.inbox_update_id_list = []

    """
    删除
    """

    def bind_delete(self):
        self.delete_apk_button.clicked.connect(self.delete_apk_button_click)
        self.delete_apk_signal.connect(self.delete_apk_success)
        self.delete_from_folder_button.clicked.connect(self.delete_from_folder_button_click)

    def delete_apk_button_click(self):
        if not self.inbox_update_id_list:
            return

        # clear the information box
        self.clear_apk_info_layout()
        inbox_update_id_list = self.inbox_update_id_list
        self.inbox_update_id_list = []

        # check the third file system tree
        in_third_tree = False
        reserved_update_list = []  # type: List[Dict]
        for update in self.update_list:
            if update['update_id'] in inbox_update_id_list:
                in_third_tree = True
            else:
                reserved_update_list.append(update)
        if in_third_tree:
            new_update_model = QStandardItemModel()
            icon_path = os.path.join(__current_folder_path__, "./images/version.png")
            for update in reserved_update_list:
                version = update['version'].split('.apk')[0] if update['version'].endswith('.apk') else update['version']
                version = update['version'].split('.xapk')[0] if update['version'].endswith('.xapk') else version
                new_update_model.appendRow(QStandardItem(QIcon(icon_path), version))
            self.update_list = reserved_update_list
            if self.update_model:
                self.update_model.deleteLater()
            self.update_model = new_update_model
            self.third_file_tree.setModel(new_update_model)
            self.third_file_tree.scrollTo(new_update_model.index(0, 0))

        # start the delete thread
        delete_apk_thread = DeleteApkThread()
        delete_apk_thread.transfer(self, inbox_update_id_list)
        self.thread_pool.start(delete_apk_thread)

    def delete_apk_success(self):
        QMessageBox.information(self, "Delete successfully", "Successfully delete APK(s).", QMessageBox.Yes)

        self.delete_from_folder_button.setVisible(True)
        self.delete_progress_bar.setValue(0)
        self.delete_progress_bar.setVisible(False)

    def delete_from_folder_button_click(self):
        dir_choose = QFileDialog.getExistingDirectory(self, "Choose APK Directory", os.path.join(__current_folder_path__, "../../"))
        if not dir_choose:
            return

        user_choose = QMessageBox.question(self, "Delete Confirm", "Do confirm to delete folder '{}'?.".format(dir_choose), QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if user_choose == QMessageBox.Cancel:
            return

        # set the layout
        self.delete_from_folder_button.setVisible(False)
        self.delete_progress_bar.setValue(0)
        self.delete_progress_bar.setVisible(True)

        # start the delete thread
        delete_thread = MultiDeleteThread()
        delete_thread.transfer(self, dir_choose)
        self.thread_pool.start(delete_thread)

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

    """
    批量添加APK
    """

    def bind_add_apk(self):
        self.add_progress_signal.connect(self.add_apk_progress_bar.setValue)
        self.add_apk_signal.connect(self.add_apk_success)
        self.add_apk_button.clicked.connect(self.add_apk_button_click)

    def add_apk_button_click(self):
        dir_choose = QFileDialog.getExistingDirectory(self, "Choose APK Directory", os.path.join(__current_folder_path__, "../../"))
        if not dir_choose:
            return
        self.add_apk_button.setVisible(False)
        self.add_apk_progress_bar.setValue(0)
        self.add_apk_progress_bar.setVisible(True)
        add_apk_thread = AddAPKThread()
        add_apk_thread.transfer(self, dir_choose)
        self.thread_pool.start(add_apk_thread)

    def add_apk_success(self, success_number, repeated_number, error_number):
        QMessageBox.information(self, "Add APK", "Successfully add APKs.  {} success,  {} Repeated  and  {} error.".format(success_number, repeated_number, error_number), QMessageBox.Ok, QMessageBox.Ok)

        self.add_apk_button.setVisible(True)
        self.add_apk_progress_bar.setVisible(False)
        self.add_apk_progress_bar.setValue(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    data_gui = DataProcess()
    data_gui.show()
    sys.exit(app.exec_())
