# coding=utf-8
import os

import scrapy

import items
import settings


class FossDroidSpider(scrapy.Spider):
    name = "FossDroid Spider"

    def start_requests(self):
        start_url = "https://fossdroid.com/"
        yield scrapy.Request(start_url, callback=self.parse_homepage)

    def parse_homepage(self, response):
        """
        parse homepage
        """
        # 不同类别
        type_urls = response.css("nav.mdl-navigation.mdl-color--white a::attr('href')").getall()

        diff_sort_names = ["whats_new.html", "trending.html", "most_popular.html"]
        for type_url in type_urls:
            for diff_sort_name in diff_sort_names:
                new_url = response.urljoin(type_url) + diff_sort_name
                yield scrapy.Request(new_url, callback=self.parse_list)

    def parse_list(self, response):
        """
        parse app list
        """
        # 不同app
        app_urls = response.css("main.mdl-layout__content div.fd-list_applications div.fd-application div.mdl-card__actions a::attr('href')").getall()

        for app_url in app_urls:
            new_url = response.urljoin(app_url)
            yield scrapy.Request(new_url, callback=self.parse)

    def parse(self, response, **kwargs):
        """
        parse app
        """
        # app title
        app_title = response.css("main.mdl-layout__content div#fd-section_container section.fd-section div.mdl-card h1::text").get()
        if not app_title:
            raise ValueError('App Title Error.')

        # description
        description = "".join([line.strip() for line in response.css("main.mdl-layout__content div#fd-section_container section.fd-section div.mdl-card div.mdl-card__supporting-text::text").getall()])

        # version
        try:
            app_version = response.css("main.mdl-layout__content div#fd-section_container section.fd-section div.mdl-card div.mdl-card__supporting-text div.fd-application_info::text").getall()[1].split(':')[1].strip()
            if not app_version:
                raise ValueError('App Version Error.')
        except IndexError:
            raise ValueError('App Version Error.')

        # update date
        try:
            update_date = response.css("main.mdl-layout__content div#fd-section_container section.fd-section div.mdl-card div.mdl-card__supporting-text div.fd-application_info::text").getall()[5].split(':')[1].strip()
            if not update_date:
                raise ValueError("App Update Date Error.")
        except IndexError:
            raise ValueError("App Update Date Error.")
        else:
            day, month, year = update_date.split('-')
            update_date = year + "-" + month + "-" + day

        # pictures
        picture_links = [response.urljoin(picture_link) for picture_link in response.css('main.mdl-layout__content div#fd-section_container section.fd-section div.mdl-card div.mdl-card__supporting-text img::attr(src)').getall()]

        # download url
        download_url = response.urljoin(response.css("main.mdl-layout__content div#fd-section_container section.fd-section ul li:nth-child(6) a::attr('href')").get())
        if not download_url:
            raise ValueError("Download Link Error.")

        # app url
        app_link = response.url

        # apk name
        apk_name = os.path.basename(download_url)

        # type
        app_type = response.css('header.mdl-layout__header div.mdl-layout__header-row span.fd-breadcrumb a::text').get().lower()
        if not app_type:
            raise ValueError('App Type Error.')

        # market
        market = "fossdroid"

        app_detail = items.AppDetail(
            app_title=app_title, apk_name=apk_name, description=description, developer=settings.DEFAULT_DEVELOPER, app_link=app_link, category=app_type, market=market, version=app_version, picture_links=picture_links, size=settings.DEFAULT_SIZE, download_link=download_url, update_date=update_date
        )

        yield app_detail
