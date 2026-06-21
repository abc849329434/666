# -*- coding: utf-8 -*-
# JavBus + 磁力 + 115 秒传 完整版
# TVBox / 不夜 / pySpider
# Python 3.9+

import re
import json
import time
import base64
import hashlib
import urllib.parse
import requests

from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class Spider:

    def __init__(self):
        self.UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"

        self.VERSION = "2026-05-26-javbus-115-final"

        # =========================
        # JAVBUS
        # =========================

        self.JAVBUS_BASES = [
            "https://www.javbus.com",
            "https://www.javbus.org",
            "https://www.javbus.one",
        ]

        self.JAVBUS_BASE = self.JAVBUS_BASES[0]

        self.JAVBUS_COOKIE = (
            "PHPSESSID=vittq8vf2fhopu6eemc0d452q5; "
            "existmag=mag; "
            "age=verified;"
        )

        # =========================
        # 115 COOKIE
        # =========================

        self.PAN_115_COOKIE = (
            "UID=102499290_R1_1769876709; "
            "CID=b9da9913cf6f6ce1206ac446738d4dc6; "
            "SEID=282eda490440b12f9122e9c54995bf56deed1ad88ed46c943d9a6c6f211ce9a3da4830940c1beddd968551db169ff1ec6d307a04d5f95a980a70d2f6; "
            "KID=78ee45569034ca7aaf204563d02b1d7f;"
        )

        self.session = requests.Session()

        retry = Retry(
            total=3,
            backoff_factor=1,
            allowed_methods=["GET", "POST"]
        )

        self.session.mount(
            "https://",
            HTTPAdapter(max_retries=retry)
        )

        self.session.verify = False

        self.session.headers.update({
            "User-Agent": self.UA,
            "Cookie": self.JAVBUS_COOKIE,
            "Referer": self.JAVBUS_BASE + "/"
        })

    # =========================================================
    # 工具
    # =========================================================

    def text(self, v):
        return str(v or "").strip()

    def clean(self, s):
        return re.sub(r"\s+", " ", self.text(s)).strip()

    def md5(self, s):
        return hashlib.md5(
            self.text(s).encode()
        ).hexdigest()

    def abs_url(self, url):
        if not url:
            return ""
        return urllib.parse.urljoin(
            self.JAVBUS_BASE + "/",
            url
        )

    def safe_name(self, name):
        return re.sub(
            r'[\\/:*?"<>|#$]',
            ' ',
            self.text(name)
        ).strip()

    def encode_id(self, obj):
        raw = json.dumps(obj, ensure_ascii=False)
        return base64.b64encode(
            raw.encode()
        ).decode()

    def decode_id(self, s):
        try:
            return json.loads(
                base64.b64decode(s).decode()
            )
        except:
            return {}

    # =========================================================
    # 请求
    # =========================================================

    def get_html(self, url):
        full = self.abs_url(url)

        r = self.session.get(
            full,
            timeout=20
        )

        r.encoding = "utf-8"

        return r.text

    # =========================================================
    # 磁力
    # =========================================================

    def normalize_magnet(self, url):
        url = self.text(url)

        m = re.search(
            r'btih:([0-9a-fA-F]{32,40})',
            url
        )

        if not m:
            return ""

        return (
            "magnet:?xt=urn:btih:"
            + m.group(1)
        )

    # =========================================================
    # 首页
    # =========================================================

    def homeContent(self, filter=False):

        classes = [
            {
                "type_id": "censored",
                "type_name": "有码"
            },
            {
                "type_id": "uncensored",
                "type_name": "无码"
            },
            {
                "type_id": "western",
                "type_name": "欧美"
            },
            {
                "type_id": "hd",
                "type_name": "高清"
            },
            {
                "type_id": "sub",
                "type_name": "字幕"
            }
        ]

        return {
            "class": classes
        }

    # =========================================================
    # 分类
    # =========================================================

    def categoryContent(
            self,
            tid,
            pg,
            filter=False,
            extend={}
    ):

        pg = int(pg or 1)

        path_map = {
            "censored": "/",
            "uncensored": "/uncensored",
            "western": "https://www.javbus.org",
            "hd": "/genre/hd",
            "sub": "/genre/sub"
        }

        path = path_map.get(tid, "/")

        if pg > 1:
            path = path.rstrip("/") + "/" + str(pg)

        html = self.get_html(path)

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        videos = []

        for a in soup.select("a.movie-box"):

            href = self.abs_url(
                a.get("href")
            )

            code = href.rstrip("/").split("/")[-1]

            img = a.select_one("img")

            title = self.clean(
                img.get("title")
                or img.get("alt")
                or code
            )

            pic = self.abs_url(
                img.get("src")
            )

            videos.append({
                "vod_id": code,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": code
            })

        return {
            "list": videos,
            "page": pg,
            "pagecount": pg + 1,
            "limit": 24,
            "total": 9999
        }

    # =========================================================
    # 搜索
    # =========================================================

    def searchContent(
            self,
            key,
            quick=False,
            pg=1
    ):

        pg = int(pg or 1)

        url = (
            "/search/"
            + urllib.parse.quote(key)
        )

        if pg > 1:
            url += "/" + str(pg)

        html = self.get_html(url)

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        videos = []

        for a in soup.select("a.movie-box"):

            href = self.abs_url(
                a.get("href")
            )

            code = href.rstrip("/").split("/")[-1]

            img = a.select_one("img")

            title = self.clean(
                img.get("title")
                or img.get("alt")
                or code
            )

            pic = self.abs_url(
                img.get("src")
            )

            videos.append({
                "vod_id": code,
                "vod_name": title,
                "vod_pic": pic,
                "vod_remarks": code
            })

        return {
            "list": videos
        }

    # =========================================================
    # 解析磁力
    # =========================================================

    def parse_magnets(self, code):

        html = self.get_html("/" + code)

        magnets = []

        def add_magnet(m):

            magnet = self.normalize_magnet(m)

            if magnet and magnet not in magnets:
                magnets.append(magnet)

        # 页面磁力

        for m in re.findall(
                r'magnet:\?xt=urn:btih:[^"\']+',
                html,
                re.I
        ):
            add_magnet(m)

        # ajax磁力

        gid = re.search(
            r'var gid\s*=\s*(\d+)',
            html
        )

        uc = re.search(
            r'var uc\s*=\s*(\d+)',
            html
        )

        img = re.search(
            r'var img\s*=\s*"([^"]+)"',
            html
        )

        if gid:

            gid = gid.group(1)

            uc = uc.group(1) if uc else "0"

            img = img.group(1) if img else ""

            ajax_url = (
                "/ajax/uncledatoolsbyajax.php?"
                f"gid={gid}"
                f"&lang=zh"
                f"&img={urllib.parse.quote(img)}"
                f"&uc={uc}"
                f"&floor=1"
            )

            try:

                ajax_html = self.get_html(
                    ajax_url
                )

                for m in re.findall(
                        r'magnet:\?xt=urn:btih:[^"\']+',
                        ajax_html,
                        re.I
                ):
                    add_magnet(m)

            except Exception as e:
                print("ajax magnet error:", e)

        return magnets

    # =========================================================
    # 115
    # =========================================================

    def build_115_headers(self):

        return {
            "User-Agent": self.UA,
            "Cookie": self.PAN_115_COOKIE,
            "Referer": "https://115.com/",
            "Origin": "https://115.com",
            "X-Requested-With": "XMLHttpRequest"
        }

    def push_magnet_to_115(self, magnet):

        try:

            uid_match = re.search(
                r'UID=(\d+)',
                self.PAN_115_COOKIE
            )

            if not uid_match:
                return None

            uid = uid_match.group(1)

            headers = self.build_115_headers()

            # 获取 sign

            r = requests.get(
                "https://115.com/?ct=offline&ac=space",
                headers=headers,
                timeout=15,
                verify=False
            )

            data = r.json()

            if not data.get("state"):
                return None

            sign = data.get("sign")

            tm = data.get("time")

            payload = {
                "url": magnet,
                "uid": uid,
                "sign": sign,
                "time": tm
            }

            r = requests.post(
                "https://115.com/web/lixian/?ct=lixian&ac=add_task_url",
                headers=headers,
                data=payload,
                timeout=20,
                verify=False
            )

            return r.json()

        except Exception as e:

            print("115 error:", e)

            return None

    # =========================================================
    # detail
    # =========================================================

    def detailContent(self, ids):

        code = ids[0]

        html = self.get_html("/" + code)

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        title = self.clean(
            soup.select_one("title")
            .text
            .replace("- JavBus", "")
        )

        img = soup.select_one(
            ".bigImage img"
        )

        pic = ""

        if img:
            pic = self.abs_url(
                img.get("src")
            )

        magnets = self.parse_magnets(code)

        play_urls = []

        # 115线路

        for idx, magnet in enumerate(magnets[:12]):

            pid = self.encode_id({
                "type": "115",
                "url": magnet
            })

            play_urls.append(
                f"115-{idx+1}${pid}"
            )

        # 直连线路

        for idx, magnet in enumerate(magnets[:12]):

            pid = self.encode_id({
                "type": "magnet",
                "url": magnet
            })

            play_urls.append(
                f"磁力-{idx+1}${pid}"
            )

        vod = {
            "vod_id": code,
            "vod_name": title,
            "vod_pic": pic,
            "type_name": "JAV视频",
            "vod_year": "",
            "vod_area": "日本",
            "vod_actor": "",
            "vod_director": "",
            "vod_content": title,
            "vod_play_from": "115秒传$$$磁力直连",
            "vod_play_url": (
                "#".join(play_urls[:12])
                + "$$$"
                + "#".join(play_urls[12:])
            )
        }

        return {
            "list": [vod]
        }

    # =========================================================
    # 播放
    # =========================================================

    def playerContent(
            self,
            flag,
            pid,
            vipFlags=[]
    ):

        data = self.decode_id(pid)

        ptype = data.get("type")

        magnet = data.get("url")

        # =====================================================
        # 115
        # =====================================================

        if ptype == "115":

            try:

                self.push_magnet_to_115(
                    magnet
                )

            except Exception as e:
                print("115 submit error:", e)

            return {
                "parse": 0,
                "playUrl": "",
                "url": magnet,
                "header": {
                    "User-Agent": self.UA
                }
            }

        # =====================================================
        # 磁力
        # =====================================================

        if ptype == "magnet":

            return {
                "parse": 0,
                "playUrl": "",
                "url": magnet,
                "header": {
                    "User-Agent": self.UA
                }
            }

        return {
            "parse": 1,
            "url": pid
        }

    # =========================================================
    # 兼容
    # =========================================================

    def getName(self):
        return "JavBus115"

    def init(self, extend=""):
        pass

    def isVideoFormat(self, url):
        return True

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass