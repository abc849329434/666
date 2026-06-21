# -*- coding:utf-8 -*-
import requests
import json
import time


class Spider:

    def init(self, extend=""):
        ext = json.loads(extend)

        self.host = "http://110.42.3.227:12356/xiaohuangren.php"

        # 👉 从ext拿header
        self.header = ext.get("header", {})

    # ================= 公共请求 =================
    def post(self, data):
        try:
            # 👉 动态时间（有些接口会校验）
            self.header["build-time"] = str(int(time.time() * 1000))

            res = requests.post(
                self.host,
                json=data,
                headers=self.header,
                timeout=10
            )

            return res.json()

        except Exception as e:
            print("请求失败:", e)
            return {}

    # ================= 首页 =================
    def homeContent(self, filter):
        return {
            "class": [
                {"type_name": "随看", "type_id": "2"}
            ]
        }

    # ================= 分类 =================
    def categoryContent(self, tid, pg, filter, extend):

        data = self.post({
            "tid": tid,
            "page": pg
        })

        return data

    # ================= 详情 =================
    def detailContent(self, ids):

        data = self.post({
            "id": ids[0]
        })

        return data

    # ================= 播放 =================
    def playerContent(self, flag, id, vipFlags):

        try:
            real_id = id.split("|")[0]

            # ---------- NSYS ----------
            if real_id.startswith("NSYS-"):

                file_id = real_id.replace("NSYS-", "")

                play_url = f"https://vip.nsapi.sbs/nsys/proxy.php?file={file_id}.m3u8"

                return {
                    "parse": 0,
                    "url": play_url,
                    "header": {
                        "User-Agent": "Mozilla/5.0"
                    }
                }

            # ---------- NBY ----------
            elif real_id.startswith("NBY-"):

                key = id.split("|")[1] if "|" in id else ""

                play_url = f"https://vip.nsapi.sbs/nby/api.php?id={real_id}&key={key}"

                return {
                    "parse": 0,
                    "url": play_url
                }

            # ---------- ROSE ----------
            elif real_id.startswith("rose_"):

                play_url = f"https://vip.nsapi.sbs/rose/api.php?id={real_id}"

                return {
                    "parse": 0,
                    "url": play_url
                }

        except Exception as e:
            print("播放解析错误:", e)

        return {"parse": 1, "url": ""}

    # ================= 搜索（可选） =================
    def searchContent(self, key, quick):

        data = self.post({
            "wd": key
        })

        return data