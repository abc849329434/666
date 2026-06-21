# coding = utf-8
# !/usr/bin/python
# 熊修改
from base.spider import Spider
import requests
import json
import sys

sys.path.append('..')

HOST = "http://pgcms.lyyytv.cn"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; NOH-AN00 Build/HUAWEINOH-AN00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36'
}
# 解析接口配置 - 可以留空，让外部传入
JX_CONFIG = {
    'jx_url': 'http://8.134.205.252:39466/ceshi/ys.php?key=ugd&url='   #此处填写解析
}

class Spider(Spider):
    def __init__(self):
        self.host = HOST
        self.headers = HEADERS
        self.jx_url = JX_CONFIG['jx_url']
        
    def getName(self):
        return "CMS站点"
    
    def init(self, extend):
        if extend:
            if isinstance(extend, dict):
                if 'playUrl' in extend:
                    play_url = extend['playUrl']
                    if play_url.startswith('json:'):
                        self.jx_url = play_url[5:]
                    else:
                        self.jx_url = play_url
                elif 'jx_url' in extend:
                    self.jx_url = extend['jx_url']
    
    def isVideoFormat(self, url):
        pass
    
    def manualVideoCheck(self):
        pass
    
    def homeContent(self, filter):
        url = f"{self.host}/api.php/app/nav?token"
        response = requests.get(url, headers=self.headers, timeout=10)
        response.encoding = 'utf-8'
        data = response.json()
        
        classes = []
        if 'list' in data:
            for item in data['list']:
                if 'type_name' in item and 'type_id' in item:
                    classes.append({
                        'type_id': str(item['type_id']),
                        'type_name': item['type_name']
                    })
        
        return {"class": classes}
    
    def homeVideoContent(self):
        videos = []
        url = f"{self.host}/api.php/app/index_video?page=1&limit=20"
        response = requests.get(url, headers=self.headers, timeout=10)
        response.encoding = 'utf-8'
        data = response.json()
        
        if 'list' in data:
            for category in data['list']:
                if 'vlist' in category and category['vlist']:
                    for item in category['vlist']:
                        videos.append({
                            "vod_id": str(item.get('vod_id', '')),
                            "vod_name": item.get('vod_name', ''),
                            "vod_pic": item.get('vod_pic', ''),
                            "vod_remarks": item.get('vod_remarks', '')
                        })
        
        return {"list": videos}
    
    def categoryContent(self, tid, pg, filter, ext):
        result = {}
        videos = []
        
        params = {
            "tid": tid,
            "limit": 20,
            "pg": pg
        }
        
        if ext:
            if 'class' in ext and ext['class']:
                params['class'] = ext['class']
            if 'area' in ext and ext['area']:
                params['area'] = ext['area']
            if 'lang' in ext and ext['lang']:
                params['lang'] = ext['lang']
            if 'year' in ext and ext['year']:
                params['year'] = ext['year']
            if 'letter' in ext and ext['letter']:
                params['letter'] = ext['letter']
            if 'by' in ext and ext['by']:
                params['by'] = ext['by']
        
        url = f"{self.host}/api.php/app/video"
        response = requests.get(url, params=params, headers=self.headers, timeout=10)
        response.encoding = 'utf-8'
        data = response.json()
        
        if 'list' in data:
            for item in data['list']:
                videos.append({
                    "vod_id": str(item.get('vod_id', '')),
                    "vod_name": item.get('vod_name', ''),
                    "vod_pic": item.get('vod_pic', ''),
                    "vod_remarks": item.get('vod_remarks', '')
                })
            
            result = {
                'list': videos,
                'page': int(pg),
                'pagecount': data.get('pagecount', 1000),
                'limit': 20,
                'total': data.get('total', len(videos))
            }
        else:
            result = {
                'list': videos,
                'page': int(pg),
                'pagecount': 0,
                'limit': 20,
                'total': 0
            }
        
        return result
    
    def detailContent(self, ids):
        result = {}
        videos = []
        
        vod_id = ids[0]
        url = f"{self.host}/api.php/app/video_detail?id={vod_id}"
        response = requests.get(url, headers=self.headers, timeout=10)
        response.encoding = 'utf-8'
        data = response.json()
        
        video_data = data.get('data', data)
        
        play_from = video_data.get('vod_play_from', '')
        play_url = video_data.get('vod_play_url', '')
        
        vod_info = {
            "vod_id": str(video_data.get('vod_id', vod_id)),
            "vod_name": video_data.get('vod_name', ''),
            "vod_pic": video_data.get('vod_pic', ''),
            "vod_remarks": video_data.get('vod_remarks', ''),
            "vod_actor": video_data.get('vod_actor', ''),
            "vod_director": video_data.get('vod_director', ''),
            "vod_area": video_data.get('vod_area', ''),
            "vod_year": video_data.get('vod_year', ''),
            "vod_content": video_data.get('vod_content', ''),
            "vod_play_from": play_from,
            "vod_play_url": play_url
        }
        
        videos.append(vod_info)
        result = {"list": videos}
        
        return result
    
    def internal_request(self, url, timeout=5):
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            return {
                'code': response.status_code,
                'data': response.text
            }
        except Exception as e:
            return {
                'code': 500,
                'data': ''
            }
    
    def playerContent(self, flag, id, vipFlags):
        try:
            if not id:
                return {
                    'jx': 0,
                    'parse': 0,
                    'url': '',
                    'header': {}
                }
            # 原有解析逻辑保留不变
            if not self.jx_url:                
                old_url = id
            else:
                parser_url = self.jx_url + id
                result = self.internal_request(parser_url, 5)
                if result['code'] == 200 and result['data']:
                    json_data = json.loads(result['data'])
                    if json_data and 'url' in json_data and json_data['url'].strip():
                        old_url = json_data['url'].strip()
                    else:
                        old_url = id
                else:
                    old_url = id

            # ============ 仅此处修改域名替换逻辑，其余全部原样 ============
            # 任意域名全部替换为目标域名，保留后面路径参数
            if "://" in old_url:
                # 分割去掉协议和域名，只取后面路径
                path = old_url.split("/", 3)[-1]
                new_play_url = f"http://wx4kjx.lyyytv.cn/{path}"
            else:
                new_play_url = old_url

            return {
                'jx': 0,
                'parse': 0,
                'url': new_play_url,
                'header': self.headers
            }
                
        except Exception as e:
            return {
                'jx': 1,     
                'parse': 1,  
                'url': id,   
                'header': {}
            }
    
    def searchContentPage(self, key, quick, page):
        result={}
        videos=[]
        if not page:
            page = 1
        url=f'{self.host}/api.php/app/search?text={key}&pg={page}'
        res=requests.get(url=url,headers=self.headers)
        res.encoding = "utf-8"
        res=res.text
        kjson=json.loads(res)
        for i in kjson['list']:
            id= str(i['vod_id'])
            name=i['vod_name']
            pic=i['vod_pic']
            remask=i['vod_remarks']
            video={
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remask
            }
            videos.append(video)

        result['list'] = videos
        result['page'] = page
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
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
