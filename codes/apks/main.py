# coding=utf-8
import click
import time
import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders import *


@click.command()
@click.option("--market_name", "-m", default="fossdroid", type=click.Choice(["fossdroid", "xiaomi", "apkpure", "github", "github_opensource"], case_sensitive=False), help="Market Name in ['fossdroid', 'xiaomi', 'apkpure', 'github', 'github_opensource']. Default is fossdroid.")
@click.option("--using_log_file", "-l", expose_value=True, is_flag=True, help="Whether use log file to save the log information, default is False.")
@click.option("--log_level", "-v", default="INFO", type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']), help="Log level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']. Default is INFO")
@click.option("--using_proxy", "-u", default=False, type=bool, is_flag=True, help="Whether use proxy server on 127.0.0.1:10809.")
def main(market_name: str = "fossdroid", using_log_file: bool = False, log_level: str = "INFO", using_proxy: bool = False):
    if market_name == "xiaomi":
        spider = XiaomiSpider
    elif market_name == "fossdroid":
        spider = FossDroidSpider
    elif market_name == "apkpure":
        spider = ApkPureSpider
    elif market_name == "github":
        spider = GithubSpider
    elif market_name == "github_opensource":
        spider = OpenSourceSpider
    else:
        raise ValueError("Market Name Error.")

    start_time = str(int(time.time()))
    cur_folder = os.path.dirname(__file__)
    log_folder = os.path.join(cur_folder, "../../log/")
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    process = CrawlerProcess(get_project_settings())
    if using_log_file:
        log_file = os.path.join(log_folder, "{}.{}.txt".format(start_time, market_name))
        process.settings.set('LOG_FILE', log_file)  # for developer environment
    if using_proxy:
        process.settings.set("USING_PROXY", True)
    process.settings.set('LOG_LEVEL', log_level)
    process.crawl(spider)
    process.start()


if __name__ == '__main__':
    main()
