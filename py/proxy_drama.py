# -*- coding: utf-8 -*-
# 本资源来源于互联网公开渠道，仅可用于个人学习爬虫技术。
# 严禁将其用于任何商业用途，下载后请于 24 小时内删除，搜索结果均来自源站，本人不承担任何责任。

import urllib.parse
from base64 import b64encode
from base.spider import Spider
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
import sys,time,json,random,hashlib,urllib3
from Crypto.Cipher import AES, PKCS1_v1_5
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.path.append('..')

class Spider(Spider):
    def localProxy(self, params):
        if params.get('type') == 'drama':
            response = ''
            try:
                if params.get('from') == 'paramsData':
                    name = params.get('name')
                    if not name: return '请按要求传参'
                    data =  self.params_data(name)
                    response = data
                elif params.get('from') == 'host':
                        url = params.get('url')
                        if url.startswith('http'):
                            res = self.fetch(url,headers={'User-Agent': 'okhttp/3.12.1'}).json()
                            if res['domain'].startswith('http'):
                                response =  res['domain']
                return [200, 'text/text;charset=utf-8', response]
            except Exception:
                return None
        return None

    def params_data(self,name):
        if name or name != 'juzhi':
            vApp = '3018'
            vName = '3.0.1.8'
            appName = '橘汁'
            pkg = 'com.tjjiangh.android'
            publicKey = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCp9Ek4wIlQAtwFnuBRlsFiow2tr+4UOciGeNKbY7nL74etUqUb6fvpOSOHhFEfaWlfwUpOB17x3JEL3No19nfjCeVYrYPjlJcgoqUWH/tfIfFAQWvtxBIBlKazkhw8d3ChysWmeWRikKqkBsVRY4oqNPuj4sjm6Zult0U4I4prRQIDAQAB'
        else:
            return '请按要求传参'
        androidID = '313c3eeeb2a098a1'
        mac = '02:00:00:00:00:00'
        model = '23113RKC6C'
        facturer = 'Xiaomi'
        uuid = hashlib.md5(f"{androidID}{mac}{model}{facturer}".encode()).hexdigest().upper()
        timestamp = self.get_13_digit_timestamp()
        random_str = self.random_str_function()
        aes_key = 'OC1A06E197EF10CF3F6058CA7A803B5E'.encode()
        cipher_aes = AES.new(aes_key, AES.MODE_ECB)
        sign_data = f"{timestamp}{random_str}".encode()
        sign_encrypted = cipher_aes.encrypt(pad(sign_data, AES.block_size))
        sign = b64encode(sign_encrypted).decode()
        deviceInfo = {
            "country": "CN",
            "vName": vName,
            "cpuId": "",
            "young": 0,
            "facturer": facturer,
            "pkg": pkg,
            "uuid": uuid,
            "resolution": "900x1600",
            "mac": urllib.parse.quote(mac),
            "sig": self.rsa_encrypt(f"{timestamp}{random_str}{vApp}", publicKey),
            "abid": "6249",
            "model": model,
            "plat": "android",
            "udid": uuid,
            "dpi": "240",
            "net": "1",
            "lang": "zh",
            "random_str": random_str,
            "brand": "Redmi",
            "timestamp": timestamp,
            "density": "3.25",
            "appName": urllib.parse.quote(appName),
            "cpu": "arm64-v8a",
            "chid": "10000",
            "carrier": urllib.parse.quote('移动'),
            "sig2": sign[:8],
            "sig3": sign[8:],
            "_vOsCode": "32",
            "vOs": "12",
            "vApp": vApp,
            "device": "0",
            "androidID": androidID
        }
        dat = json.dumps(deviceInfo, ensure_ascii=False, separators=(',', ':'))
        aes_key2 = 'ed5fdsgucxumegqa'.encode()
        iv = 'ed5fdsgucxumegqa'.encode()
        cipher_aes2 = AES.new(aes_key2, AES.MODE_CBC, iv)
        dat_encrypted = cipher_aes2.encrypt(pad(dat.encode(), AES.block_size))
        dat_hex = dat_encrypted.hex()
        return dat_hex

    def rsa_encrypt(self,plaintext, public_key_str):
        public_key_pem = f"-----BEGIN PUBLIC KEY-----\n{public_key_str}\n-----END PUBLIC KEY-----"
        rsa_key = RSA.import_key(public_key_pem)
        cipher_rsa = PKCS1_v1_5.new(rsa_key)
        encrypted = cipher_rsa.encrypt(plaintext.encode())
        return b64encode(encrypted).decode()

    def random_str_function(self,length=16):
        char_array = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        result_str = ''
        i = 0
        while i < length - 1:
            c = random.choice(char_array)
            if c not in result_str:
                result_str += c
                i += 1
        return result_str + "="

    def get_13_digit_timestamp(self):
        return int(round(time.time() * 1000))

    def init(self, extend=''):
        pass

    def homeContent(self, filter):
        pass

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        pass

    def searchContent(self, key, quick, pg='1'):
        pass

    def detailContent(self, ids):
        pass

    def playerContent(self, flag, id, vipflags):
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass