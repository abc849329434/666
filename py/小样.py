# coding = utf-8
#!/usr/bin/python
from urllib.parse import unquote
from urllib.parse import quote
from base.spider import Spider
from bs4 import BeautifulSoup
from collections import Counter
import urllib.request
import urllib.parse
import threading
import requests
import binascii
import base64
import json
import time
import sys
import re
import os

sys.path.append('..')

xurl = "http://xsayang.fun:12512/index.php"


QuarkCookie="ck"

UCCookie = "ck"

BaiduCookie = "ck"

headers = {
    'Content-Type': "",
    'referer': 'https://drive.uc.cn/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Cookie': UCCookie
}
headerx = {
  'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/2.5.20 Chrome/100.0.4896.160 Electron/18.3.5.12-a038f7b798 Safari/537.36 Channel/pckk_other_ch",
  'referer': "https://pan.quark.cn/",
  'Cookie': QuarkCookie
}
headerz = {
    'User-Agent': "netdisk;1.4.2;22021211RC;android-android;12;JSbridge4.4.0;jointBridge;1.1.0;",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Referer': "https://pan.baidu.com",
    'Cookie': BaiduCookie
}
header_ = {
        'User-Agent': "Dart/2.19(dart:io)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'referer': "https://www.123pan.com/",
        'origin': "https://www.123pan.com",
        'platform': "android",
        'app-version': "3",
    }
header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
}
pm = ''

class Spider(Spider):
    global xurl
    global headerx
    global headers
    global header
    global headerz
    global header_

    def getName(self):
        return "首页"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        result = {}
        result = {"class": [
                            {"type_id": "35", "type_name": "123"}
                            ],
                  }

        return result
    def homeVideoContent(self):
        pass

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []
        url = f'{xurl}/vod/show/id/{cid}/page/{pg}.html'
        res = requests.get(url=url, headers=header)
        res.encoding = "utf-8"
        doc = BeautifulSoup(res.text, 'lxml')
        soups = doc.find_all('div', class_='module-item')
        for i in soups:
            id = i.find('a')['href']
            match = re.search(r'/id/(\d+)', id)
            if match:
                bid = match.group(1)
            name = i.find('a')['title']
            pic = i.find('img')['data-src']
            remarks = i.find('div', class_='module-item-text').text

            video = {
                "vod_id": bid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remarks
            }
            videos.append(video)
        result = {'list': videos}
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        result = {}
        videos = []
        play_form = ""
        play_kurl = []
        play_urls = []
        did = ids[0]
        url = f'{xurl}/vod/detail/id/{did}.html'
        res = requests.get(url=url, headers=header)
        res.encoding = "utf-8"
        doc = BeautifulSoup(res.text, 'lxml')
        soups = doc.find('div', class_='video-info')
        name = soups.find('h1').text
        actors_title = soups.find('span', class_='video-info-itemtitle', string='主演：')
        if actors_title:
            actors_container = actors_title.find_next('div', class_='video-info-item')
            actor_links = actors_container.find_all('a', target='_blank')
            actors = ' / '.join([actor.text.strip() for actor in actor_links])
        director = soups.find('span', class_='video-info-items')
        content = soups.find('p').text
        content = content.replace('\xa0', '').replace('\u3000', '')
        content = ' '.join(content.split())
        remarks = soups.find('div', class_='tag-link').text.replace('\n', '')
        tag_links = soups.find_all('a', class_='tag-link')
        if len(tag_links) > 1:
            year = tag_links[1].text.strip()
        if len(tag_links) > 1:
            area = tag_links[2].text.strip()
        kjson = doc.find('div', id='download-list')
        if kjson:
            tab_content = kjson.find('div', class_='module-tab-content')
            if tab_content:
                tabs = tab_content.find_all('div', class_='module-tab-item')
                sources = []
                for item in tabs:
                    span = item.find('span')
                    if span and span.get('data-dropdown-value'):
                        source_name = span.get('data-dropdown-value')
                        sources.append(source_name)
                play_form = '$$$'.join(sources)
            row = kjson.find('div', class_='scroll-box-y')
            if row:
                kurl = row.find_all('div', class_='module-row-info')
                for k in kurl:
                    urls = k.find('p').text.strip()
                    id = 'http://sspa8.top:8100/api/vips.php?url=' + urls
                    res = requests.get(url=id, headers=header)
                    kjson = res.json()
                    if 'list' in kjson and kjson['list']:
                        for i in kjson['list']:
                            play_urls = i['vod_play_url']
                            play_kurl.append(''.join(play_urls).rstrip('#'))
                play_url1 = '$$$'.join(play_kurl)

            video = {
                "vod_id": did,
                "vod_name": name,
                "vod_actor": actors,
                "vod_director": director.text if director else "",
                "vod_content": content,
                "vod_remarks": '臻彩视界',
                "vod_year": year,
                "vod_area": area,
                "vod_play_from": play_form,
                "vod_play_url": play_url1
            }
            videos.append(video)

            result['list'] = videos
            return result
    def playerContent(self, flag, id, vipFlags):
        result = {}
        if '123' in id:
            bid = "http://sspa8.top:8100/api/sui.php?url=" + id
            res = requests.get(url=bid, headers=header_)
            if res.status_code == 200:
                kjson = res.json()
                url = kjson['url']
                result = {}
                result["parse"] = 0
                result["playUrl"] = ''
                result["url"] = url
                result["header"] = header_
                return result
        elif 'baidu' in id:
            uid = "http://sspa8.top:8100/api/sui.php?url=" + id
            res = requests.get(url=uid, headers=headerz)
            if res.status_code == 200:
                kjson = res.json()
                url = kjson['url']
                result = {}
                result["parse"] = 0
                result["playUrl"] = ''
                result["url"] = url
                result["header"] = headerz
                return result
        elif 'quark' in id:
            bid = "http://sspa8.top:8100/api/sui.php?url=" + id
            res = requests.get(url=bid, headers=headerx)
            if res.status_code == 200:
                kjson = res.json()
                url = kjson['url']
                result = {}
                result["parse"] = 0
                result["playUrl"] = ''
                result["url"] = url
                result["header"] = headerx
                return result
        elif 'UC' in id:
                id = "http://sspa8.top:8100/suisui.php?url=" + id
                res = requests.get(url=id, headers=headers)
                if res.status_code == 200:
                    kjson = res.json()
                    url = kjson['url']
                    result = {}
                    result["parse"] = 0
                    result["playUrl"] = ''
                    result["url"] = url
                    result["header"] = headers
                    return result

    def searchContentPage(self, key, quick, page):
        result = {}
        videos = []
        if not page:
            page = 1
        url = f'{xurl}/vod/search/page/{page}/wd/{key}.html'
        res = requests.get(url=url, headers=header)
        res.encoding = "utf-8"
        res = res.text
        doc = BeautifulSoup(res, 'lxml')
        soups = doc.find_all('div', class_='module-search-item')
        for i in soups:
            img_tag = i.find('img')
            info_tag = i.find('div', class_='video-info')

            if img_tag and info_tag:
                pic = img_tag.get('data-src') or img_tag.get('src')
            id = i.find('a')['href']
            match = re.search(r'/id/(\d+)', id)
            if match:
                bid = match.group(1)
            name = i.find('img')['alt']
            remarks = info_tag.find('a', class_='video-serial').text
            video = {
                "vod_id": bid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remarks
            }
            videos.append(video)
        result = {'list': videos}
        result['page'] = page
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def searchContent(self, key, quick, pg="1"):
        return self.searchContentPage(key, quick, '1')

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None