# coding=utf-8
import logging
import os

import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
from .folder_path import get_file_size
import settings as project_settings
from items import AppDetail
from utils import cal_file_hash
from database import Database
from pipelines.folder_path import get_app_folder


class ApkDownloadPipeline(FilesPipeline):
    logger = logging.getLogger("ApkDownloadPipeline")

    def __init__(self, store_uri, download_func=None, settings=None):
        super(ApkDownloadPipeline, self).__init__(store_uri, download_func, settings)
        self.db_handler = Database()

    def get_media_requests(self, item: AppDetail, info):
        app_folder = get_app_folder(item)
        download_link = item['download_link']
        apk_name = item['apk_name']

        file_path = os.path.join(app_folder, apk_name)
        if item['market'] == "github_opensource":
            file_path += ".zip"
        elif not file_path.endswith('.apk'):
            file_path += '.apk'
        file_path = os.path.relpath(file_path, project_settings.FILES_STORE)
        if not self.db_handler.get_update_status(item['update_id']):
            yield scrapy.Request(download_link, meta={'file_path': file_path})
        else:
            raise DropItem("Apk File {} exists.".format(download_link))

    def file_path(self, request, response=None, info=None, *, item=None):
        return request.meta['file_path']

    def item_completed(self, results, item: AppDetail, info):
        if results[0][0]:
            # download successfully
            self.logger.info("Download app '{}' version '{}' from market '{}' successfully.".format(item['app_title'], item['version'], item['market']))
            apk_path = results[0][1]['path']
            apk_path = os.path.join(project_settings.FILES_STORE, apk_path)
            apk_size = get_file_size(apk_path)
            apk_hash = cal_file_hash(apk_path)
            self.db_handler.set_update_available(item['update_id'], apk_size, apk_hash)
            return item
        else:
            # download fail
            self.logger.error("Fail to Download app '{}' version '{}' from market '{}'.".format(item['app_title'], item['version'], item['market']))
            return item
