# coding=utf-8
import json
import os
import scrapy
from urllib import parse

import items

max_callback_time = 10


class XiaomiSpider(scrapy.Spider):
    name = "Xiaomi Spider"

    def start_requests(self):
        start_url = "http://app.mi.com/"
        yield scrapy.Request(start_url, callback=self.parse_diff_category)

    def parse_diff_category(self, response: scrapy.http.Response):
        """
        parse different categories.
        """
        category_urls = response.css(".sidebar ul.category-list li a::attr(href)").getall()

        for category_url in category_urls:
            category_id = os.path.basename(category_url)
            json_url = "http://app.mi.com/categotyAllListApi?page=0&categoryId={}".format(category_id)
            yield scrapy.Request(json_url, callback=self.parse_category_list)

    def parse_category_list(self, response: scrapy.http.Response):
        """
        parse category list.
        """
        try:
            json_data = json.loads(response.text)['data']
        except json.decoder.JSONDecodeError as _err:
            callback_time = response.meta.get('callback_time') or 0
            if callback_time < 3:
                self.logger.warning("Spider crawl {} failed.".format(response.url))
                yield scrapy.Request(response.url, callback=self.parse_category_list, dont_filter=True, meta={"callback_time": callback_time + 1})
            else:
                raise _err
            return

        if len(json_data) == 0:
            return

            # parse app
        for app_data in json_data:
            package_name = app_data['packageName']
            app_url = "http://app.mi.com/details?id={}".format(package_name)
            yield scrapy.Request(app_url, callback=self.parse)

        # parse next page
        request_url = response.url
        url_data = parse.parse_qs(parse.urlparse(request_url).query)
        page_id = int(url_data['page'][0]) + 1
        category_id = url_data['categoryId'][0]
        new_url = "http://app.mi.com/categotyAllListApi?page={}&categoryId={}".format(page_id, category_id)
        yield scrapy.Request(new_url, callback=self.parse_category_list)

    def parse(self, response: scrapy.http.Response, **kwargs):
        """
        parse app detail.
        """
        # app title
        app_title = response.css("div.container div.app-intro div.app-info div.intro-titles h3::text").get()
        if not app_title:
            callback_time = response.meta.get('callback_time') or 0
            if callback_time < 3:
                self.logger.warning("Spider crawl {} failed.".format(response.url))
                yield scrapy.Request(response.url, callback=self.parse, dont_filter=True, meta={"callback_time": callback_time + 1})
                return
            else:
                raise ValueError("App Title Error!")
        app_title = app_title.strip()

        # get the information
        left_information = response.css("div.container div.float-left div:nth-child(2)::text").getall()
        right_information = response.css("div.container div.float-right div:nth-child(2)::text").getall()
        if left_information is None or len(left_information) != 4:
            raise ValueError("Get Left Information Error!")
        if right_information is None or len(right_information) != 4:
            raise ValueError("Get Right Information Error!")

        # apk name
        apk_name = left_information[3].strip()

        # update date
        update_date = left_information[2].strip()

        # introduction
        try:
            introduction = "\n".join(response.css("div.app-text p.pslide::text").getall())
        except IndexError:
            raise ValueError("App Introduction Error!")

        # link
        app_link = response.url

        # category
        category = response.css("div.container div.app-intro div.app-info div.intro-titles p.special-font::text").get()
        if not category:
            raise ValueError("Category Error!")
        category = category.strip()

        # developer
        developer = right_information[1].strip()

        # market
        market = "xiaomi"

        # version
        version = left_information[1].strip()

        # size
        size = left_information[0].strip()

        # pictures
        picture_urls = response.css("div.bigimg-scroll div.img-list img::attr(src)").getall()

        # download link
        download_link = response.css("div.app-info-down a::attr(href)").get()
        if not download_link:
            raise ValueError("Download Link Error!")
        download_link = response.urljoin(download_link)

        # yield app detail
        app_detail = items.AppDetail(
            app_title=app_title, apk_name=apk_name, description=introduction, app_link=app_link, category=category, market=market, version=version, picture_links=picture_urls, size=size, download_link=download_link, developer=developer, update_date=update_date
        )
        yield app_detail

        # parse the related app
        related_urls = response.css("div.second-imgbox li>a::attr(href)").getall()
        for related_url in related_urls:
            new_url = response.urljoin(related_url)
            yield scrapy.Request(new_url, callback=self.parse)
