# coding=utf-8

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy


class AppDetail(scrapy.Item):
    app_title = scrapy.Field()  # app 名字
    apk_name = scrapy.Field()  # apk 包名
    description = scrapy.Field()  # 介绍
    developer = scrapy.Field()  # 开发者
    app_link = scrapy.Field()  # 网页链接
    category = scrapy.Field()  # 类别
    market = scrapy.Field()  # 应用市场
    version = scrapy.Field()  # 版本号
    picture_links = scrapy.Field()  # 截图链接
    size = scrapy.Field()  # apk大小
    download_link = scrapy.Field()  # 下载地址
    update_id = scrapy.Field()  # update id
    picture_link_ids = scrapy.Field()  # 截图id
    update_date = scrapy.Field()  # update date
