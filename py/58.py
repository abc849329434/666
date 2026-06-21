# coding=utf-8
# !/usr/bin/python
"""
作者 xiaye 内容仅供交流学习使用 版权归原创者所有 如侵犯了您的权益 请通知作者 将及时删除侵权内容

"""
from base.spider import Spider
import requests
import json
import time
import re

xurl = "https://1026a.shreade.com:8999/addons/appto/app.php"

headers = {
    'User-Agent': 'Dart/3.8 (dart:io)',
    'version': '1.0.0',
    'accept-encoding': 'gzip',
    'host': '1026a.shreade.com:8999',
    'content-type': 'application/json',
    'clienttype': 'mobile'
}

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
}

class Spider(Spider):
    def getName(self):
        return "58视频"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def fetch_search(self, payload):
        videos = []
        urlz = f'{xurl}/tindex/home_vod_list2'
        
        timestamp = int(time.time() * 1000)
        headers['timestamp'] = str(timestamp)
        
        try:
            response = requests.post(url=urlz, headers=headers, json=payload, timeout=10)
            
            if 'ENCRYPTION' in response.headers and response.headers['ENCRYPTION'] == '1':
                data = self.decrypt_response(response.text)
            else:
                data = response.json()
            
            if data['code'] == 1 and 'data' in data and 'vods' in data['data']:
                vod_list = data['data']['vods']
                for vod in vod_list:
                    video = {
                        "vod_id": tr(vod['vod_id']),
                        "vod_name": vod['vod_name'],
                        "vod_pic": self.fix_pic_url(vod['vod_pic']),
                        "vod_remarks": vod['vod_remarks'] if 'vod_remarks' in vod else ''
                    }
                    videos.append(video)
        except:
            pass
        
        return videos

    def fetch_search_results(self, keyword, page=1, limit=24):
        videos = []
        urlz = f'{xurl}/tindex/search_film'
        
        timestamp = int(time.time() * 1000)
        headers['timestamp'] = str(timestamp)
        
        payload = {
            "Limit": limit,
            "Page": page,
            "Search": keyword,
            "type": None
        }
        
        try:
            response = requests.post(url=urlz, headers=headers, json=payload, timeout=10)
            
            if 'ENCRYPTION' in response.headers and response.headers['ENCRYPTION'] == '1':
                data = self.decrypt_response(response.text)
            else:
                data = response.json()
            
            if data['code'] == 1 and 'data' in data and 'vods' in data['data']:
                vod_data = data['data']['vods']
                if 'list' in vod_data and vod_data['list']:
                    vod_list = vod_data['list']
                    for vod in vod_list:
                        video = {
                            "vod_id": str(vod['vod_id']),
                            "vod_name": vod['vod_name'],
                            "vod_pic": self.fix_pic_url(vod['vod_pic']),
                            "vod_remarks": vod.get('vod_remarks', '')
                        }
                        videos.append(video)
                    
                    total = vod_data.get('total', 0)
                    current_page = vod_data.get('page', 1)
                    page_limit = vod_data.get('limit', limit)
                    
                    if total > 0 and page_limit > 0:
                        pagecount = (total + page_limit - 1) // page_limit
                    else:
                        pagecount = 9999
                        
                    return videos, current_page, pagecount, total, page_limit
                else:
                    return [], page, 9999, 0, limit
            else:
                return [], page, 9999, 0, limit
                
        except:
            return [], page, 9999, 0, limit

    def fetch_detail(self, vod_id):
        urlz = f'{xurl}/tindex/page_player'
        
        timestamp = int(time.time() * 1000)
        headers['timestamp'] = str(timestamp)
        
        payload = {
            "id": str(vod_id)
        }
        
        try:
            response = requests.post(url=urlz, headers=headers, json=payload, timeout=10)
            
            if 'ENCRYPTION' in response.headers and response.headers['ENCRYPTION'] == '1':
                data = self.decrypt_response(response.text)
            else:
                data = response.json()
            
            if data['code'] == 1 and 'data' in data:
                return data['data']
            else:
                return None
        except:
            return None

    def fix_pic_url(self, url):
        if not url:
            return ""
        if url.startswith('mac://'):
            url = url.replace('mac://', 'https://')
            url = url.replace(':8443', ':443')
        return url

    def fix_video_url(self, url):
        if not url:
            return ""
        if url.startswith('https://'):
            return url
        if '://' not in url:
            url = 'https://' + url
        return url

    def decrypt_response(self, encrypted_text):
        try:
            return json.loads(encrypted_text)
        except:
            try:
                import base64
                decoded = base64.b64decode(encrypted_text).decode('utf-8')
                return json.loads(decoded)
            except:
                return {"msg": "解密失败", "code": 0, "data": {"vods": {"list": []}}}

    def parse_play_url(self, play_url):
        if not play_url:
            return ""
        
        episodes = play_url.split('#')
        parsed_episodes = []
        
        for episode in episodes:
            if '$' in episode:
                name, url = episode.split('$', 1)
                url = self.fix_video_url(url)
                parsed_episodes.append(f"{name}${url}")
        
        return "#".join(parsed_episodes)

    def homeContent(self, filter):
        result = {
            "class": [
                {"type_id": "1", "type_name": "电影"},
                {"type_id": "2", "type_name": "电视剧"},
                {"type_id": "3", "type_name": "短剧"},
                {"type_id": "4", "type_name": "动漫"},
                {"type_id": "28", "type_name": "综艺"}
            ]
        }
        return result

    def homeVideoContent(self):
        payload = {
            "Id": 1,
            "Type": 1,
            "Page": 1,
            "Limit": 24
        }
        
        videos = self.fetch_search(payload)
        result = {'list': videos}
        return result

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        
        if pg:
            page = int(pg)
        else:
            page = 1
        
        limit = 24
        
        payload = {
            "Id": int(cid),
            "Type": 1,
            "Page": page,
            "Limit": limit
        }
        
        videos = self.fetch_search(payload)
        
        result = {
            'list': videos,
            'page': page,
            'pagecount': 9999,
            'limit': limit,
            'total': 999999
        }
        return result

    def detailContent(self, ids):
        result = {}
        videos = []
        
        did = ids[0]
        detail_data = self.fetch_detail(did)
        
        if detail_data:
            vod_id = str(detail_data.get('vod_id', did))
            vod_name = detail_data.get('vod_name', '未知')
            vod_pic = self.fix_pic_url(detail_data.get('vod_pic', ''))
            vod_remarks = detail_data.get('vod_remarks', '')
            vod_year = detail_data.get('vod_year', '')
            vod_area = detail_data.get('vod_area', '')
            vod_director = detail_data.get('vod_director', '')
            vod_actor = detail_data.get('vod_actor', '')
            vod_content = detail_data.get('vod_blurb', detail_data.get('vod_behind', ''))
            
            play_from = ""
            play_url = ""
            
            if 'vod_play_url' in detail_data and detail_data['vod_play_url']:
                play_url = self.parse_play_url(detail_data['vod_play_url'])
                play_from = detail_data.get('vod_play_from', 'ppvod')
            elif 'vod_play_list' in detail_data and detail_data['vod_play_list']:
                for play_item in detail_data['vod_play_list']:
                    if 'url' in play_item and play_item['url']:
                        play_url = self.parse_play_url(play_item['url'])
                        play_from = play_item.get('from', 'ppvod')
                        break
            
            actor = vod_actor.replace(',', ' ') if vod_actor else "未知"
            director = vod_director if vod_director else "未知"
            
            video_info = {
                "vod_id": vod_id,
                "vod_name": vod_name,
                "vod_pic": vod_pic,
                "vod_remarks": vod_remarks,
                "vod_year": vod_year,
                "vod_area": vod_area,
                "vod_director": director,
                "vod_actor": actor,
                "vod_content": vod_content,
                "vod_play_from": play_from,
                "vod_play_url": play_url
            }
            videos.append(video_info)
        
        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        
        if '$' in id:
            parts = id.split('$', 1)
            play_url = parts[1] if len(parts) > 1 else id
        else:
            play_url = id
        
        play_url = self.fix_video_url(play_url)
        
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = play_url
        result["header"] = headerx
        
        return result

    def searchContentPage(self, key, quick, pg):
        result = {}
        
        if pg:
            page = int(pg)
        else:
            page = 1
        
        limit = 24
        
        videos, current_page, pagecount, total, page_limit = self.fetch_search_results(key, page, limit)
        
        result = {
            'list': videos,
            'page': current_page,
            'pagecount': pagecount,
            'limit': page_limit,
            'total': total
        }
        return result

    def searchContent(self, key, quick, pg="1"):
        return self.searchContentPage(key, quick, pg)

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None

    def extract_middle_text(self, text, start_str, end_str, pl, start_index1: str = '', end_index2: str = ''):
        if pl == 3:
            plx = []
            while True:
                start_index = text.find(start_str)
                if start_index == -1:
                    break
                end_index = text.find(end_str, start_index + len(start_str))
                if end_index == -1:
                    break
                middle_text = text[start_index + len(start_str):end_index]
                plx.append(middle_text)
                text = text.replace(start_str + middle_text + end_str, '')
            if len(plx) > 0:
                purl = ''
                for i in range(len(plx)):
                    matches = re.findall(start_index1, plx[i])
                    output = ""
                    for match in matches:
                        match3 = re.search(r'(?:^|[^0-9])(\d+)(?:[^0-9]|$)', match[1])
                        if match3:
                            number = match3.group(1)
                        else:
                            number = 0
                        if 'http' not in match[0]:
                            output += f"#{match[1]}${number}{xurl}{match[0]}"
                        else:
                            output += f"#{match[1]}${number}{match[0]}"
                    output = output[1:]
                    purl = purl + output + "$$$"
                purl = purl[:-3]
                return purl
            else:
                return ""
        else:
            start_index = text.find(start_str)
            if start_index == -1:
                return ""
            end_index = text.find(end_str, start_index + len(start_str))
            if end_index == -1:
                return ""

        if pl == 0:
            middle_text = text[start_index + len(start_str):end_index]
            return middle_text.replace("\\", "")

        if pl == 1:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                jg = ' '.join(matches)
                return jg

        if pl == 2:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                new_list = [f'{item}' for item in matches]
                jg = '$$$'.join(new_list)
                return jg