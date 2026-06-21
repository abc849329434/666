# -*- coding: utf-8 -*-
import binascii
import json
import os
import re
import sys
import time
import uuid
import random
from urllib.parse import urlparse, quote
from concurrent.futures import ThreadPoolExecutor
sys.path.append('..')
from base.spider import Spider
from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Util.Padding import unpad, pad
from Crypto.Hash import MD5
import hashlib

class Spider(Spider):

    def init(self, extend=""):
        try:
            self.log("=" * 50)
            self.log("零度影视爬虫初始化开始")
            self.log("=" * 50)
            
            did = self.getdid()
            self.headers.update({'deviceId': did})
            token = self.gettk()
            self.headers.update({'token': token})
            self.getskey()
            
            self.log(f"初始化完成 - deviceId: {did}")
            self.log(f"初始化完成 - token: {token}")
            
        except Exception as e:
            self.log(f"初始化失败: {str(e)}")
            raise

    def getName(self):
        return "零度影视"

    def isVideoFormat(self, url):
        formats = ['.m3u8', '.mp4', '.avi', '.flv', '.mkv', '.mov', 'm3u8', 'mp4']
        return any(fmt in url.lower() for fmt in formats)

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    host = 'http://ldys.sq1005.top'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'client': 'app',
        'deviceType': 'Android',
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }

    def homeContent(self, filter):
        try:
            self.log("获取首页分类数据")
            data = self.fetch(f"{self.host}/api/v1/app/screen/screenType").json()
            
            if data.get('code') != 200:
                self.log(f"获取分类失败: {data.get('msg')}")
                return {'class': [], 'filters': {}}
            
            result = {}
            cate = {
                "类型": "classify",
                "地区": "region",
                "年份": "year"
            }
            sort = {
                'key': 'sreecnTypeEnum',
                'name': '排序',
                'value': [
                    {'n': '人气', 'v': 'POPULARITY'},
                    {'n': '评分', 'v': 'COLLECT'},
                    {'n': '热搜', 'v': 'HOT'},
                    {'n': '最新', 'v': 'NEWEST'}
                ]
            }
            classes = []
            filters = {}
            
            for k in data['data']:
                classes.append({
                    'type_name': k['name'],
                    'type_id': str(k['id'])
                })
                filters[str(k['id'])] = [
                    {
                        'name': v['name'],
                        'key': cate.get(v['name'], v['name'].lower()),
                        'value': [
                            {'n': i['name'], 'v': i['name']}
                            for i in v['children']
                        ]
                    }
                    for v in k['children']
                ]
                filters[str(k['id'])].append(sort)
                
            result['class'] = classes
            result['filters'] = filters
            self.log(f"首页分类加载成功: {len(classes)} 个分类")
            return result
        except Exception as e:
            self.log(f"homeContent错误: {str(e)}")
            return {'class': [], 'filters': {}}

    def homeVideoContent(self):
        try:
            # 使用简单的GET请求获取首页推荐
            self.log("获取首页推荐视频")
            response = self.fetch(f"{self.host}/api/v1/app/recommend/recommendSubList?condition=64&pageNum=1&pageSize=40")
            data = response.json()
            
            if data.get('code') == 200:
                videos = self.getlist(data['data']['records'])
                self.log(f"首页推荐加载成功: {len(videos)} 个视频")
                return {'list': videos}
            else:
                self.log(f"首页推荐API返回错误: {data.get('msg')}")
                return {'list': []}
        except Exception as e:
            self.log(f"homeVideoContent错误: {str(e)}")
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            # 构建查询条件
            condition = {
                'sreecnTypeEnum': 'NEWEST',
                'typeId': int(tid),
            }
            
            # 添加扩展参数
            for key, value in extend.items():
                if key in ['classify', 'region', 'year', 'sreecnTypeEnum']:
                    condition[key] = value
            
            jdata = {
                'condition': condition,
                'pageNum': int(pg),
                'pageSize': 40,
            }
            
            self.log(f"获取分类内容: tid={tid}, pg={pg}")
            data = self.getdata("/api/v1/app/screen/screenMovie", jdata)
            
            if data.get('code') != 200:
                self.log(f"分类内容API返回错误: {data.get('msg')}")
                return {'list': [], 'page': pg, 'pagecount': 0, 'limit': 0, 'total': 0}
            
            result = {}
            result['list'] = self.getlist(data['data']['records'])
            result['page'] = pg
            result['pagecount'] = 9999
            result['limit'] = 40
            result['total'] = data['data'].get('total', 999999)
            
            self.log(f"分类内容加载成功: {len(result['list'])} 个视频")
            return result
        except Exception as e:
            self.log(f"categoryContent错误: {str(e)}")
            return {'list': [], 'page': pg, 'pagecount': 0, 'limit': 0, 'total': 0}

    def detailContent(self, ids):
        try:
            if not ids or not ids[0]:
                return {'list': []}
                
            id_parts = ids[0].split('@@')
            if len(id_parts) < 2:
                return {'list': []}
            
            video_id = id_parts[0]
            type_id = id_parts[1]
            
            self.log(f"获取视频详情: video_id={video_id}, type_id={type_id}")
            
            # 获取视频描述信息
            jdata = {"id": int(video_id), "typeId": int(type_id)}
            v_response = self.getdata("/api/v1/app/play/movieDesc", jdata)
            
            if v_response.get('code') != 200 or 'data' not in v_response:
                self.log("未获取到详情数据")
                return {'list': []}
                
            v = v_response['data']
            
            # 构建基本vod信息
            vod = {
                'vod_id': f"{video_id}@@{type_id}",
                'vod_name': v.get('name', ''),
                'vod_pic': v.get('cover', ''),
                'vod_year': v.get('year', ''),
                'vod_area': v.get('area', ''),
                'vod_actor': v.get('star', '未知'),
                'vod_director': v.get('director', '未知'),
                'vod_content': v.get('introduce', '暂无简介').replace('\n', '').strip(),
                'vod_remarks': v.get('totalEpisode', ''),
                'vod_play_from': '',
                'vod_play_url': ''
            }
            
            # 获取播放详情
            play_response = self.getdata("/api/v1/app/play/movieDetails", jdata)
            if play_response.get('code') != 200 or 'data' not in play_response:
                self.log("未获取到播放详情")
                return {'list': [vod]}
            
            player_list = play_response['data'].get('moviePlayerList', [])
            if not player_list:
                self.log("无播放源数据")
                return {'list': [vod]}
            
            # 处理播放源
            play_from = []
            play_url = []
            
            for player in player_list:
                player_id = str(player['id'])
                player_name = player.get('moviePlayerName', f'播放源{player_id}')
                
                episodes = player.get('episodeList', [])
                if episodes:
                    episode_list = []
                    for ep in episodes:
                        ep_data = {
                            'id': int(video_id),
                            'typeId': int(type_id),
                            'playerId': player_id,
                            'episodeId': str(ep['id'])
                        }
                        ep_name = ep.get('episode', f'第{len(episode_list)+1}集')
                        ep_str = f"{ep_name}${self.e64(json.dumps(ep_data))}"
                        episode_list.append(ep_str)
                    
                    if episode_list:
                        play_from.append(player_name)
                        play_url.append('#'.join(episode_list))
            
            if play_from and play_url:
                vod['vod_play_from'] = '$$$'.join(play_from)
                vod['vod_play_url'] = '$$$'.join(play_url)
                self.log(f"成功加载 {len(play_from)} 个播放源，共 {sum(len(p.split('#')) for p in play_url)} 个剧集")
            else:
                self.log("未生成有效的播放列表")
            
            return {'list': [vod]}
        except Exception as e:
            self.log(f"detailContent错误: {str(e)}")
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        try:
            jdata = {
                "condition": {"value": key},
                "pageNum": int(pg),
                "pageSize": 40
            }
            self.log(f"搜索内容: key={key}, pg={pg}")
            data = self.getdata("/api/v1/app/search/searchMovie", jdata)
            
            if data.get('code') != 200:
                return {'list': [], 'page': pg, 'pagecount': 0, 'limit': 0, 'total': 0}
            
            return {
                'list': self.getlist(data['data']['records']),
                'page': pg,
                'pagecount': 9999,
                'limit': 40,
                'total': data['data'].get('total', 0)
            }
        except Exception as e:
            self.log(f"searchContent错误: {str(e)}")
            return {'list': [], 'page': pg, 'pagecount': 0, 'limit': 0, 'total': 0}

    def playerContent(self, flag, id, vipFlags):
        try:
            self.log(f"获取播放内容: flag={flag}, id={id}")
            
            # 解码播放数据
            jdata = json.loads(self.d64(id))
            self.log(f"播放请求数据: {jdata}")
            
            # 直接获取播放详情
            data = self.getdata("/api/v1/app/play/movieDetails", jdata)
            
            if not data or data.get('code') != 200 or 'data' not in data:
                self.log("未获取到播放数据")
                return {'parse': 0, 'url': '', 'header': self.headers}
            
            # 查找对应的剧集播放信息
            episode_id = jdata.get('episodeId', '')
            player_id = jdata.get('playerId', '')
            
            self.log(f"查找剧集: episode_id={episode_id}, player_id={player_id}")
            
            # 遍历所有播放源找到匹配的
            player_list = data['data'].get('moviePlayerList', [])
            for player in player_list:
                if str(player['id']) == player_id:
                    episodes = player.get('episodeList', [])
                    for ep in episodes:
                        if str(ep.get('id')) == episode_id:
                            play_url = ep.get('url', '')
                            if play_url:
                                self.log(f"找到播放地址: {play_url}")
                                return {
                                    'parse': 0 if self.isVideoFormat(play_url) else 1,
                                    'url': play_url,
                                    'header': {
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                                        'Referer': f"{self.host}/",
                                        'Origin': f"{self.host}"
                                    }
                                }
            
            # 如果上面没找到，尝试备用方案
            play_url = data['data'].get('url', '')
            if play_url:
                self.log(f"使用备用播放地址: {play_url}")
                return {
                    'parse': 0 if self.isVideoFormat(play_url) else 1,
                    'url': play_url,
                    'header': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': f"{self.host}/"
                    }
                }
            
            self.log("未找到有效播放地址")
            return {'parse': 0, 'url': '', 'header': self.headers}
            
        except Exception as e:
            self.log(f"playerContent错误: {str(e)}")
            return {'parse': 0, 'url': '', 'header': self.headers}

    def localProxy(self, param):
        return None

    def liveContent(self, url):
        return []

    # ========== 工具方法 ==========
    
    def gettk(self):
        try:
            # 尝试从缓存获取
            cached_token = self.getCache('token')
            if cached_token:
                return cached_token
                
            # 尝试获取访问者token
            response = self.fetch(
                f"{self.host}/api/v1/app/user/visitorInfo",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    token = data['data'].get('token', '')
                    if token:
                        self.setCache('token', token, 3600)
                        return token
        except Exception as e:
            self.log(f"获取token失败: {str(e)}")
        
        # 生成默认token
        default_token = hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
        self.setCache('token', default_token, 3600)
        return default_token

    def getdid(self):
        did = self.getCache('ldid')
        if not did:
            hex_chars = '0123456789abcdef'
            did = ''.join(random.choice(hex_chars) for _ in range(16))
            self.setCache('ldid', did, 3600*24*30)
        return did

    def getskey(self):
        """获取或生成AES密钥"""
        skey = self.getCache('skey')
        if not skey:
            skey = ''.join(random.choice('0123456789abcdef') for _ in range(16))
            self.setCache('skey', skey, 3600*24)
        return skey

    def getlist(self, data):
        videos = []
        for i in data:
            videos.append({
                'vod_id': f"{i['id']}@@{i.get('typeId', '')}",
                'vod_name': i.get('name', ''),
                'vod_pic': i.get('cover', ''),
                'vod_year': i.get('year', ''),
                'vod_remarks': i.get('totalEpisode', ''),
                'vod_score': i.get('score', ''),
                'vod_tag': i.get('classify', ''),
                'vod_area': i.get('area', '')
            })
        return videos

    # ========== 加密解密方法 ==========
    
    def getdata(self, path, body):
        """发送请求数据，支持明文和加密两种方式"""
        try:
            self.log(f"发送请求: {path}")
            
            # 先尝试明文请求
            try:
                header = self.headers.copy()
                response = self.fetch(
                    f"{self.host}{path}",
                    headers=header,
                    data=json.dumps(body, ensure_ascii=False, separators=(',', ':')),
                    method='POST'
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'code' in data:
                        return data
            except:
                pass
            
            # 如果明文失败，尝试加密请求
            jdata = json.dumps(body, ensure_ascii=False, separators=(',', ':'))
            msign = self.md5(jdata)
            skey = self.getskey()
            
            jsign = {'key': skey, 'sign': msign}
            Sign = self.ersa(json.dumps(jsign, ensure_ascii=False, separators=(',', ':')))
            dbody = self.eaes(jdata, skey)
            
            header = self.headers.copy()
            header['Sign'] = Sign
            
            response = self.fetch(
                f"{self.host}{path}",
                headers=header,
                data=dbody,
                method='POST'
            )
            
            rdata = response.text
            
            # 尝试解密响应
            if 'Sign' in response.headers and response.headers['Sign']:
                try:
                    dkey_json = self.drsa(response.headers['Sign'])
                    if dkey_json:
                        dkey_data = json.loads(dkey_json)
                        dkey = dkey_data.get('key', '')
                        if dkey:
                            rdata = self.daes(rdata, dkey)
                except:
                    pass
            
            return json.loads(rdata)
            
        except Exception as e:
            self.log(f"请求失败: {str(e)}")
            return {'code': 500, 'msg': str(e), 'data': {}}

    def drsa(self, encrypted_data):
        """RSA解密"""
        try:
            private_key_pem = """-----BEGIN RSA PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDA5NWiAwRjH50/
IJY1N0zLopa4jpuWE7kWMn1Qunu6SjBgTvNRmRUoPDHn54haLfbfXIa2X+/sIaMB
/O3HhrpVsz55E5W2vpZ5fBYWh+M65bQERKTW+l72H7GR9x0yj3QPByzzfsj/QkyP
81prpwR9i8yMe7yG9TFKqUQCPE+/GrhNU1Qf6nFmV+vMnlP9DantkwAt4fPOMZn3
j4da65/1YQV+F5bYzaLenNVKbHf8U8fVYLZWIy4yk2Vpe4R2Z+JX/eHWsChE9hOu
iFm02eTW5NJLZlWUxYrSE23VXi8oXSEdON3UEOrwSdAUh4SXxLZ9U7KpNVdTwWyR
AS4GyzJ/AgMBAAECggEBAKzmcXefLLeNBu4mz30z7Go7es5DRcLoOudiqmFKRs1c
4q/xFLj3drdx/WnZZ6ctvDPKRBYFOJF4NRz7Ekfew/c9i6oLnA8KFuceCs53T37j
ltCclwT7t1L2ZbxovIsteuJdlDVOV+w2CVqez1Xfh27heKAT6ZEvBtfdkVBPr0uj
oVwa2+XlJmYZw5dHeB7ySVeAQ+69zDuADB8OWxPWsv6Del+Fhf0kTHAw4WgqcYsd
JUunCjgLdJUlDgXzH/M/Nj8NYVEuq6QpmhaktJ4fwn/F7u3lQllVCFKj5lr0Xb92
y7lvQlGqMKX1oxf+P5c5/vie1kDx1Rj4S++flIcVlUECgYEA4BuxCZ1c8oOF98bs
KTAONnnZniQ1BRt7rA+O9+++lDjxJhxkuthwjB9YzrnZtxHJtvIIie9Jv8MVfzHa
p2woDtiEh3YYwmIlgNUFvTcGe++tTiEiLDcGc/xNhpvfbLaw9QB7/HQ+LT1QCMxJ
ufdBrR98l0khIGjYqxDW3W5pV70CgYEA3Ff/9+GM2XI/EUSTYrpnwp5R5OsXz1DL
3CFFgp1EPCNk/c3YNWnrUtTkfmKAlRqWIHfphvH/jS6jpGrfRxDggPwGMtBc134b
brIM5i4KNj/EcE+w5g03HaKBf1ZihHDQ53c6wTn6IFOHJNSPRLqMNqRymfbclNyO
lBMHQmB8yOsCgYBCdZPTwRnuRTi2WQRx1nFwkEQL1Lrwb80GInsIZc2DkTtaTPNG
QadmtmkUrSK2Wo0SNsZ3eUHKn2TBmpw4KCfc9zKeJVSEWKy8fu+7xBSlLlebotHK
gOrl/H1VHOZuC+OAVItwO1yw98zDPynh/0Q3ve2pw6MSRGV0nYLKmdKdlQKBgQCJ
Ty1rw1qKhu9WS22tMIxIc3CFPxtvTeI8I1+1rVtAPq5Im2YIoyDKVXCucaO/RvoW
8aLNPTELQe0oIJFTL+k3d9ZFBCNXBncB3GK9biNe+w3nD0IlmkamaQZZ2/M4pTUJ
iPtMPlzomCS3ht5g7f9CbegcmgGLooYXMGRtsMMSUQKBgQCoj+3UciH2i+HyUla5
1FxivjH3MqSTE4Q7OdzrELb6DoLYzjgWAbpG8HIuodD4uG5xz1oR5H7vkblf1itB
hwOwDEiabyX76e/I3Q0ovwBV+9PMjM4UVU0kHoiu3Z2s90ckwNh58w3QH5fn9E0b
fqMnB6uWze+xrXWijaOzVZhIZg==
-----END RSA PRIVATE KEY-----"""
            private_key = RSA.import_key(private_key_pem)
            cipher = PKCS1_v1_5.new(private_key)
            encrypted_bytes = b64decode(encrypted_data)
            decrypted_data = cipher.decrypt(encrypted_bytes, None)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            self.log(f"RSA解密错误: {str(e)}")
            return ""

    def ersa(self, data):
        """RSA加密"""
        try:
            public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA+0QMb3WDXjNBRovRhTLH
g3d+CliZAva2tepWNNN0Pj6DgE3ZTnPR34iL/cjo9Jbd3dqAJs/YkKnFurGkDxz5
TthIqvmz244wiFcHt+FGWoJsj5ZVvrH3pPwH85ggmI1DjxSJEUhB12Z9X6FGli8D
drR9xeLe5y8vFekux8xCQ7pwH1mNQu4Wy32WVM8aLjmRjNzEWOvEMAWCRuwymEdS
zlWoH53qk1dqd6DAmOJhWU2hH6Yt2ZY9LTaDGiHrS+g0DuwajAQzhbM8eonGYMph
n4q0UTHWEfaGR3HoILmeM32M+qF/UCGfgfR6tCMiXPoHwnD2zoxbZ2p+QlYuTZL
vQIDAQAB
-----END PUBLIC KEY-----"""
            key = RSA.importKey(public_key)
            cipher = PKCS1_v1_5.new(key)
            encrypted = cipher.encrypt(data.encode())
            return b64encode(encrypted).decode()
        except Exception as e:
            self.log(f"RSA加密错误: {str(e)}")
            return ""

    def eaes(self, data, key):
        """AES加密"""
        try:
            if len(key) < 16:
                key = key.ljust(16, '0')
            elif len(key) > 16:
                key = key[:16]
            key_bytes = key.encode('utf-8')
            cipher = AES.new(key_bytes, AES.MODE_ECB)
            data_bytes = data.encode('utf-8')
            padded_data = pad(data_bytes, AES.block_size)
            encrypted = cipher.encrypt(padded_data)
            return b64encode(encrypted).decode('utf-8')
        except Exception as e:
            self.log(f"AES加密错误: {str(e)}")
            return ""

    def daes(self, encrypted_data, key):
        """AES解密"""
        try:
            if len(key) < 16:
                key = key.ljust(16, '0')
            elif len(key) > 16:
                key = key[:16]
            key_bytes = key.encode('utf-8')
            cipher = AES.new(key_bytes, AES.MODE_ECB)
            encrypted_bytes = b64decode(encrypted_data)
            decrypted = cipher.decrypt(encrypted_bytes)
            unpadded = unpad(decrypted, AES.block_size)
            return unpadded.decode('utf-8')
        except Exception as e:
            self.log(f"AES解密错误: {str(e)}")
            return ""

    def e64(self, text):
        """Base64编码"""
        try:
            text_bytes = text.encode('utf-8')
            encoded_bytes = b64encode(text_bytes)
            return encoded_bytes.decode('utf-8')
        except Exception as e:
            self.log(f"Base64编码错误: {str(e)}")
            return ""

    def d64(self, encoded_text):
        """Base64解码"""
        try:
            encoded_bytes = encoded_text.encode('utf-8')
            decoded_bytes = b64decode(encoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            self.log(f"Base64解码错误: {str(e)}")
            return ""

    def md5(self, text):
        """MD5加密"""
        try:
            return hashlib.md5(text.encode('utf-8')).hexdigest()
        except Exception as e:
            self.log(f"MD5加密错误: {str(e)}")
            return ""

    def log(self, message):
        """日志输出"""
        print(f"[零度影视] {message}")

    def fetch(self, url, headers=None, data=None, method='GET', timeout=10):
        """统一的请求方法"""
        try:
            if headers is None:
                headers = self.headers
            
            if method.upper() == 'GET':
                return self.fetch_get(url, headers=headers, timeout=timeout)
            else:
                return self.fetch_post(url, headers=headers, data=data, timeout=timeout)
        except Exception as e:
            self.log(f"fetch请求失败: {str(e)}")
            # 返回一个空的响应对象
            class EmptyResponse:
                def __init__(self):
                    self.status_code = 500
                    self.text = '{}'
                def json(self):
                    return {'code': 500, 'msg': '请求失败'}
            return EmptyResponse()

    def fetch_get(self, url, headers=None, timeout=10):
        """GET请求"""
        import requests
        if headers is None:
            headers = self.headers
        response = requests.get(url, headers=headers, timeout=timeout)
        return response

    def fetch_post(self, url, headers=None, data=None, timeout=10):
        """POST请求"""
        import requests
        if headers is None:
            headers = self.headers
        response = requests.post(url, headers=headers, data=data, timeout=timeout)
        return response
