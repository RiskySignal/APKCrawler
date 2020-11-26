# coding=utf-8
import logging
from scrapy.pipelines.images import ImagesPipeline
from items import AppDetail
from scrapy.utils.python import to_bytes
import hashlib
import scrapy
import os
from pipelines.folder_path import get_app_folder
import settings as project_settings
from database import Database


class ImageDownloadPipeline(ImagesPipeline):
    logger = logging.getLogger("ImageDownloadPipeline")

    def __init__(self, store_uri, download_func=None, settings=None):
        super().__init__(store_uri, download_func, settings)
        self.db = Database()

    def get_media_requests(self, item: AppDetail, info):
        app_folder = get_app_folder(item)
        file_path = os.path.relpath(app_folder, project_settings.FILES_STORE)

        image_length = len(item['picture_links'])
        pruned_picture_links = []
        pruned_picture_link_ids = []
        for _image_index_ in range(image_length):
            picture_link = item['picture_links'][_image_index_]
            picture_link_id = item['picture_link_ids'][_image_index_]
            if not self.db.get_image_status(picture_link_id):
                pruned_picture_links.append(picture_link)
                pruned_picture_link_ids.append(picture_link_id)
            else:
                logging.info("Image file {} exists.".format(picture_link))
        item['picture_links'] = pruned_picture_links
        item['picture_link_ids'] = pruned_picture_link_ids

        for picture_link in item['picture_links']:
            yield scrapy.Request(picture_link, meta={'file_path': file_path})

    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return os.path.join(request.meta['file_path'], "%s.jpg" % image_guid)

    def item_completed(self, results, item: AppDetail, info):
        for result_index in range(len(results)):
            result = results[result_index]
            if result[0]:
                self.logger.info("Download image '{}' successfully.".format(item['picture_links'][result_index]))
                self.db.set_image_available(item['picture_link_ids'][result_index])
            else:
                self.logger.error("Fail to download image '{}'.".format(item['picture_links'][result_index]))

        return item
