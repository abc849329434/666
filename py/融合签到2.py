# -*- coding: utf-8 -*-
"""
TVBox 本地 Python 插件
三站合一：岁岁 + 小白白 + 夏夜
缓存：/sdcard/签到缓存/.sign_缓存_xxxx.json
"""
import json
import os
import time
import hashlib
import urllib.request
import urllib.parse

# ========== 用户配置 ==========
SIGN_KEY_SUISUI = "suisui"
SIGN_KEY_XBB    = "PUlVe6K2"
SIGN_KEY_XIAYE  = "转存下UC再要口令"
CACHE_DIR       = "/storage/emulated/0/Easybox/"
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_FILE      = os.path.join(CACHE_DIR,
                               "sign_缓存_{0}.json".format(
                                   hashlib.md5((SIGN_KEY_SUISUI + SIGN_KEY_XBB + SIGN_KEY_XIAYE).encode()).hexdigest()[:8]))
CACHE_TTL       = 3600
# ==============================

def _load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if time.time() - data.get("ts", 0) < CACHE_TTL:
            return data
    except Exception:
        pass
    return {}

def _save_cache(result):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({"ts": time.time(), "result": result}, f, ensure_ascii=False)

def _post(url, data):
    try:
        data = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("User-Agent", "Mozilla/5.0")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"status": "fail", "message": str(e)}

def _sign_all():
    cache = _load_cache()
    if cache:
        return cache["result"]
    msg = []
    # 1. 岁岁
    r = _post("http://sspa8.top:8100/qiandao.php", {"sign_key": SIGN_KEY_SUISUI})
    if r.get("status") == "success":
        msg.append("岁岁成功 小馒头={0}".format(r.get("call_count", 0)))
    else:
        msg.append("岁岁失败：{0}".format(r.get("message", "未知")))
    # 2. 小白白
    r = _post("http://xiaobaibai.feng1210.top/xiaobaibai_sign.php", {"sign_key": SIGN_KEY_XBB})
    if r.get("status") == "success":
        msg.append("小白白成功 剩余={0}".format(r.get("call_count", 0)))
    else:
        msg.append("小白白失败：{0}".format(r.get("message", "未知")))
    # 3. 夏夜
    r = _post("http://8.155.50.80/algorithm_sign.php", {"sign_key": SIGN_KEY_XIAYE})
    if r.get("status") == "success":
        msg.append("夏夜成功 次数={0}".format(r.get("call_count", 0)))
    else:
        msg.append("夏夜失败：{0}".format(r.get("message", "未知")))
    result = "；".join(msg)
    _save_cache(result)
    return result

# ========== TVBox Spider 规范 ==========
class Spider:

    def init(self, extend=""):
        pass

    def getDependence(self):
        return []

    def homeContent(self, filter_=None):
        return self._make_list()

    def categoryContent(self, tid, pg, filter_, extend):
        return self._make_list()

    def searchContent(self, key, quick=None):
        return self._make_list()

    def detailContent(self, ids):
        return self._make_list()

    def playerContent(self, flag, id_, vipFlags):
        return {"url": id_, "header": {}}

    def _make_list(self):
        tip = _sign_all()
        return {
            "list": [
                {
                    "vod_id": "1",
                    "vod_name": "签到提醒",
                    "vod_pic": "https://pic.616pic.com/ys_bnew_img/00/07/36/WkmKs2g5T4.jpg",
                    "vod_remarks": tip,
                }
            ]
        }