# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from .apkpure_spider import ApkPureSpider
from .fossdroid_spider import FossDroidSpider
from .xiaomi_spider import XiaomiSpider
from .github_spider import GithubSpider
from .opensource_spider import OpenSourceSpider

__all__ = ['ApkPureSpider', 'FossDroidSpider', 'XiaomiSpider', 'GithubSpider', 'OpenSourceSpider']
