# coding=utf-8
import os

import scrapy
import logging
import items


class GithubSpider(scrapy.Spider):
    name = "github"
    logger = logging.getLogger("GithubSpider")

    def start_requests(self):
        start_url = "https://github.com/search?q=APK&type=Commits"
        yield scrapy.Request(start_url, callback=self.parse_list)

    def parse_list(self, response):
        commit_urls = response.css('div#commit_search_results div.commit a.sha.btn::attr("href")').getall()
        for commit_url in commit_urls:
            yield scrapy.Request(
                response.urljoin(commit_url), callback=self.parse_commit
            )

        # parse next list
        next_list_url = response.css('a.next_page::attr("href")').get()
        if next_list_url:
            next_list_url = response.urljoin(next_list_url)
            yield scrapy.Request(
                response.urljoin(next_list_url), callback=self.parse_list
            )

    def parse_commit(self, response):
        for commit_file_dom in response.css("div#files div.file"):  # type: scrapy.Selector
            file_name = commit_file_dom.css("a.link-gray-dark::attr('title')").get()  # type: str
            file_url = commit_file_dom.css('details-menu.dropdown-menu a.btn-link::attr("href")').get()  # type: str
            if file_name.endswith(".apk"):  # likely to be a apk file
                yield scrapy.Request(
                    response.urljoin(file_url), callback=self.parse_file
                )

    def parse_file(self, response):
        # download url
        download_url = response.url.replace("/blob/", '/raw/')

        # author name
        author = response.css("div.application-main span.author a::text").get()
        if not author:
            raise ValueError("Developer Name error.")
        app_link = response.url
        market = "github"

        # project name
        project_name = response.css('main div.flex-auto strong.flex-self-stretch a::text').get()
        app_title = project_name
        apk_name = app_title

        # version
        file_name = os.path.splitext(os.path.basename(response.url))[0]
        path_list = response.url.split('/')  # type: list
        hash_index = path_list.index("blob") + 1
        sub_version_str = ""
        commit_hash = path_list[hash_index]
        for path in path_list[hash_index + 1:-1]:
            sub_version_str += "." + path[:2]
        version = file_name + "." + commit_hash[:8]
        if sub_version_str != "":
            version += sub_version_str
        version = version[:255]

        # update time
        update_date = response.css('span.d-none.d-md-inline relative-time::attr("datetime")').get()  # type: str
        if update_date:
            update_date = update_date.replace('T', " ").replace('Z', "")

        # description
        description = response.css("main div.repository-content div.Box div.Details-content--hidden pre::text").get()

        # size
        size = response.css("main div.repository-content div.Box div.Box-header div.text-mono.f6::text").get().strip()
        yield items.AppDetail(app_title=app_title, apk_name=apk_name, description=description, developer=author, app_link=app_link, market=market, version=version, size=size, download_link=download_url, update_date=update_date)
