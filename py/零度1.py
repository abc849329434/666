# -*- coding: utf-8 -*-
# by @嗷呜
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
            self.log(f"初始化爬虫，扩展参数: {extend}")
            did = self.getdid()
            self.headers.update({'deviceId': did})
            token = self.gettk()
            self.headers.update({'token': token})
            # 生成并存储AES密钥
            self.getskey()
            self.log(f"初始化完成，deviceId: {did}, token: {token}")
        except Exception as e:
            self.log(f"初始化失败: {str(e)}")
            raise

    def getName(self):
        return "零度影视"

    def isVideoFormat(self, url):
        formats = ['.m3u8', '.mp4', '.avi', '.flv', '.mkv', '.mov']
        return any(url.lower().endswith(fmt) for fmt in formats)

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    host = 'http://ldys.sq1005.top'

    headers = {
        'User-Agent': 'okhttp/4.12.0',
        'client': 'app',
        'deviceType': 'Android',
        'Content-Type': 'application/json; charset=utf-8'
    }

    def homeContent(self, filter):
        try:
            self.log("获取首页分类数据")
            data = self.getdata("/api/v1/app/screen/screenType", {})
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
                    'type_id': k['id']
                })
                filters[k['id']] = [
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
                filters[k['id']].append(sort)
            result['class'] = classes
            result['filters'] = filters
            return result
        except Exception as e:
            self.log(f"homeContent错误: {str(e)}")
            return {'class': [], 'filters': {}}

    def homeVideoContent(self):
        try:
            jdata = {"condition": 64, "pageNum": 1, "pageSize": 40}
            self.log(f"获取首页推荐视频: {jdata}")
            data = self.getdata("/api/v1/app/recommend/recommendSubList", jdata)
            return {'list': self.getlist(data['data']['records'])}
        except Exception as e:
            self.log(f"homeVideoContent错误: {str(e)}")
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            jdata = {
                'condition': {
                    'sreecnTypeEnum': 'NEWEST',
                    'typeId': int(tid),
                },
                'pageNum': int(pg),
                'pageSize': 40,
            }
            
            # 处理扩展参数
            for key, value in extend.items():
                if key in ['classify', 'region', 'year', 'sreecnTypeEnum']:
                    jdata['condition'][key] = value
            
            self.log(f"获取分类内容: tid={tid}, pg={pg}, jdata={jdata}")
            data = self.getdata("/api/v1/app/screen/screenMovie", jdata)
            result = {}
            result['list'] = self.getlist(data['data']['records'])
            result['page'] = pg
            result['pagecount'] = 9999
            result['limit'] = 40
            result['total'] = data['data'].get('total', 999999)
            return result
        except Exception as e:
            self.log(f"categoryContent错误: {str(e)}")
            return {'list': [], 'page': pg, 'pagecount': 0, 'limit': 0, 'total': 0}

    def detailContent(self, ids):
        try:
            if not ids or not ids[0]:
                return {'list': []}
                
            ids = ids[0].split('@@')
            if len(ids) < 2:
                return {'list': []}
            
            video_id = ids[0]
            type_id = ids[-1]
            
            self.log(f"获取视频详情: video_id={video_id}, type_id={type_id}")
            
            # 获取视频描述信息
            jdata = {"id": int(video_id), "typeId": int(type_id)}
            v = self.getdata("/api/v1/app/play/movieDesc", jdata)
            
            if not v or 'data' not in v:
                return {'list': []}
                
            v = v['data']
            
            # 提取播放源信息
            vod = {
                'vod_id': video_id,
                'vod_name': v.get('name', ''),
                'vod_pic': v.get('cover', ''),
                'vod_year': v.get('year', ''),
                'vod_area': v.get('area', ''),
                'vod_actor': v.get('star', ''),
                'vod_director': v.get('director', ''),
                'vod_content': v.get('introduce', ''),
                'vod_remarks': v.get('totalEpisode', ''),
                'vod_play_from': '',
                'vod_play_url': ''
            }
            
            # 获取播放详情
            c = self.getdata("/api/v1/app/play/movieDetails", jdata)
            if not c or 'data' not in c:
                return {'list': [vod]}
            
            l = c['data'].get('moviePlayerList', [])
            if not l:
                return {'list': [vod]}
            
            # 获取所有播放源的剧集
            play_from = []
            play_url = []
            
            for player in l:
                player_id = str(player['id'])
                player_name = player.get('moviePlayerName', f'源{player_id}')
                
                # 获取该播放源的剧集
                player_jdata = jdata.copy()
                player_jdata['playerId'] = player_id
                player_response = self.getdata("/api/v1/app/play/movieDetails", player_jdata)
                
                if player_response and 'data' in player_response:
                    episodes = player_response['data'].get('episodeList', [])
                    if episodes:
                        episode_list = []
                        for ep in episodes:
                            ep_data = player_jdata.copy()
                            ep_data['episodeId'] = str(ep['id'])
                            ep_str = f"{ep.get('episode', '第1集')}${self.e64(json.dumps(ep_data))}"
                            episode_list.append(ep_str)
                        
                        if episode_list:
                            play_from.append(player_name)
                            play_url.append('#'.join(episode_list))
            
            if play_from and play_url:
                vod['vod_play_from'] = '$$$'.join(play_from)
                vod['vod_play_url'] = '$$$'.join(play_url)
            
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
            
            # 获取播放详情
            data = self.getdata("/api/v1/app/play/movieDetails", jdata)
            
            if not data or 'data' not in data:
                return {'parse': 0, 'url': '', 'header': self.headers}
            
            # 获取播放URL
            player_url = data['data'].get('url', '')
            if not player_url:
                return {'parse': 0, 'url': '', 'header': self.headers}
            
            # 尝试解析播放地址
            try:
                params = {
                    'playerUrl': player_url,
                    'playerId': jdata.get('playerId', '')
                }
                
                # 这里使用普通的GET请求，因为analysisMovieUrl可能不需要加密
                response = self.fetch(
                    f"{self.host}/api/v1/app/play/analysisMovieUrl",
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code == 200:
                    pd = response.json()
                    if pd.get('code') == 200 and pd.get('data'):
                        return {
                            'parse': 0,
                            'url': pd['data'],
                            'header': {'User-Agent': 'okhttp/4.12.0', 'Referer': self.host}
                        }
            except Exception as e:
                self.log(f"解析播放地址失败: {str(e)}")
                # 如果解析失败，使用原始URL
                return {
                    'parse': 0,
                    'url': player_url,
                    'header': {'User-Agent': 'okhttp/4.12.0', 'Referer': self.host}
                }
            
            # 返回原始URL
            return {
                'parse': 0,
                'url': player_url,
                'header': {'User-Agent': 'okhttp/4.12.0', 'Referer': self.host}
            }
            
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
        
        # 如果获取失败，尝试从缓存获取
        cached_token = self.getCache('token')
        if cached_token:
            return cached_token
        
        # 生成默认token
        default_token = hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
        self.setCache('token', default_token, 3600)
        return default_token

    def getdid(self):
        did = self.getCache('ldid')
        if not did:
            hex_chars = '0123456789abcdef'
            did = ''.join(random.choice(hex_chars) for _ in range(16))
            self.setCache('ldid', did, 3600*24*30)  # 缓存30天
        return did

    def getskey(self):
        """获取或生成AES密钥"""
        skey = self.getCache('skey')
        if not skey:
            # 生成16位随机密钥
            skey = ''.join(random.choice('0123456789abcdef') for _ in range(16))
            self.setCache('skey', skey, 3600*24)  # 缓存1天
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
            
            # 解码base64
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
nP4q0UTHWEfaGR3HoILmeM32M+qF/UCGfgfR6tCMiXPoHwnD2zoxbZ2p+QlYuTZL
vQIDAQAB
-----END PUBLIC KEY-----"""
            key = RSA.importKey(public_key)
            cipher = PKCS1_v1_5.new(key)
            
            # 加密数据
            encrypted = cipher.encrypt(data.encode())
            
            # 返回base64编码的加密数据
            return b64encode(encrypted).decode()
        except Exception as e:
            self.log(f"RSA加密错误: {str(e)}")
            return ""

    def eaes(self, data, key):
        """AES加密"""
        try:
            # 确保key是16字节
            if len(key) < 16:
                key = key.ljust(16, '0')
            elif len(key) > 16:
                key = key[:16]
            
            key_bytes = key.encode('utf-8')
            cipher = AES.new(key_bytes, AES.MODE_ECB)
            
            # 填充数据
            data_bytes = data.encode('utf-8')
            padded_data = pad(data_bytes, AES.block_size)
            
            # 加密
            encrypted = cipher.encrypt(padded_data)
            
            # 返回base64编码
            return b64encode(encrypted).decode('utf-8')
        except Exception as e:
            self.log(f"AES加密错误: {str(e)}")
            return ""

    def daes(self, encrypted_data, key):
        """AES解密"""
        try:
            # 确保key是16字节
            if len(key) < 16:
                key = key.ljust(16, '0')
            elif len(key) > 16:
                key = key[:16]
            
            key_bytes = key.encode('utf-8')
            cipher = AES.new(key_bytes, AES.MODE_ECB)
            
            # 解码base64
            encrypted_bytes = b64decode(encrypted_data)
            
            # 解密
            decrypted = cipher.decrypt(encrypted_bytes)
            
            # 去除填充
            unpadded = unpad(decrypted, AES.block_size)
            
            return unpadded.decode('utf-8')
        except Exception as e:
            self.log(f"AES解密错误: {str(e)}")
            return ""

    def getdata(self, path, body):
        """加密请求数据"""
        try:
            self.log(f"发送加密请求: {path}, body: {body}")
            
            # 准备请求数据
            jdata = json.dumps(body, ensure_ascii=False, separators=(',', ':'))
            
            # 生成签名
            msign = self.md5(jdata)
            
            # 获取AES密钥
            skey = self.getskey()
            
            # 准备签名数据
            jsign = {'key': skey, 'sign': msign}
            
            # RSA加密签名
            Sign = self.ersa(json.dumps(jsign, ensure_ascii=False, separators=(',', ':')))
            
            # AES加密请求体
            dbody = self.eaes(jdata, skey)
            
            # 设置请求头
            header = self.headers.copy()
            header['Sign'] = Sign
            
            # 发送请求
            response = self.post(
                f'{self.host}{path}',
                headers=header,
                data=dbody
            )
            
            # 处理响应
            rdata = response.text
            
            # 检查响应头中的签名
            if 'Sign' in response.headers:
                # RSA解密响应签名获取AES密钥
                dkey_json = self.drsa(response.headers['Sign'])
                if dkey_json:
                    dkey_data = json.loads(dkey_json)
                    dkey = dkey_data.get('key', '')
                    
                    # AES解密响应数据
                    if dkey:
                        rdata = self.daes(rdata, dkey)
            
            # 解析响应
            result = json.loads(rdata)
            
            if result.get('code') != 200:
                self.log(f"API返回错误: {result.get('msg')}")
            
            return result
            
        except Exception as e:
            self.log(f"加密请求失败: {str(e)}")
            # 返回空数据，避免程序崩溃
            return {'code': 200, 'msg': str(e), 'data': {}}

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