# coding=utf-8
import scrapy
import logging
import items
from settings import crawler_key_words


class OpenSourceSpider(scrapy.Spider):
    name = "Github Open Source"
    logger = logging.getLogger("OpenSourceSpider")

    def start_requests(self):
        # define keywords
        keywords = crawler_key_words

        start_url = "https://github.com/search?q={}&type=Repositories"
        for keyword in keywords:
            yield scrapy.Request(start_url.format(keyword), callback=self.parse_list)

    def parse_list(self, response):
        repository_urls = response.css("div.application-main ul.repo-list li.repo-list-item div.f4 a::attr('href')").getall()

        for repository_url in repository_urls:
            yield scrapy.Request(
                response.urljoin(repository_url), callback=self.parse_repository
            )

        # parse next list
        next_list_url = response.css('a.next_page::attr("href")').get()
        if next_list_url:
            next_list_url = response.urljoin(next_list_url)
            yield scrapy.Request(
                response.urljoin(next_list_url), callback=self.parse_list
            )

    def parse_repository(self, response):
        # author name
        author = response.css("div.application-main span.author a::text").get()
        if not author:
            raise ValueError("Developer Name Error.")
        app_link = response.url

        # project name
        project_name = response.css('main div.flex-auto strong.flex-self-stretch a::text').get()

        # update time
        update_date = response.css("relative-time::attr('datetime')").get()
        if not update_date:
            date_time = response.css("time-ago::attr('datetime')").getall()
            if len(date_time) > 0:
                update_date = date_time[0]
                for _index_ in range(1, len(date_time)):
                    update_date = date_time[_index_] if date_time[_index_] > update_date else update_date
        try:
            update_date = update_date.replace('T', ' ').replace('Z', ' ')
        except Exception:
            logging.warning("Load Update Info Error for {}".format(response.url))
            yield scrapy.Request(response.url, callback=self.parse_repository)
        else:
            # description
            description = response.css("div.repository-content div.BorderGrid div.BorderGrid-cell p::text").get()
            if not description:
                description = "No Description."
            else:
                description = description.strip()

            # download url
            zip_url = response.css("div.repository-content details.details-overlay ul.list-style-none li.Box-row a::attr('href')").getall()[1]
            zip_url = response.urljoin(zip_url)

            info = {
                "author": author,
                "app_link": app_link,
                "project_name": project_name,
                "update_date": update_date,
                "description": description,
                "download_url": zip_url
            }

            yield scrapy.Request(
                response.url, callback=self.parse_folder_check, meta=info
            )

    def parse_folder_check(self, response):
        # check whether a android project
        svg_labels = response.css("div.repository-content div.Details div.Box-row svg::attr('aria-label')").getall()
        files_and_folders = response.css("div.repository-content div.Details div.Box-row div[role='rowheader'] a::text").getall()
        assert len(svg_labels) == len(files_and_folders)
        is_file = [svg_label == "File" for svg_label in svg_labels]
        is_android_project = False
        for _index_ in range(len(files_and_folders)):
            if is_file[_index_] and 'build.gradle' == files_and_folders[_index_]:
                is_android_project = True

        if is_android_project:
            app_link = response.meta['app_link']
            project_name = response.meta['project_name']
            app_title = apk_name = project_name

            yield items.AppDetail(app_title=app_title, apk_name=apk_name, description=response.meta['description'], developer=response.meta['author'], app_link=app_link, market="github_opensource", version=response.meta['update_date'].split()[0], download_link=response.meta['download_url'], update_date=response.meta['update_date'])
        else:
            files_and_folders_url = response.css("div.repository-content div.Details div.Box-row div[role='rowheader'] a::attr('href')").getall()
            assert len(files_and_folders_url) == len(svg_labels)
            is_folder = [svg_label == "Directory" for svg_label in svg_labels]
            for _index_ in range(len(files_and_folders_url)):
                if is_folder[_index_]:
                    yield scrapy.Request(
                        response.urljoin(files_and_folders_url[_index_]), callback=self.parse_folder_check
                    )
