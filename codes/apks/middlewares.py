# -*- coding: utf-8 -*-
import logging
import random

import settings


class UserAgentMiddleware:
    logger = logging.getLogger("User Agent Middleware")

    def process_request(self, request, spider):
        random_ua = random.choice(settings.USER_AGENT_LIST)
        request.headers['User-Agent'] = random_ua
        if spider.settings["USING_PROXY"]:
            request.meta['proxy'] = settings.PROXY_PATH
