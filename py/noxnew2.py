# -*- coding: utf-8 -*-
# by @嗷呜 (重构修复版)
import base64
import json
import os
import random
import re
import secrets
import string
import sys
import time
from datetime import datetime
from urllib.parse import quote

# 自动处理某些环境下 PyCryptodome 库的大写 Crypto 问题
try:
    from Crypto.Cipher import AES, PKCS1_OAEP
    from Crypto.Hash import SHA256, HMAC, MD5
    from Crypto.PublicKey import RSA
except ModuleNotFoundError:
    import crypto
    sys.modules['Crypto'] = crypto
    from Crypto.Cipher import AES, PKCS1_OAEP
    from Crypto.Hash import SHA256, HMAC, MD5
    from Crypto.PublicKey import RSA

sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    def init(self, extend='{}'):
        xxx = json.loads(extend)
        self.host = xxx['host']
        self.rsa_key = xxx['rsa_key']
        # 读取可选配置：用户名、密码、设备ID
        self.cfg_username = xxx.get('username', '')
        self.cfg_password = xxx.get('password', '')
        self.cfg_did = xxx.get('did', '')
        
        # 线路排序配置，兼容外部传入的 sort 字段
        sort_str = xxx.get('sort', '')
        if sort_str:
            self.sort_order = [s.strip() for s in sort_str.split('>') if s.strip()]
        else:
            self.sort_order = []

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) NOX/1.0 Mobile/15E148 Safari/604.1',
            "x-app-package": xxx['package'],
            "x-app-signature": xxx["signature"],
            "x-app-version-code": xxx['code'],
            "x-app-version-name": xxx['version']
        }
        self.code = self.headers['x-app-version-code']
        self.version = self.headers['x-app-version-name']
        self.sign = self.headers['x-app-signature']
        self.packge = self.headers['x-app-package']
        self.auth, self.aes_key, self.hmac_key, self.user_id, self.refresh_token, self.did = '', '', '', '', '', ''
        self.key_expires, self.token_expires, self.vip_expires, self.isZc = 0, 0, 0, False
        
        # 1. 初始化用户设备信息
        self.user = self.getUser()
        # 2. 握手交换安全密钥
        self.getKey()
        # 3. 登录或注册
        self.login()

    def destroy(self):
        pass

    def RandK(self, length=32):
        random_key = os.urandom(32)
        return base64.b64encode(random_key).decode()

    def getKey(self):
        rsa_key = self.RandK()
        res_key = self.RandK()
        data = {"temp_key": res_key, "device_id": self.did}
        prt2 = self.aes_gcm_encrypt((json.dumps(data)), rsa_key)
        part1 = self.rsa_en(rsa_key)
        body = {'data': part1 + '|' + prt2}
        resp = self.post(f'{self.host}/api/sync/preferences', headers=self.headers, json=body).json()
        data = self.aes_gcm_decrypt(resp['data'], res_key)
        self.key_expires = data['expires_at']
        self.aes_key = data['aes_key']
        self.hmac_key = data['hmac_key']

    def rsa_en(self, key):
        public_key_pem = base64.b64decode(self.rsa_key).decode()
        recipient_key = RSA.import_key(public_key_pem)
        cipher_rsa = PKCS1_OAEP.new(recipient_key, hashAlgo=SHA256)
        ciphertext = cipher_rsa.encrypt(base64.b64decode(key))
        return base64.b64encode(ciphertext).decode()

    def aes_gcm_decrypt(self, b64_cipher, key):
        try:
            full_data = base64.b64decode(b64_cipher)
            iv = full_data[:12]
            ciphertext = full_data[12:-16]
            tag = full_data[-16:]
            key = base64.b64decode(key)
            cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            return json.loads(plaintext.decode('utf-8'))
        except Exception as e:
            print(f"解密失败: {str(e)}")
            return {}

    def aes_gcm_encrypt(self, plaintext_str, key):
        try:
            key = base64.b64decode(key)
            iv = os.urandom(12)
            cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
            ciphertext, tag = cipher.encrypt_and_digest(plaintext_str.encode('utf-8'))
            full_data = iv + ciphertext + tag
            return base64.b64encode(full_data).decode('utf-8')
        except Exception as e:
            return f"加密失败: {str(e)}"

    def getVlist(self, data):
        v = []
        for i in data:
            v.append({
                'vod_id': i.get('vod_id'),
                'vod_name': i.get('vod_name'),
                'vod_pic': i.get('image_url'),
                'vod_remarks': i.get('vod_remarks')
            })
        return v

    def getH(self, body):
        t = str(int(time.time() * 1000))
        xt = self.RandK(16)
        h = HMAC.new(base64.b64decode(self.hmac_key), msg=(body + t + xt).encode(), digestmod=SHA256)
        headers = {
            'User-Agent': self.headers['User-Agent'],
            'Content-Type': 'application/json',
            'x-req-ts': t,
            'x-req-id': self.did,
            'x-req-trace': xt,
            'x-req-token': h.hexdigest(),
        }
        return headers

    def getbody(self, path, method="GET", body=""):
        if isinstance(body, dict):
            body = json.dumps(body)
        body = {
            "method": method,
            "path": path,
            "query": "",
            "headers": {
                "X-App-Package": self.packge,
                "X-App-Signature": self.sign,
                "X-App-Version-Code": self.code,
                "X-App-Version-Name": self.version,
                "Content-Type": "application/json"
            },
            "body": body
        }
        if self.auth:
            body['headers']['Authorization'] = "Bearer " + self.auth
        data = self.aes_gcm_encrypt(json.dumps(body), self.aes_key)
        return data

    def Reref(self):
        try:
            if self.key_expires == 0 or self.token_expires == 0:
                return
            now = int(time.time())
            key_delay = self.key_expires - now - 10
            if key_delay < 0:
                self.getKey()
            token_delay = self.token_expires - now - 10
            if token_delay < 0:
                self.refreshToken()
            if now > self.vip_expires:
                self.GetVip()
        except Exception as e:
            print(e)

    def getdata(self, path, method="GET", body=""):
        self.Reref()
        return self._base_push(path, method, body)

    def _base_push(self, path, method="GET", body=""):
        a = self.getbody(path, method, body)
        resp = self.post(f"{self.host}/api/sync/push", headers=self.getH(a), json={'bundle': a}).json()
        d = self.aes_gcm_decrypt(resp['bundle'], self.aes_key)
        return d

    def getUser(self):
        hi = MD5.new(f"{self.packge}_{self.code}".encode()).hexdigest()
        if self.cfg_username and self.cfg_password and self.cfg_did:
            user = {'u': self.cfg_username, 'p': self.cfg_password, 'd': self.cfg_did}
            self.setCache(hi, json.dumps(user))
            self.did = self.cfg_did
            self.headers['x-device-id'] = self.did
            return user
            
        data = self.getCache(hi)
        if not data:
            u, p, d = self.generate_user()
            self.did, self.isZc = d, True
            self.headers['x-device-id'] = self.did
            user = {'u': u, 'p': p, 'd': d}
            self.setCache(hi, json.dumps(user))
            return user
        user = json.loads(data)
        self.did = user['d']
        self.headers['x-device-id'] = self.did
        return user

    def login(self):
        # 【核心修复点】原版在新用户注册成功后不走登录流程导致没有 token，现改为统一登录
        if self.isZc:
            self.get_yzm()
            
        body = {'name': self.user['u'], 'password': self.user['p']}
        res = self._base_push('/api/auth/login', "POST", body)
        
        if 'data' not in res or not res['data']:
            print("登录失败，未能成功提取 Token 信息。可能是验证码接口过期或账号被风控。")
            return
            
        resp = res['data']
        self.auth = resp['access_token']
        self.refresh_token = resp['refresh_token']
        
        payload_b64 = self.auth.split('.')[1]
        missing_padding = len(payload_b64) % 4
        if missing_padding:
            payload_b64 += '=' * (4 - missing_padding)
        payload_json = base64.b64decode(payload_b64).decode('utf-8')
        payload_data = json.loads(payload_json)
        self.token_expires = payload_data['exp']
        xxx = resp['user']
        self.user_id = str(xxx['id'])
        time_str = xxx.get('vip_expires_at')
        if time_str:
            try:
                dt_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                self.vip_expires = int(dt_obj.timestamp())
            except Exception:
                self.GetVip()
        else:
            self.GetVip()

    def refreshToken(self):
        try:
            resp = self._base_push("/api/auth/refresh", "POST", {"refresh_token": self.refresh_token}).get('data')
            if not resp:
                return
            self.auth, self.refresh_token = resp['access_token'], resp['refresh_token']
        except Exception as e:
            print(e)

    def GetVip(self):
        try:
            self._base_push("/api/vv/callback", "POST", {'user_id': self.user_id})
            resp = self._base_push("/api/vip/status")
            aaa = resp.get('data', {}) or {}
            time_val = aaa.get('expires_at')
            if time_val:
                dt_obj = datetime.strptime(time_val, "%Y-%m-%d %H:%M:%S")
                self.vip_expires = int(dt_obj.timestamp())
        except Exception as e:
            print(e)

    def homeContent(self, filter):
        resp = self.getdata("/api/categories")
        classes, filters, result = [], {}, {}
        if 'data' not in resp:
            return result
        for k in resp['data']:
            tid = k['type_id']
            classes.append({
                'type_name': k['type_name'],
                'type_id': tid
            })
            current_filters = []
            if 'filters' not in k:
                continue
            for n, v in k['filters'].items():
                if len(v) < 2:
                    continue
                current_filters.append({
                    "key": n,
                    "name": n,
                    "value": [{"n": val, "v": val} for val in v]
                })
            filters[tid] = current_filters
        result['class'] = classes
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        resp = self.getdata("/api/navigations/1")
        v = []
        if 'data' not in resp or 'banners' not in resp['data']:
            return {'list': v}
        for i in resp['data']['banners']:
            v.append({
                'vod_id': i.get('id'),
                'vod_name': i.get('name'),
                'vod_pic': i.get('banner_url'),
                'vod_remarks': i.get('tags')
            })
        return {'list': v}

    def categoryContent(self, tid, pg, filter, extend):
        path = f'/api/category?type={tid}&page={pg}&limit=20'
        for n, v in extend.items():
            path += f"&{n}={v}"
        resp = self.getdata(path)
        result = {}
        if 'data' not in resp or 'list' not in resp['data']:
            return {'list': [], 'page': pg}
        result['list'] = self.getVlist(resp['data']['list'])
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 20
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        resp = self.getdata(f"/api/videos/{ids[0]}")
        if 'data' not in resp:
            return {'list': []}
        v = resp['data']
        play_sources = v.get('play_sources', [])
        if self.sort_order:
            def sort_key(source):
                code = str(source.get('source_code', ''))
                try:
                    return self.sort_order.index(code)
                except ValueError:
                    return len(self.sort_order)
            play_sources = sorted(play_sources, key=sort_key)

        n, p = [], []
        for i in play_sources:
            source_code = i.get('source_code', '')
            n.append(i['source_name'])
            npc = [f"{j['name']}${j['url']}@@@{source_code}" for j in i['episodes']]
            p.append("#".join(npc))
        vod = {
            'type_name': v.get('vod_class'),
            'vod_year': v.get('vod_year'),
            'vod_area': v.get('vod_area'),
            'vod_remarks': v.get('vod_remarks'),
            'vod_actor': v.get('vod_actor'),
            'vod_director': "",
            'vod_content': v.get('vod_blurb'),
            'vod_play_from': '$$$'.join(n),
            'vod_play_url': '$$$'.join(p)
        }
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        resp = self.getdata(f"/api/search?keyword={quote(key)}&page={pg}&limit=20")
        if 'data' not in resp or 'list' not in resp['data']:
            return {'list': [], 'page': pg}
        return {'list': self.getVlist(resp['data']['list']), 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        ids = id.split('@@@')
        video_pattern = r'^http?://[^\s]+(?:\.mp4|\.m3u8|\.flv|\.mov|\.avi|\.mkv|\.wmv)(?:\?.*)?$'
        if re.match(video_pattern, ids[0], re.IGNORECASE):
            url, hhh = ids[0], ''
        else:
            resp = self.getdata("/api/videos/parse-url", "POST", {'url': ids[0], 'source_code': ids[1]})
            rrr = resp.get('data', {})
            url, hhh = rrr.get('parsed_url', id), rrr.get("headers", "") or ''
        return {'parse': 0, 'url': url, 'header': hhh}

    def generate_user(self):
        username_chars = string.ascii_lowercase + string.digits
        password_chars = string.ascii_letters + string.digits
        u_len = secrets.randbelow(5) + 6
        p_len = secrets.randbelow(5) + 6
        username = secrets.choice(string.ascii_lowercase)
        username += ''.join(secrets.choice(username_chars) for _ in range(u_len - 1))
        password = ''.join(secrets.choice(password_chars) for _ in range(p_len))
        return username, password, secrets.token_hex(8)

    def generate_track(self, target_x):
        total_steps = random.randint(40, 60)
        forward_steps = int(total_steps * 0.9)
        back_steps = total_steps - forward_steps
        track = []
        current_t = int(time.time() * 1000)
        overshoot_x = target_x + random.uniform(2.5, 5.0)
        for i in range(forward_steps):
            progress = i / (forward_steps - 1)
            ease_progress = 1 - (1 - progress) ** 2
            point_x = overshoot_x * ease_progress
            jitter = random.uniform(-0.1, 0.1)
            track.append({
                "x": float(f"{max(0, point_x + jitter):.15f}"),
                "t": current_t
            })
            current_t += random.randint(10, 25)
        current_t += random.randint(30, 80)
        for i in range(1, back_steps + 1):
            back_progress = i / back_steps
            current_x = overshoot_x - (overshoot_x - target_x) * back_progress
            jitter = random.uniform(-0.05, 0.05)
            final_x = target_x if i == back_steps else current_x + jitter
            track.append({
                "x": float(f"{final_x:.15f}"),
                "t": current_t
            })
            current_t += random.randint(20, 40)
        return track

    def get_yzm(self, i=1):
        try:
            resp = self.getdata("/api/captcha/rotate")
            rrr = resp['data']
            # 使用原作者搭建的第三方旋转验证码识别服务
            anglep = self.post("https://ocr.tvshare.cn/rotate", headers={'Authorization': 'Bearer zyshidashabi'},
                               json={'bg': rrr['master_image'], 'thumb': rrr['thumb_image']}).json()
            angle = int(anglep['data']['angle']['cw'])
            body = {
                "name": self.user['u'],
                "password": self.user['p'],
                "password_confirmation": self.user['p'],
                "captcha_id": rrr['id'],
                "captcha_angle": angle,
                "captcha_track": self.generate_track(angle)
            }
            reg = self._base_push("/api/auth/register", 'POST', body)
            if i > 3 or reg.get('code') == 429:
                raise Exception
            if reg.get("code") != 0:
                return self.get_yzm(i + 1)
            return reg
        except Exception:
            hi = MD5.new(f"{self.packge}_{self.code}".encode()).hexdigest()
            self.delCache(hi)
            return {}
