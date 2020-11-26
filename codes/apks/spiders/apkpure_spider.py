# coding=utf-8
import logging
import os
import scrapy
from collections import defaultdict

import items
import settings


class ApkPureSpider(scrapy.Spider):
    name = "apkpure"
    logger = logging.getLogger("GoogleSpider")

    def start_requests(self):
        start_url = "https://apkpure.com/app"
        yield scrapy.Request(start_url, callback=self.parse_diff_cate)

    def parse_diff_cate(self, response):
        """
        parse different category
        """
        categories = response.css("ul.index-category.cicon li a::attr('href')").getall()

        for category in categories:
            category_url = response.urljoin(category)
            yield scrapy.Request(category_url, callback=self.parse_app_list)

    def parse_app_list(self, response):
        """
        parse app list
        """
        # 解析应用列表
        app_urls = response.css("ul.category-template#pagedata li div.category-template-img a::attr('href')").getall()
        for app_url in app_urls:
            app_url = response.urljoin(app_url)
            yield scrapy.Request(app_url, callback=self.parse_app)

        # 解析下一页
        next_url = response.css("a.loadmore::attr('href')").get()
        if next_url:
            next_url = response.urljoin(next_url)
            yield scrapy.Request(next_url, callback=self.parse_app_list)

    def parse_app(self, response):
        """
        parse app info page
        """
        # 解析应用信息
        # app title
        app_title = response.css("div.main div.title-like h1::text").get()
        if app_title is None:
            raise ValueError("App Title Error.")

        # description and update info
        description = "Description:\n" + "\n".join(response.css("div#describe div.content::text").getall())
        description += "Update Info:\n" + "\n".join(response.css("div#whatsnew div:nth-child(3)::text").getall())

        category = response.css("div.additional ul li:first-child a span::text").getall()
        if len(category) == 0:
            raise ValueError("App Type Error.")
        elif len(category) == 1:
            self.logger.info("App '{}' is a paid app. Can't Download it.".format(app_title))
            return
        else:
            category = category[1]

        # latest version
        latest_version = response.css("div.additional ul li:nth-child(2) p:nth-child(2)::text").get()
        if not latest_version:
            raise ValueError("App Latest Version Error.")

        # developer
        publisher = response.css("div.left div.box div.details-author p a::text").get()
        if not publisher:
            raise ValueError("Developer Error.")

        # apk name
        package_name = os.path.split(response.url)[-1]

        # app link
        apkpure_url = response.url

        # market
        market = "apkpure"

        # picture links
        picture_links = response.css("div.describe div.describe-img div#slide-box img::attr(src)").getall()

        app_detail = items.AppDetail(app_title=app_title, apk_name=package_name, description=description, developer=publisher, app_link=apkpure_url, category=category, market=market, version=latest_version, picture_links=picture_links)

        # 更多版本
        more_version_url = response.css("div.ver-title div.more a::attr('href')").get()
        if more_version_url:
            more_version_url = response.urljoin(more_version_url)
            yield scrapy.Request(more_version_url, meta={"app_detail": app_detail}, callback=self.parse_multi_version)

        # 相似应用 & 同一厂商
        more_urls = response.css("div.left div.box div.title div.more a::attr('href')").getall()
        for more_url in more_urls:
            if "similar" in more_url:
                # 相似应用
                similar_url = response.urljoin(more_url)
                yield scrapy.Request(similar_url, callback=self.parse_similar)
            elif "developer" in more_url:
                # 同一厂商
                developer_url = response.urljoin(more_url)
                yield scrapy.Request(developer_url, callback=self.parse_developer, meta={"raw_url": apkpure_url})

    def parse_multi_version(self, response):
        """
        parse multiple version
        """
        app_detail = response.meta['app_detail']

        ver_lis = response.css("div.ver ul.ver-wrap li")
        for ver_li in ver_lis:
            version = ver_li.css("a div.ver-item-wrap span.ver-item-n::text").get()[1:]
            file_types = ver_li.css("div.ver-item div.ver-item-wrap span.ver-item-t::text").getall()
            if "XAPK" in file_types:
                file_type = "xapk"
            else:
                file_type = "apk"
            ver_info_dom = ver_li.css("div.ver-info")

            if len(ver_info_dom) > 0:  # 没有多个变种
                # 获取版本信息
                p_doms = ver_info_dom.css("div.ver-info-m p")
                page_url = ver_li.css("li>a::attr('href')").get()
                page_url = response.urljoin(page_url)
                ext_infos = defaultdict(str)
                for p_dom in p_doms:
                    try:
                        _key = p_dom.css("strong::text").get().strip()
                    except AttributeError:
                        continue

                    if _key:
                        try:
                            _key = _key.split(":")[0].strip()
                            _value = p_dom.css("p::text").get().strip()
                        except AttributeError as _err:
                            continue

                        if _key == "Requires Android":
                            ext_infos["requirement"] = _value
                        elif _key == "Signature":
                            ext_infos["signature"] = _value
                        elif _key == "Screen DPI":
                            ext_infos['dpi'] = _value
                        elif _key == "Architecture":
                            ext_infos['architecture'] = _value
                        elif _key == "Update on":
                            ext_infos['update_time'] = _value
                        elif _key == "File Size":
                            ext_infos['size'] = _value
                        elif _key == "File SHA1":
                            ext_infos['hash'] = _value
                file_size = ext_infos['size'] or settings.DEFAULT_SIZE

                update_detail = items.AppDetail(app_title=app_detail['app_title'], apk_name=app_detail['apk_name'], developer=app_detail['developer'], app_link=app_detail['app_link'], category=app_detail['category'], market=app_detail['market'], version="{}.{}".format(version, file_type), size=file_size)

                if version == app_detail['version']:
                    update_detail['description'] = app_detail['description']
                    update_detail['picture_links'] = app_detail['picture_links']
                else:
                    update_detail['description'] = ""
                    update_detail['picture_links'] = []

                yield scrapy.Request(page_url, meta={"update_detail": update_detail}, callback=self.parse)
            else:  # 存在多个变种
                variants_url = ver_li.css("a::attr('href')").get()
                variants_url = response.urljoin(variants_url)

                yield scrapy.Request(variants_url, meta={"app_detail": app_detail}, callback=self.parse_multi_varia)

    def parse_similar(self, response):
        """
        parse similar apps
        """
        # 解析相似app列表
        similar_apps = response.css("div.main div.box ul#pagedata li dd.title-dd a::attr('href')").getall()
        for similar_app in similar_apps:
            app_url = response.urljoin(similar_app)
            yield scrapy.Request(app_url, callback=self.parse_app)

    def parse_developer(self, response):
        """
        parse the same developer's apps
        """
        # 解析app列表
        devel_apps = response.css("div.main div.left div.box dl.search-dl p.search-title a::attr('href')").getall()
        for devel_app in devel_apps:
            app_url = response.urljoin(devel_app)
            yield scrapy.Request(app_url, callback=self.parse_app)

        # 下一页
        next_page_url = response.css("div.paging ul li:last-child a::attr('href')").get()
        if next_page_url:
            next_page_url = response.urljoin(next_page_url)
            yield scrapy.Request(next_page_url, callback=self.parse_developer)

    def parse(self, response, **kwargs):
        """
        parse the download page
        """
        update_detail = response.meta['update_detail']

        # 获取下载地址
        download_url = response.css("div.left div.box div.fast-download-box.fast-bottom p.down-click a::attr('href')").get()
        if not download_url:
            raise ValueError('Get download url Error.')
        update_detail['download_link'] = download_url

        yield update_detail

    def parse_multi_varia(self, response):
        """
        parse the multi variants
        """
        app_detail = response.meta['app_detail']
        variants_dom = response.css("div.left div.table div.table-row")[1:]
        version = response.css("div.left div.box div.variant div.info div.tit span::text").get()[1:]
        app_version_list = []

        for variant_dom in variants_dom:
            variant_number = variant_dom.css("div.table-cell div.popup span::text").get()

            # 解析更新的信息
            ver_info_dom = variant_dom.css("div.table-cell div.ver-info div.ver-info-m")
            file_type_str = variant_dom.css("div.table-cell.down a::text").get()
            if "XAPK" in file_type_str:
                file_type = "xapk"
            else:
                file_type = "apk"
            p_doms = ver_info_dom.css("p")
            page_url = variant_dom.css("div.table-cell.down a::attr('href')").get()
            page_url = response.urljoin(page_url)
            ext_info = defaultdict(str)
            for p_dom in p_doms:
                try:
                    _key = p_dom.css("strong::text").get().strip()
                except AttributeError:
                    continue

                if _key:
                    _key = _key.split(':')[0].strip()
                    _value = _value = p_dom.css("p::text").get().strip()

                    if _key == "Update on":
                        ext_info['update_time'] = _value
                    elif _key == "Requires Android":
                        ext_info['requirement'] = _value
                    elif _key == "Signature":
                        ext_info['signature'] = _value
                    elif _key == "Screen DPI":
                        ext_info['dpi'] = _value
                    elif _key == "Architecture":
                        ext_info['architecture'] = _value
                    elif _key == "File SHA1":
                        ext_info['hash'] = _value
                    elif _key == "File Size":
                        ext_info['size'] = _value

            app_size = ext_info['size'] or settings.DEFAULT_SIZE
            architecture = ext_info['architecture'] or settings.DEFAULT_ARCHITECTURE
            update_date = ext_info['update_time'] if ext_info['update_time'] != "" else None
            app_version = "{}-{}-{}-{}".format(version, variant_number, architecture, file_type)

            if app_version in app_version_list:
                continue
            app_version_list.append(app_version)

            update_detail = items.AppDetail(
                app_title=app_detail['app_title'], apk_name=app_detail['apk_name'], developer=app_detail['developer'], app_link=app_detail['app_link'], category=app_detail['category'], market=app_detail['market'], version=app_version, size=app_size, update_date=update_date
            )
            if version == app_detail['version']:
                update_detail['description'] = app_detail['description']
                update_detail['picture_links'] = app_detail['picture_links']
            else:
                update_detail['description'] = ""
                update_detail['picture_links'] = []

            yield scrapy.Request(page_url, meta={"update_detail": update_detail}, callback=self.parse)
