import json
import urllib.parse
import requests
from base.spider import Spider as BaseSpider

class Spider(BaseSpider):
    _session = requests.Session()
    _session.headers.update(
        {"User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36"}
    )
    API_BASE = "https://api.cenguigui.cn/api/duanju/api.php"

    # ---------- 工具 ---------- #
    def _get(self, url: str, params=None) -> dict:
        try:
            resp = self._session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return {}

    # ========== 返回 ========== #
    def homeContent(self, filter):
        classes = [
            {"type_id": "新剧", "type_name": "新剧"},
            {"type_id": "系统", "type_name": "系统"},
            {"type_id": "重生", "type_name": "重生"},
            {"type_id": "下乡", "type_name": "下乡"},
            {"type_id": "乡下", "type_name": "乡下"},
            {"type_id": "古代", "type_name": "古代"},
            {"type_id": "穿越", "type_name": "穿越"},
            {"type_id": "战神", "type_name": "战神"},
            {"type_id": "开局", "type_name": "开局"},
            {"type_id": "逆袭", "type_name": "逆袭"},
            {"type_id": "女帝", "type_name": "女帝"},
            {"type_id": "神医", "type_name": "神医"},
            {"type_id": "总裁", "type_name": "总裁"},
            {"type_id": "萌宝", "type_name": "萌宝"},
            {"type_id": "都市", "type_name": "都市"},
        ]
        return {"class": classes, "list": []}

    def homeVideoContent(self):
        return {"list": []}

    def categoryContent(self, tid, pg, filter, extend):
        pg = pg or "1"
        data = self._get(f"{self.API_BASE}?name={urllib.parse.quote(tid)}&page={pg}").get("data", [])
        videos = [
            {
                "vod_id": item["book_id"],
                "vod_name": item["title"],
                "vod_pic": item["cover"],
                "vod_remarks": f"{item['episode_cnt']}集",
            }
            for item in data
        ]
        return {
            "list": videos,
            "page": int(pg),
            "pagecount": 20,
            "limit": 20,
            "total": 1000,
        }

    def detailContent(self, ids):
        book_id = ids[0]
        info = self._get(f"{self.API_BASE}?book_id={book_id}")
        if info.get("code") != 200:
            return {"list": []}

        episodes = info.get("data", [])
        play_urls = []
        for idx, ep in enumerate(episodes):
            if idx:
                play_urls.append("#")
            play_urls.append(f"{ep['title']}${ep['video_id']}")
        play_url = "".join(play_urls)

        vod = {
            "vod_id": book_id,
            "vod_name": info.get("book_name", ""),
            "vod_pic": "",
            "vod_play_from": "短剧",
            "vod_play_url": play_url,
            "vod_actor": "",
            "vod_director": "",
            "vod_content": info.get("desc", ""),
            "vod_year": "",
            "vod_area": "",
            "vod_remarks": info.get("category", ""),
        }
        return {"list": [vod]}

    def searchContent(self, key, quick, pg="1"):
        data = self._get(f"{self.API_BASE}?name={urllib.parse.quote(key)}").get("data", [])
        videos = [
            {
                "vod_id": item["book_id"],
                "vod_name": item["title"],
                "vod_pic": item["cover"],
                "vod_remarks": f"{item['episode_cnt']}集",
            }
            for item in data
        ]
        return {"list": videos, "page": int(pg)}

    def playerContent(self, flag, id, vipFlags):
        video_id = id[id.rfind("=") + 1 :] if "video_id=" in id else id
        info = self._get(f"{self.API_BASE}?video_id={video_id}")
        if info.get("code") != 200:
            return {"parse": 0, "url": "", "header": {}}

        m3u8 = info.get("data", {}).get("url", "")
        if not m3u8:
            return {"parse": 0, "url": "", "header": {}}

        return {"parse": 0, "url": m3u8, "header": {}}

    # ---------- 可选占位 ----------
    def init(self, extend=""):
        pass
    def getName(self):
        return "短剧-py"
    def isVideoFormat(self, url):
        return False
    def manualVideoCheck(self):
        pass
    def destroy(self):
        pass
    def localProxy(self, param):
        pass
    def liveContent(self, url):
        pass
