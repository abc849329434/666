# -*- coding: utf-8 -*-

import re
import ssl
import json
import html
import base64
import urllib3
import requests
import random
import sys

from urllib.parse import quote, unquote, urljoin
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pyquery import PyQuery as pq

sys.path.append("..")
from base.spider import Spider as BaseSpider

urllib3.disable_warnings()


class SSLAdapter(HTTPAdapter):

    def init_poolmanager(self, *args, **kwargs):

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        kwargs["ssl_context"] = ctx

        return super().init_poolmanager(*args, **kwargs)


class Spider(BaseSpider):

    hosts = [
        "https://www.qwmkv.com",
        "https://www.qwnull.com",
        "https://www.qwfilm.com",
        "https://www.qnmp4.com",
        "https://www.qn63.com"
    ]

    host = hosts[0]

    ua_list = [
        "Mozilla/5.0 (Linux; Android 13; SM-S9180) AppleWebKit/537.36 Chrome/125.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; M2102J2SC) AppleWebKit/537.36 Chrome/124.0.0.0 Mobile Safari/537.36",
        "okhttp/4.12.0",
        "Dalvik/2.1.0 (Linux; U; Android 13)"
    ]

    KEYWORDS = [
        "4k",
        "2160p",
        "蓝光",
        "remux",
        "原盘",
        "hdr",
        "dolby"
    ]

    def getName(self):
        return "七味-Pro终极版"

    def init(self, extend=""):

        self.session = requests.Session()

        retry = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[403, 429, 500, 502, 503, 504]
        )

        adapter = SSLAdapter(max_retries=retry)

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.session.verify = False

        self.session.headers.update(self.randHeaders())

        self.search_cache = {}

        self._probe_host()

    def randHeaders(self):

        return {
            "User-Agent": random.choice(self.ua_list),
            "Referer": self.host,
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive"
        }

    def _probe_host(self):

        for h in self.hosts:

            try:

                r = self.session.get(
                    h,
                    headers=self.randHeaders(),
                    timeout=5
                )

                if r.status_code == 200:
                    self.host = h.rstrip("/")
                    break

            except:
                pass

    def _full_url(self, url):

        if not url:
            return ""

        url = html.unescape(str(url)).strip()

        if url.startswith("//"):
            return "https:" + url

        if url.startswith(("http://", "https://", "magnet:", "push://")):
            return url

        return urljoin(self.host + "/", url.lstrip("/"))

    def _b64e(self, obj):

        txt = json.dumps(
            obj,
            ensure_ascii=False,
            separators=(",", ":")
        )

        return base64.urlsafe_b64encode(
            txt.encode()
        ).decode().rstrip("=")

    def _b64d(self, txt):

        try:

            txt += "=" * (-len(txt) % 4)

            return json.loads(
                base64.urlsafe_b64decode(txt.encode()).decode()
            )

        except:
            return {}

    def _score_name(self, name):

        n = (name or "").lower()

        score = 0

        for i, kw in enumerate(self.KEYWORDS):

            if kw.lower() in n:
                score += (len(self.KEYWORDS) - i)

        return score

    # 首页分类
    def homeContent(self, filter):

        classes = [
            {"type_name": "电影", "type_id": "1"},
            {"type_name": "剧集", "type_id": "2"},
            {"type_name": "综艺", "type_id": "3"},
            {"type_name": "动漫", "type_id": "4"},
            {"type_name": "短剧", "type_id": "30"}
        ]

        return {
            "class": classes,
            "filters": {}
        }

    # 首页推荐
    def homeVideoContent(self):

        try:

            r = self.session.get(
                self.host,
                headers=self.randHeaders(),
                timeout=10
            )

            r.encoding = "utf-8"

            doc = pq(r.text)

            videos = self._extract_video_list(doc)

            return {
                "list": videos
            }

        except:

            return {"list": []}

    # 分类
    def categoryContent(self, tid, pg, filter, extend):

        pg = int(pg)

        try:

            mid = re.search(r"(\d+)", str(tid)).group(1)

            if pg == 1:
                url = self._full_url(f"/type/{mid}.html")
            else:
                url = self._full_url(f"/type/{mid}-{pg}.html")

            r = self.session.get(
                url,
                headers=self.randHeaders(),
                timeout=10
            )

            r.encoding = "utf-8"

            doc = pq(r.text)

            videos = []

            selectors = [
                "ul.pic-list li",
                ".module-items .module-item",
                ".module-list .module-item",
                ".vodlist li",
                ".stui-vodlist li",
                ".myui-vodlist li",
                ".pic-list li"
            ]

            for sel in selectors:

                items = list(doc(sel).items())

                if len(items) < 1:
                    continue

                for li in items:

                    a = li("a").eq(0)

                    href = (
                        a.attr("href")
                        or li.find("a").attr("href")
                    )

                    if not href:
                        continue

                    title = (
                        a.attr("title")
                        or li.find("img").attr("alt")
                        or li.find(".module-item-title").text()
                        or li.find(".vod-title").text()
                        or li.find("h3").text()
                        or li.text()
                    )

                    img = (
                        li.find("img").attr("data-src")
                        or li.find("img").attr("data-original")
                        or li.find("img").attr("src")
                    )

                    remark = (
                        li.find(".module-item-note").text()
                        or li.find(".pic-text").text()
                        or li.find(".remarks").text()
                        or li.find(".tag").text()
                        or ""
                    )

                    videos.append({
                        "vod_id": href,
                        "vod_name": title.strip() if title else "未知",
                        "vod_pic": self._full_url(img),
                        "vod_remarks": remark.strip()
                    })

                break

            has_more = (
                "下一页" in r.text
                or "尾页" in r.text
                or f"/type/{mid}-{pg + 1}.html" in r.text
            )

            return {
                "list": videos,
                "page": pg,
                "pagecount": pg + 1 if has_more else pg,
                "limit": len(videos),
                "total": 9999
            }

        except Exception as e:

            print("分类错误:", str(e))

            return {
                "list": [],
                "page": pg,
                "pagecount": pg,
                "limit": 0,
                "total": 0
            }

    # 提取列表
    def _extract_video_list(self, doc):

        videos = []

        selectors = [
            "ul.pic-list li",
            ".module-items .module-item",
            ".module-list .module-item",
            ".vodlist li",
            ".stui-vodlist li",
            ".myui-vodlist li",
            ".pic-list li"
        ]

        for sel in selectors:

            items = list(doc(sel).items())

            if len(items) < 1:
                continue

            for li in items:

                a = li("a").eq(0)

                href = (
                    a.attr("href")
                    or li.find("a").attr("href")
                )

                if not href:
                    continue

                title = (
                    a.attr("title")
                    or li.find("img").attr("alt")
                    or li.find(".module-item-title").text()
                    or li.find(".vod-title").text()
                    or li.find("h3").text()
                    or li.text()
                )

                img = (
                    li.find("img").attr("data-src")
                    or li.find("img").attr("data-original")
                    or li.find("img").attr("src")
                )

                remark = (
                    li.find(".module-item-note").text()
                    or li.find(".pic-text").text()
                    or li.find(".remarks").text()
                    or li.find(".tag").text()
                    or ""
                )

                videos.append({
                    "vod_id": href,
                    "vod_name": title.strip() if title else "未知",
                    "vod_pic": self._full_url(img),
                    "vod_remarks": remark.strip()
                })

            break

        return videos

    # 详情
    def detailContent(self, ids):

        try:

            vod_id = ids[0]

            url = self._full_url(vod_id)

            r = self.session.get(
                url,
                headers=self.randHeaders(),
                timeout=10
            )

            r.encoding = "utf-8"

            doc = pq(r.text)

            title = doc("h1").text().strip()

            pic = self._full_url(
                doc("img").attr("src")
            )

            content = (
                doc(".movie-introduce").text()
                or doc(".content").text()
            )

            play_from = []
            play_url = []

            online = []
            pan = []
            magnet = []

            for a in doc("a[href]").items():

                href = a.attr("href") or ""
                name = a.text().strip() or "播放"

                if "magnet:?" in href:

                    magnet.append(
                        f"{name}${href}"
                    )

                elif any(x in href for x in [
                    "pan.quark.cn",
                    "115.com",
                    "aliyundrive",
                    "alipan",
                    "pan.baidu"
                ]):

                    pan.append(
                        f"{name}$" + self._b64e({
                            "type": "pan",
                            "url": href
                        })
                    )

            for a in doc("ul.player a, .player a").items():

                name = a.text().strip()

                href = a.attr("href")

                if not href:
                    continue

                online.append(
                    f"{name}$" + self._b64e({
                        "type": "play",
                        "url": self._full_url(href)
                    })
                )

            if online:
                play_from.append("在线")
                play_url.append("#".join(online))

            if pan:

                pan.sort(
                    key=lambda x: -self._score_name(
                        x.split("$")[0]
                    )
                )

                play_from.append("网盘")
                play_url.append("#".join(pan))

            if magnet:

                magnet.sort(
                    key=lambda x: -self._score_name(
                        x.split("$")[0]
                    )
                )

                play_from.append("磁力")
                play_url.append("#".join(magnet))

            vod = {
                "vod_id": vod_id,
                "vod_name": title,
                "vod_pic": pic,
                "vod_content": content,
                "vod_play_from": "$$$".join(play_from),
                "vod_play_url": "$$$".join(play_url)
            }

            return {
                "list": [vod]
            }

        except:

            return {"list": []}

    # 播放
    def playerContent(self, flag, id, vipFlags):

        try:

            if id.startswith("magnet:?"):

                return {
                    "parse": 0,
                    "url": "push://" + id
                }

            data = self._b64d(id)

            url = data.get("url", id)

            tp = data.get("type", "")

            if tp == "pan":

                return {
                    "parse": 0,
                    "url": "push://" + url
                }

            if tp == "play":

                r = self.session.get(
                    url,
                    headers=self.randHeaders(),
                    timeout=10
                )

                text = r.text

                m = re.search(
                    r'player_aaaa\s*=\s*(\{.*?\})',
                    text
                )

                if m:

                    j = json.loads(m.group(1))

                    real = j.get("url", "")

                    enc = str(j.get("encrypt", "0"))

                    if enc == "1":
                        real = unquote(real)

                    elif enc == "2":

                        real = unquote(
                            base64.b64decode(real).decode()
                        )

                    if ".m3u8" in real or ".mp4" in real:

                        return {
                            "parse": 0,
                            "url": real
                        }

                    return {
                        "parse": 1,
                        "url": real
                    }

                m3u8 = re.search(
                    r'https?:\/\/[^"\']+?\.m3u8[^"\']*',
                    text
                )

                if m3u8:

                    return {
                        "parse": 0,
                        "url": m3u8.group()
                    }

                mp4 = re.search(
                    r'https?:\/\/[^"\']+?\.mp4[^"\']*',
                    text
                )

                if mp4:

                    return {
                        "parse": 0,
                        "url": mp4.group()
                    }

                iframe = re.search(
                    r'<iframe.*?src=["\'](.*?)["\']',
                    text,
                    re.S
                )

                if iframe:

                    return {
                        "parse": 1,
                        "url": self._full_url(
                            iframe.group(1)
                        )
                    }

                return {
                    "parse": 1,
                    "url": url
                }

            return {
                "parse": 1,
                "url": url
            }

        except:

            return {
                "parse": 1,
                "url": id
            }

    # 搜索
    def searchContent(self, key, quick, pg="1"):

        if key in self.search_cache:
            return self.search_cache[key]

        try:

            wd = quote(key)

            api = (
                f"{self.host}/api.php/provide/vod"
                f"?ac=detail&wd={wd}"
            )

            r = self.session.get(
                api,
                headers=self.randHeaders(),
                timeout=10
            )

            data = r.json()

            videos = []

            for it in data.get("list", []):

                videos.append({
                    "vod_id": f"/mv/{it['vod_id']}.html",
                    "vod_name": it["vod_name"],
                    "vod_pic": it["vod_pic"],
                    "vod_remarks": it.get("vod_remarks", "")
                })

            result = {
                "list": videos
            }

            self.search_cache[key] = result

            return result

        except:

            try:

                url = (
                    f"{self.host}/search/"
                    f"{quote(key)}----------1---.html"
                )

                r = self.session.get(
                    url,
                    headers=self.randHeaders(),
                    timeout=10
                )

                r.encoding = "utf-8"

                doc = pq(r.text)

                return {
                    "list": self._extract_video_list(doc)
                }

            except:

                return {"list": []}