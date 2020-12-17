# coding=utf-8
import os
import time
from typing import *

from PyQt5 import QtCore
from PyQt5.QtCore import *
from database import Database
import glob
from pipelines.folder_path import get_file_size
from utils import cal_file_hash
from settings import DEFAULT_DEVELOPER, DEFAULT_CATEGORY, DEFAULT_MARKET, python_interface
import traceback


def catch_exception(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as _err_:
            self.communication.error_signal.emit(traceback.format_exc())

    return wrapper


class AutoDeleteRunnable(QRunnable):
    def __init__(self):
        super(AutoDeleteRunnable, self).__init__()
        self.setAutoDelete(True)


class SDKLevelThread(AutoDeleteRunnable):
    def transfer(self, communication):
        self.communication = communication

    @catch_exception
    def run(self):
        db = Database()
        sdk_level_list = db.get_all_sdk_level()
        self.communication.sdk_level_signal.emit(sdk_level_list)


class AuthorityThread(AutoDeleteRunnable):
    def transfer(self, communication):
        self.communication = communication

    @catch_exception
    def run(self):
        db = Database()
        authority_list = db.get_all_authority()
        self.communication.authority_signal.emit(authority_list)


class TypeThread(AutoDeleteRunnable):
    def transfer(self, communication):
        self.communication = communication

    @catch_exception
    def run(self):
        db = Database()
        type_item_list = db.get_all_app_type()
        self.communication.type_signal.emit(type_item_list)


class ScrapyWorker(QObject):
    def __init__(self, communication, parent=None):
        super().__init__(parent)
        self.communication = communication
        self._process = QtCore.QProcess(self)
        self._process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self._process.setProgram(python_interface)
        self._process.readyReadStandardOutput.connect(self.on_readyReadStandardOutput)
        self._process.started.connect(self.communication.scrapy_start_signal)
        self._process.finished.connect(self.communication.scrapy_finish_signal)

    @catch_exception
    def run(self, platform):
        self._process.setWorkingDirectory('./')
        self._process.setArguments(['./main.py', "--market_name", platform])
        self._process.start()

    def on_readyReadStandardOutput(self):
        data = self._process.readAllStandardOutput().data().decode()
        self.communication.scrapy_log_signal.emit(data)

    def stop(self):
        self._process.kill()


class AddAPKThread(AutoDeleteRunnable):
    def transfer(self, communication, root_folder):
        self.communication = communication
        self.root_folder = root_folder

    @catch_exception
    def run(self):
        file_list = glob.glob(os.path.join(self.root_folder, "**/*"), recursive=True)
        file_number = len(file_list)
        db = Database()

        finish_number = 0
        success_number = 0
        repeated_number = 0
        error_number = 0
        for file in file_list:
            if os.path.isfile(file):
                try:
                    apk_name = os.path.splitext(os.path.basename(file))[0]
                    apk_name = apk_name[:256]  # clip the too long string
                    app_title = apk_name
                    developer = DEFAULT_DEVELOPER
                    category = DEFAULT_CATEGORY
                    market = DEFAULT_MARKET
                    size = get_file_size(file)
                    update_date = time.strftime("%Y-%m-%d", time.localtime())
                    version = update_date
                    file_hash = cal_file_hash(file)
                    if db.insert_app_from_file(market, file_hash, app_title, apk_name, developer, category, version, size, update_date):
                        success_number += 1
                    else:
                        repeated_number += 1
                except Exception:
                    error_number += 1

            finish_number += 1
            self.communication.add_progress_signal.emit(finish_number * 1.0 / file_number * 100)

        self.communication.add_apk_signal.emit(success_number, repeated_number, error_number)


def generate_sdk_sql_str(sdk_name_list):
    if sdk_name_list is None:
        return "", []
    sql_str = ""
    param_list = []
    for sdk_name in sdk_name_list:
        if sdk_name == "UNKNOWN":
            if sql_str == "":
                sql_str = "sdk_level is NULL "
            else:
                sql_str += " OR sdk_level is NULL "
        else:
            param_list.append(sdk_name)
            if sql_str == "":
                sql_str = "sdk_level=%s "
            else:
                sql_str += " OR sdk_level=%s "
    sql_str = " (" + sql_str[:-1] + ") "
    return sql_str, param_list


def generate_authority_sql_str(authority_id_list):
    if authority_id_list is None:
        return "", []
    sql_str = ""
    for _ in authority_id_list:
        if sql_str == "":
            sql_str += " EXISTS (SELECT 1 FROM authority_relation WHERE authority_relation.update_id=`update`.update_id AND authority_id=%s) "
        else:
            sql_str += " AND EXISTS (SELECT 1 FROM authority_relation WHERE authority_relation.update_id=`update`.update_id AND authority_id=%s) "
    return sql_str, authority_id_list


def generate_type_sql_str(app_type_list):
    if app_type_list is None:
        return "", []
    sql_str = ""
    for _ in app_type_list:
        if sql_str == "":
            sql_str = "type_id=%s "
        else:
            sql_str += " OR type_id=%s "
    sql_str = " (" + sql_str[:-1] + ") "
    return sql_str, app_type_list


class SearchPlatformThread(AutoDeleteRunnable):
    def transfer(self, communication, sdk_name_list: Union[None, List] = None, authority_id_list: Union[None, List] = None, type_id_list: Union[None, List] = None):
        self.communication = communication
        self.sdk_name_list = sdk_name_list
        self.authority_id_list = authority_id_list
        self.type_id_list = type_id_list

    @catch_exception
    def run(self):
        db = Database()

        if self.sdk_name_list is None and self.authority_id_list is None and self.type_id_list is None:
            # not apply any search condition
            market_list = db.search_platform_not_delete()
        else:
            sdk_sql_str, sdk_param_list = generate_sdk_sql_str(self.sdk_name_list)
            authority_sql_str, authority_param_list = generate_authority_sql_str(self.authority_id_list)
            type_sql_str, type_param_list = generate_type_sql_str(self.type_id_list)
            sql_str = "select m.market_id, market_name from `update` join app a on `update`.app_id = a.app_id join market m on m.market_id = a.market_id where is_delete=FALSE "
            if sdk_sql_str:
                sql_str += " AND " + sdk_sql_str
            if authority_sql_str:
                sql_str += " AND " + authority_sql_str
            if type_sql_str:
                sql_str += " AND " + type_sql_str
            sql_str += " group by market_id order by market_name;"
            param_list = sdk_param_list + authority_param_list + type_param_list

            cursor = db.get_cursor()
            cursor.execute(sql_str, param_list)
            results = cursor.fetchall()
            market_list = []
            for result in results:
                if result and result['market_name']:
                    market_list.append({
                        "market_id": result['market_id'],
                        "market_name": result['market_name'].decode('utf-8')
                    })

        self.communication.market_signal.emit(market_list)


class SearchAppThread(AutoDeleteRunnable):
    def transfer(self, communication, market_id, sdk_name_list: Union[None, list] = None, authority_id_list: Union[None, List] = None, type_id_list: Union[None, List] = None):
        self.communication = communication
        self.market_id = market_id
        self.sdk_name_list = sdk_name_list
        self.authority_id_list = authority_id_list
        self.type_id_list = type_id_list

    @catch_exception
    def run(self):
        db = Database()

        if self.sdk_name_list is None and self.authority_id_list is None and self.type_id_list is None:
            # not apply ant search condition
            app_list = db.search_app_not_delete(self.market_id)
        else:
            sdk_sql_str, sdk_param_list = generate_sdk_sql_str(self.sdk_name_list)
            authority_sql_str, authority_param_list = generate_authority_sql_str(self.authority_id_list)
            type_sql_str, type_param_list = generate_type_sql_str(self.type_id_list)
            sql_str = "select a.app_id, app_title from `update` join app a on `update`.app_id = a.app_id join market m on m.market_id = a.market_id where is_delete=FALSE and a.market_id=%s "
            if sdk_sql_str:
                sql_str += " AND " + sdk_sql_str
            if authority_sql_str:
                sql_str += " AND " + authority_sql_str
            if type_sql_str:
                sql_str += " AND " + type_sql_str
            sql_str += " group by app_id order by app_title;"
            param_list = [self.market_id] + sdk_param_list + authority_param_list + type_param_list

            cursor = db.get_cursor()
            cursor.execute(sql_str, param_list)
            results = cursor.fetchall()
            app_list = []
            for result in results:
                if result and result['app_title']:
                    app_list.append({
                        "app_id": result['app_id'],
                        "app_title": result['app_title'].decode('utf-8')
                    })

        self.communication.app_signal.emit(app_list)


class SearchUpdateThread(AutoDeleteRunnable):
    def transfer(self, communication, app_id, sdk_name_list: Union[None, list] = None, authority_id_list: Union[None, List] = None, type_id_list: Union[None, List] = None):
        self.communication = communication
        self.app_id = app_id
        self.sdk_name_list = sdk_name_list
        self.authority_id_list = authority_id_list
        self.type_id_list = type_id_list

    @catch_exception
    def run(self):
        db = Database()

        if self.sdk_name_list is None and self.authority_id_list is None and self.type_id_list is None:
            # not apply ant search condition
            update_list = db.search_update_not_delete(self.app_id)
        else:
            sdk_sql_str, sdk_param_list = generate_sdk_sql_str(self.sdk_name_list)
            authority_sql_str, authority_param_list = generate_authority_sql_str(self.authority_id_list)
            sql_str = "select update_id, version from `update` where is_delete=FALSE and app_id=%s "
            if sdk_sql_str:
                sql_str += " AND " + sdk_sql_str
            if authority_sql_str:
                sql_str += " AND " + authority_sql_str
            sql_str += " order by version;"
            param_list = [self.app_id] + sdk_param_list + authority_param_list

            cursor = db.get_cursor()
            cursor.execute(sql_str, param_list)
            results = cursor.fetchall()
            update_list = []
            for result in results:
                if result and result['version']:
                    update_list.append({
                        "update_id": result['update_id'],
                        "version": result['version'].decode('utf-8')
                    })

        self.communication.update_signal.emit(update_list)


class SearchApkInfoByUpdateIdThread(AutoDeleteRunnable):
    def transfer(self, communication, update_id):
        self.communication = communication
        self.update_id = update_id

    @catch_exception
    def run(self):
        db = Database()
        update_info_list = db.get_information_by_update_id(self.update_id)
        self.communication.update_information_signal.emit(update_info_list)


class DeleteApkThread(AutoDeleteRunnable):
    def transfer(self, communication, update_id_list):
        self.communication = communication
        self.update_id_list = update_id_list

    @catch_exception
    def run(self):
        db = Database()
        for update_id in self.update_id_list:
            db.delete_apk_by_update_id(update_id)
        self.communication.delete_apk_signal.emit()


class DragSearchThread(AutoDeleteRunnable):
    def transfer(self, communication, file_url):
        self.communication = communication
        self.file_path = file_url

    @catch_exception
    def run(self):
        db = Database()
        file_hash = cal_file_hash(self.file_path)
        update_info_list = db.get_information_by_file_hash(file_hash)
        self.communication.update_information_signal.emit(update_info_list)


class MultiDeleteThread(AutoDeleteRunnable):
    def transfer(self, communication, folder_path):
        self.communication = communication
        self.folder_path = folder_path

    @catch_exception
    def run(self):
        db = Database()
        hash_list = []
        file_list = glob.glob(os.path.join(self.folder_path, "**/*"), recursive=True)
        file_number = len(file_list)

        current_number = 0
        for file in file_list:
            current_number += 1
            if os.path.isfile(file):
                hash_list.append(
                    cal_file_hash(file)
                )
            self.communication.delete_progress_signal.emit(
                current_number * 1.0 / file_number * 100 * 0.5
            )

        hash_number = len(hash_list)
        current_number = 0
        for apk_hash in hash_list:
            current_number += 1
            db.delete_apk_by_hash(apk_hash)
            self.communication.delete_progress_signal.emit(
                current_number * 1.0 / hash_number * 100 * 0.5 + 0.5
            )

        self.communication.delete_apk_signal.emit()
