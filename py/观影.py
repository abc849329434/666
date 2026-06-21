import re
import sys
import json
import random
import base64
from urllib.parse import urljoin
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base.spider import Spider

sys.path.append('..')


class Spider(Spider):
    headers = {
        'User-Agent': 'okhttp/4.12.0'
    }

    FIXED_CONFIG = {
        'hosts': [
            "http:// am4kjx.lyyytv.cn ",
            'http://cms339.lyyytv.cn',
            'http://pgcms.lyyytv.cn',
            'http://cms4kzj.lyyytv.cn',
            'http://cms.lygdyy.cn'
        ],
        'cmskey': 'wP5btxoc3yv8FoBQENFZumF0EUYr4LTy',
        'RawPlayUrl': 0
    }

    def init(self, extend=''):
        self.hosts = self.FIXED_CONFIG.get('hosts', [])
        random.shuffle(self.hosts)

        self.cmskey = self.FIXED_CONFIG.get('cmskey', '')
        self.raw_play_url = int(self.FIXED_CONFIG.get('RawPlayUrl', 0))

    # ================= 核心：多域名轮询 =================
    def fetch_host(self, path, **kwargs):
        last_err = None
        for host in self.hosts:
            try:
                url = host.rstrip('/') + '/' + path.lstrip('/')
                resp = self.fetch(url, headers=self.headers, timeout=10, **kwargs)
                if resp.status_code == 200:
                    return resp
            except Exception as e:
                last_err = e
                continue
        raise last_err or Exception("所有域名均不可用")

    # ===================================================

    def homeContent(self, filter):
        data = self.fetch_host("api.php/app/nav?token=").json()
        keys = ["class", "area", "lang", "year", "letter", "by", "sort"]

        filters = {}
        classes = []

        for item in data['list']:
            classes.append({
                "type_name": item["type_name"],
                "type_id": item["type_id"]
            })

            has_filter = any(
                k in item["type_extend"] and item["type_extend"][k].strip()
                for k in keys
            )

            if not has_filter:
                continue

            filters[str(item["type_id"])] = []

            for k in keys:
                if k in item["type_extend"] and item["type_extend"][k].strip():
                    values = item["type_extend"][k].split(",")
                    value_array = [
                        {"n": v.strip(), "v": v.strip()}
                        for v in values if v.strip()
                    ]
                    filters[str(item["type_id"])].append({
                        "key": k,
                        "name": k,
                        "value": value_array
                    })

        return {"class": classes, "filters": filters}

    def homeVideoContent(self):
        data = self.fetch_host("api.php/app/index_video?token=").json()
        videos = []
        for item in data['list']:
            videos.extend(item['vlist'])
        return {'list': videos}

    def categoryContent(self, tid, pg, filter, extend):
        params = [
            f"tid={tid}",
            f"pg={pg}",
            "limit=18"
        ]

        if extend.get('class'):
            params.append(f"class={extend['class']}")
        if extend.get('area'):
            params.append(f"area={extend['area']}")
        if extend.get('lang'):
            params.append(f"lang={extend['lang']}")
        if extend.get('year'):
            params.append(f"year={extend['year']}")

        url = "api.php/app/video?" + "&".join(params)
        data = self.fetch_host(url).json()
        return data

    def searchContent(self, key, quick, pg="1"):
        data = self.fetch_host(
            f"api.php/app/search?text={key}&pg={pg}"
        ).json()

        for item in data.get('list', []):
            item.pop('type', None)

        return {'list': data.get('list', []), 'page': pg}

    def detailContent(self, ids):
        data = self.fetch_host(
            f"api.php/app/video_detail?id={ids[0]}"
        ).json()['data']

        play_from = []
        play_urls = []

        for i in data['vod_url_with_player']:
            urls = []
            for u in i['url'].split('#'):
                if u:
                    name, url = u.split('$', 1)
                    urls.append(f"{name}${self.lvdou(url)}")

            play_from.append(i['name'].strip())
            play_urls.append('#'.join(urls))

        data.pop('vod_url_with_player', None)
        data['vod_play_from'] = '$$$'.join(play_from)
        data['vod_play_url'] = '$$$'.join(play_urls)

        return {'list': [data]}

    def playerContent(self, flag, video_id, vipFlags):
        jx = 0

        if self.check_paly_url(video_id):
            if self.raw_play_url == 1:
                video_id = self.raw_url(video_id)
        elif re.search(
            r'(?:www\.iqiyi|v\.qq|v\.youku|www\.mgtv|www\.bilibili)\.com',
            video_id
        ):
            jx = 1

        return {
            'jx': jx,
            'playUrl': '',
            'parse': 0,
            'url': video_id,
            'header': self.headers
        }

    # ================= 工具方法 =================

    def lvdou(self, text):
        prefix = "lvdou+"
        if not text.startswith(prefix):
            return text

        key = self.cmskey[:16].encode()
        iv = self.cmskey[-16:].encode()

        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            ct = base64.b64decode(text[len(prefix):])
            pt = cipher.decrypt(ct)
            return unpad(pt, AES.block_size).decode()
        except Exception:
            return text

    def raw_url(self, url):
        try:
            r = self.fetch(url, allow_redirects=False, timeout=20)
            if 300 <= r.status_code < 400:
                loc = r.headers.get('Location')
                if loc:
                    return urljoin(url, loc)
        except Exception:
            pass
        return url

    def check_paly_url(self, text):
        return bool(re.search(
            r"https?://.*(?:\.(?:mp4|m3u8|flv|avi|mkv|ts|mov|wmv|webm)|lyyytv\.cn/)",
            text,
            re.I
        ))

    def getName(self):
        return "LYYY多域"

    def isVideoFormat(self, url):
        return bool(re.search(r"\.(mp4|m3u8|flv)$", url, re.I))

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass
