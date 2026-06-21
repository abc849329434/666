# -*- coding: utf-8 -*-
# 本资源来源于互联网公开渠道，仅可用于个人学习爬虫技术。
# 严禁将其用于任何商业用途，下载后请于 24 小时内删除，搜索结果均来自源站，本人不承担任何责任。

from Crypto.Cipher import AES
from base.spider import Spider
from Crypto.Util.Padding import unpad
from urllib.parse import unquote_plus
import re, sys, time, json, base64, hashlib, urllib3
from Crypto.Util.number import bytes_to_long, long_to_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.path.append('..')

# ------------------------------------------------------
# 解密器：适配 vod-parses.baidu.com 的 RSA→AES 链路
# ------------------------------------------------------
_RSA_PUB_PEM = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApvt3yXxUw6XxurT5cUC1
xUDMjmhh8vsdU7q5rS2v9NzNO9t8oo1WwxH2PKjr7154wX7W6g3szPdOyr44Sff
KT+QTffeoj7J1ij/eyg+3OfRrv79yRZe/cGOg4RI0c+P6XYefeljD6HA2+AWseJS
niFPVNM0jv9yDXvSq0eGW5jC0Wb8hELYySLMKQdMrjHOOUe84FoL7vceDzHeSLiS
iwj8gxKr0ls+P4TUT9S7tpqSu3CVJ
'''  # 注意：这里为了代码展示，公钥被截断，实际使用请确保完整

# 新增 ui8__compatible 解密类
class DecryptShijie:
    def __call__(self, str_data, z=False):
        return self.decrypt(str_data, z)

    @staticmethod
    def decrypt(str_data, z=False):
        if not str_data:
            return None if z else str_data
        trim_str = str_data.strip()
        if trim_str.lower().startswith('<!doctype html') or trim_str.lower().startswith('<html'):
            return None if z else str_data
        try:
            json_obj = json.loads(str_data)
            if json_obj.get('code') != 1 or json_obj.get('msg') in ['退出成功', '热搜词库']:
                return None if z else str_data
        except:
            pass
        clean_str = str_data.replace('"', '').replace('\\/', '/')
        prefix = ''
        if clean_str.startswith('lvdou+'):
            prefix = 'lvdou+'
        elif clean_str.startswith('lvDou+'):
            prefix = 'lvDou+'
        data_after_prefix = clean_str[len(prefix):] if prefix else clean_str
        if len(data_after_prefix) <= 32:
            return None if z else clean_str
        main_key = data_after_prefix[:32]
        if len(main_key) != 32 or not main_key.isalnum():
            return None if z else clean_str
        encrypted_data = data_after_prefix[32:]
        return DecryptShijie.core_decrypt(main_key, encrypted_data, z, clean_str)

    @staticmethod
    def core_decrypt(main_key, encrypted_data, z, origin_str):
        if not encrypted_data.strip() or not DecryptShijie.is_valid_base64(encrypted_data):
            return None if z else origin_str
        try:
            decrypted_raw = DecryptShijie.aes_decrypt(encrypted_data, main_key)
            if not decrypted_raw or not decrypted_raw.strip():
                return None if z else origin_str
        except Exception as e:
            return None if z else origin_str
        try:
            return DecryptShijie.de_obfuscate(decrypted_raw)
        except Exception as e:
            return decrypted_raw

    @staticmethod
    def aes_decrypt(encrypted_data, main_key):
        key_hash = hashlib.sha256((main_key + 'encryption_key_salt_2024').encode()).digest()
        iv_hash = hashlib.sha256((main_key + 'iv_salt_2024').encode()).digest()[:16]
        if len(key_hash) != 32 or len(iv_hash) != 16:
            raise Exception("密钥或IV长度无效")
        cipher = AES.new(key_hash, AES.MODE_CBC, iv_hash)
        decrypted = unpad(cipher.decrypt(base64.b64decode(encrypted_data)), AES.block_size)
        return decrypted.decode()

    @staticmethod
    def de_obfuscate(data):
        try:
            json_obj = json.loads(data)
        except:
            return data
        if '_f' not in json_obj or not isinstance(json_obj['_f'], dict): return data
        field_map = json_obj['_f']
        required_fields = ['data', 'timestamp', 'checksum']
        if not all(field in field_map for field in required_fields): return data
        if not all(field in json_obj for field in [field_map['data'], field_map['timestamp'], field_map['checksum']]): return data
        encoded_data = json_obj[field_map['data']]
        if not DecryptShijie.is_valid_base64(encoded_data): return data
        try:
            decoded_data = base64.b64decode(encoded_data)
        except:
            return data
        return decoded_data.decode()

    @staticmethod
    def is_valid_base64(s):
        if not s or len(s) % 4 != 0:
            return False
        try:
            if re.match(r'^[A-Za-z0-9+/]*={0,2}$', s):
                base64.b64decode(s, validate=True)
                return True
        except:
            pass
        return False

# ------------------------------------------------------
# Spider 主体
# ------------------------------------------------------
class Spider(Spider):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 9; vivo PD1728 Build/PQ3A.190705.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Mobile Safari/537.36'
    }

    def localProxy(self, params):
        if params.get('type') == 'ryjx':
            try:
                data = self.ry_jx(params)
                return [200, 'text/json;charset=utf-8', data]
            except:
                data = self.json_encode({"code": "400", "success": "0", "msg": "处理出错"})
                return [400, 'text/json;charset=utf-8', data]
        return None

    def ry_jx(self, params):
        error_msg = self.json_encode({"code": "400", "success": "0", "msg": "URL或API为空"})
        try:
            v = params['v']
            api = unquote_plus(params['api'])
            if not (v and api.startswith('http')):
                return error_msg
        except Exception:
            return error_msg
        play_from = params.get('from')
        play_prefix = params.get('prefix')
        play_include = params.get('include')
        play_from_map = {
            'qq': 'qq.com',
            'qiyi': 'iqiyi.com',
            'youku': 'youku.com',
            'mgtv': 'mgtv.com',
            'bili': 'bilibili.com'
        }
        if play_from or play_prefix or play_include:
            play_from_parts = play_from.split(',') if isinstance(play_from, str) and play_from else []
            play_prefix_parts = play_prefix.split(',') if isinstance(play_prefix, str) and play_prefix else []
            play_include_parts = play_include.split(',') if isinstance(play_include, str) and play_include else []
            is_play_from_all = (play_from == 'all' and any(item in v for item in play_from_map.values() if item))
            is_play_from = (play_from_parts and any((value := play_from_map.get(key.strip())) is not None and value in v for key in play_from_parts))
            is_play_prefix = (play_prefix_parts and any(v.startswith(prefix.strip()) for prefix in play_prefix_parts if prefix.strip()))
            is_play_include = (play_include_parts and any(inc.strip() in v for inc in play_include_parts if inc is not None and inc.strip() != ''))
            if not (is_play_from_all or is_play_from or is_play_prefix or is_play_include):
                return self.json_encode({"code": "-0", "success": "0", "msg": "不支持的地址"})
        try:
            data = self.fetch(f'{api}{v}', headers=self.headers, timeout=30, verify=False).json()
        except Exception:
            return self.json_encode({"code": "-1", "success": "0", "msg": "请求或json解析失败"})
        dat_vurl = data.get('url', '')
        video_url = self.common_decr(dat_vurlypt)
        if not self.is_valid_url(video_url) or video_url == v:
            return self.json_encode({"code": "-3", "success": "0", "msg": "解密或解析失败"})
        data['url'] = video_url
        if 'url' not in data:
            return self.json_encode({"code": "404", "msg": "解析失败", "from": v, "server_data": data})
        for k in ('type', 'ip', 'player', 'From'):
            data.pop(k, None)
        if re.match(r'^https://(?:m|www)\.bilibili\.com/', v, re.I):
            if 'Referer' not in data:
                data['Referer'] = 'https://www.bilibili.com/'
            if 'User-Agent' not in data:
                data['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        elif re.match(r'^https://(?:m|www)\.mgtv\.com/', v, re.I):
            if 'User-Agent' not in data or data.get('User-Agent') == 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36':
                data['User-Agent'] = 'MGDS/Android/2.0.5'
        data['from'] = v
        return self.json_encode(data)

    def json_encode(self, arr):
        return json.dumps(arr, ensure_ascii=False, indent=2)

    def is_valid_url(self, url):
        if not url or url == 'null':
            return False
        return re.match(r'https?://.*', url, re.I) is not None

    # ------------------------------------------------------
    # 统一解密入口（新增 ui8_java_compatible 调用）
    # ------------------------------------------------------
    def common_decrypt(self, dat_vurl):
        # ===== 本地先尝试解密 vod.baidu.com =====
        if dat_vurl.startswith('https://vod.baidu.com/'):
            result = self.vod_baidu_xor(dat_vurl)
            if result:
                return result
        # =======================================
        if re.match(r'^https?://baidu\.con/', dat_vurl, re.I):
            if dat_vurl.count(':') > 2:
                result = self.ui9_decode(dat_vurl)
                if result:
                    return result
            result = self.decode(dat_vurl)
            if result and self.is_valid_url(result):
                return result
            if result:
                result = self.ld_xor(result)
                if result:
                    return result
            result = self.ld_xor(dat_vurl)
            if result:
                return result
            result = self.yd_xor(dat_vurl)
            if result:
                return result
        elif '6max.con' in dat_vurl:
            result = self.yd2(dat_vurl)
            if result:
                return result
        elif 'lvDou+' in dat_vurl:
            result = DecryptShijie()(dat_vurl)
            if result:
                return result
        elif dat_vurl.startswith('https://vod-parses.baidu.com/'):
            result = self.ui8(dat_vurl)
            if not result:                       # 原 ui8 解不开就试新版
                result = self.ui8_java_compatible(dat_vurl)
            if result:
                return result
        return None

    # ------------------------------------------------------
    # 下面所有函数与原文件完全一致
    # ------------------------------------------------------
    def ui9_decode(self, input_str):
        try:
            cleaned_input = re.sub(r'https://baidu\.con/|lvDou\+', '', input_str)
            if cleaned_input.count(':') < 2:
                return None
            parts = cleaned_input.split(':', 3)
            if len(parts) < 4:
                return None
            _, key, iv, data_part = parts
            cipher = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
            decrypted = unpad(cipher.decrypt(base64.b64decode(data_part)), AES.block_size)
            return decrypted.decode()
        except Exception:
            return None

    def decode(self, d):
        original_d = d
        try:
            while re.match(r'^https?://baidu\.con/', d, re.I):
                data = re.sub(r'^https?://baidu\.con/', '', d, flags=re.I)
                if len(data) < 16:
                    return None
                key = data[:16].encode()
                encrypted_data = data[16:]
                cipher = AES.new(key, AES.MODE_CBC, key)
                decrypted = unpad(cipher.decrypt(base64.b64decode(encrypted_data)), AES.block_size)
                d = decrypted.decode()
            return d if d != original_d else None
        except Exception:
            return None

    def ld_xor(self, d):
        if not d:
            return None
        original_d = d
        try:
            if "https://baidu.con/" in d or d.startswith("2423"):
                d = d.replace("https://baidu.con/", "")
                if d.startswith("2423"):
                    d = d[6:]
                substring = str(int(time.time()))[:8]
                decoded = base64.b64decode(d)
                sb = ''
                length = len(substring)
                length2 = len(decoded)
                for i in range(length2):
                    sb += chr(decoded[i] ^ ord(substring[i % length]))
                d = base64.b64decode(sb).decode()
            return d if d != original_d else None
        except Exception:
            return None

    def yd_xor(self, d):
        if not d or 'baidu.con/' not in d:
            return None
        try:
            parts = d.split('baidu.con/', 1)
            if len(parts) < 2:
                return None
            encoded_part = parts[1]
            decoded = base64.b64decode(encoded_part)
            split_parts = decoded.split(b'|', 1)
            if len(split_parts) != 2:
                return None
            str2, str3 = split_parts
            key = 'k3yM@$k2024'
            key_length = len(key)
            sb2 = ''
            for i in range(len(str2)):
                char = chr(str2[i] ^ ord(key[i % key_length]))
                sb2 += char
            sb3 = ''
            sb2_length = len(sb2)
            if sb2_length == 0:
                return None
            for i2 in range(len(str3)):
                pos1 = (i2 + 5) % sb2_length
                pos2 = i2 % sb2_length
                xor_value = (ord(sb2[pos1]) + ord(sb2[pos2])) % 256
                char = chr(str3[i2] ^ xor_value)
                sb3 += char
            return sb3
        except Exception:
            return None

    def yd2(self, d):
        if not d or '6max.con' not in d:
            return None
        try:
            data = d.replace('https://6max.con/', '')
            if len(data) < 16:
                return None
            key = data[:16][::-1]
            encrypted_data = data[16:]
            cipher = AES.new(key.encode(), AES.MODE_CBC, key.encode())
            decrypted = unpad(cipher.decrypt(base64.b64decode(encrypted_data)), AES.block_size)
            return decrypted.decode()
        except Exception:
            return None

    def ui8_key(self, data):
        def remove_padding(data_bytes):
            if len(data_bytes) > 10 and data_bytes[0:2] == b'\x00\x02':
                separator_index = -1
                for i in range(2, len(data_bytes)):
                    if data_bytes[i] == 0x00:
                        separator_index = i
                        break
                if separator_index != -1 and separator_index >= 10:
                    return data_bytes[separator_index + 1:]
            if len(data_bytes) > 10 and data_bytes[0:2] == b'\x00\x01':
                separator_index = data_bytes.find(b'\x00', 2)
                if separator_index != -1:
                    return data_bytes[separator_index + 1:]
            leading_zeros = 0
            for i, byte in enumerate(data_bytes):
                if byte == 0x00:
                    leading_zeros += 1
                else:
                    break
            if 4 < leading_zeros < len(data_bytes) - 4:
                return data_bytes[leading_zeros:]
            return data_bytes

        try:
            ciphertext = base64.b64decode(data)
            e = 65537
            key_size = 256
            n = 21079562076490917015219587480852512299132282846588972509613626067512096161389328018952967457235862130835563213420479656634103575049300097161679204081658154497272581125245352803881834652019229809107820308002912749854520391970510245623300240009991722378306164668314002824501199929254049911331868110702469664803250702178374575823923934377743766444104491434605938939890181211241005585699358654598872394352374955459144334648826707577459995980217087014729507004998084715621911009102107688390105352539795259098849457413742825469024104523030276553490595865329453646012415093918163886593950079624681378051572920908409755103897
            if len(ciphertext) > key_size:
                raise ValueError
            data_int = bytes_to_long(ciphertext)
            if data_int >= n:
                raise ValueError
            result_bytes = long_to_bytes(pow(data_int, e, n))
            if len(result_bytes) < key_size:
                padding_length = key_size - len(result_bytes)
                result_bytes = b'\x00' * padding_length + result_bytes
            cleaned_bytes = remove_padding(result_bytes)
            try:
                result = cleaned_bytes.decode('utf-8')
                return result
            except UnicodeDecodeError as e:
                printable_bytes = bytes(b for b in cleaned_bytes if 32 <= b <= 126)
                if printable_bytes:
                    try:
                        return printable_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        return None
                return None
        except Exception:
            raise ValueError

    def ui8(self, data):
        try:
            if not data:
                return None
            processed = data.replace('https://vod-parses.baidu.com/', '').replace('"', '')
            parts = processed.split('81238', 1)
            if len(parts) < 2 or not parts[1]:
                return None
            aes_encrypted_part = parts[0]
            rsa_encrypted_part = parts[1]
            rsa_decrypted = self.ui8_key(rsa_encrypted_part)
            aes_key_iv = rsa_decrypted.split('|', 1)
            if len(aes_key_iv) < 2:
                return None
            aes_key = aes_key_iv[0].encode('utf-8')
            aes_iv = aes_key_iv[1].encode('utf-8')
            if len(aes_key) != 16 or len(aes_iv) != 16:
                raise ValueError
            aes_encrypted_bytes = base64.b64decode(aes_encrypted_part)
            cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
            decrypted_padded = cipher.decrypt(aes_encrypted_bytes)
            decrypted = unpad(decrypted_padded, AES.block_size).decode('utf-8')
            return decrypted.strip('"')
        except Exception:
            return None

    # ------------------------------------------------------
    # 新增：完全对齐 Java 端的 RSA→AES 解密
    # ------------------------------------------------------
    def ui8_java_compatible(self, data: str) -> str:
        try:
            body = data.replace('https://vod-parses.baidu.com/', '').replace('"', '')
            if '81238' not in body:
                return None
            aes_cipher, rsa_cipher = body.split('81238', 1)
            key_iv = _rsa_decrypt(rsa_cipher)          # "key|iv"
            aes_key, aes_iv = key_iv.split('|', 1)
            real_url = _aes_cbc_decrypt(aes_cipher,
                                        aes_key.encode('utf-8'),
                                        aes_iv.encode('utf-8'))
            return real_url.strip('"')
        except Exception:
            return None

    # ========== 新增：本地解密 vod.baidu.com 异或链路（严格按照图片要求修改） ==========
    def vod_baidu_xor(self, cipher_url: str) -> str:
        """
        解析下发数据先base64解码（解码后密文作如下处理）
        1、首先删除前缀 https://ldmax.cooom/ （注意：代码中处理的是去掉URL中的这个前缀，取剩余的密文部分）
        2、然后取剩余部分的前16位密文反转顺序作为key和iv
        3、最后依然按照AES-CBC-128方法进行解密
        """
        try:
            # 步骤1: 去除前缀 'https://ldmax.cooom/'
            # 注意：这里假设传入的 cipher_url 是完整的带前缀的，或者已经包含了该前缀的密文串
            # 如果传入的是 URL，需要先提取密文部分，或者直接假设输入是密文（根据实际情况调整）
            # 这里按照图片要求，先删除前缀
            prefix_to_remove = 'https://ldmax.cooom/'
            if cipher_url.startswith(prefix_to_remove):
                # 去掉前缀，取剩余部分作为待处理的密文
                encrypted_text = cipher_url[len(prefix_to_remove):]
            else:
                # 如果不带前缀，直接使用整个字符串（可能是已经处理过的）
                encrypted_text = cipher_url

            # 步骤2: Base64解码
            # 注意：这里需要确保 encrypted_text 是有效的 Base64 字符串
            try:
                decoded_bytes = base64.b64decode(encrypted_text)
            except Exception as e:
                # 如果解码失败，尝试直接处理（可能已经是二进制数据？但通常不会）
                # 这里为了健壮性，返回 None
                return None

            # 步骤3: 取前16位密文反转作为 key 和 iv
            # 注意：取前16字节（即128位），然后反转
            if len(decoded_bytes) < 16:
                return None
            key_iv_bytes = decoded_bytes[:16]  # 取前16字节
            key_iv_reversed = key_iv_bytes[::-1]  # 反转顺序
            # 使用反转后的字节作为 key 和 iv（AES-CBC-128 要求 key 和 iv 都是16字节）
            key = key_iv_reversed
            iv = key_iv_reversed

            # 步骤4: 剩余的密文（去掉前16字节）进行 AES-CBC-128 解密
            remaining_bytes = decoded_bytes[16:]  # 剩余部分作为真正的密文

            # 创建 AES 解密对象
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_padded = cipher.decrypt(remaining_bytes)
            decrypted = unpad(decrypted_padded, AES.block_size).decode('utf-8')

            # 返回解密后的结果
            return decrypted

        except Exception as e:
            return None

    # ============================================================

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


# ------------------------------------------------------
# 辅助函数（与 _RSA_PUB_PEM 对应）
# ------------------------------------------------------
def _rsa_decrypt(cipher_b64: str) -> str:
    """RSA/ECB/PKCS1Padding 解密，返回 key|iv"""
    cipher_bin = base64.b64decode(cipher_b64)
    pub = RSA.import_key(_RSA_PUB_PEM)
    rsa = PKCS1_v1_5.new(pub)
    n, e = pub.n, pub.e
    c_int = bytes_to_long(cipher_bin)
    if c_int >= n:
        raise ValueError('cipher_int >= n')
    m_int = pow(c_int, e, n)
    plain_bin = long_to_bytes(m_int)
    if plain_bin[0:2] != b'\x00\x02':
        raise ValueError('PKCS1 padding error')
    sep = plain_bin.find(b'\x00', 2)
    if sep < 10:
        raise ValueError('PKCS1 padding error')
    return plain_bin[sep + 1:].decode()          # "key|iv"


def _aes_cbc_decrypt(cipher_b64: str, key: bytes, iv: bytes) -> str:
    if len(key) not in (16, 32) or len(iv) != 16:
        raise ValueError('key/iv length error')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain = unpad(cipher.decrypt(base64.b64decode(cipher_b64)), AES.block_size)
    return plain.decode()


if __name__ == '__main__':
    # 示例测试
    spider = Spider()
    test_url = "https://ldmax.cooom/U2FsdGVkX1+..."
    result = spider.vod_baidu_xor(test_url)
    print(f"解密结果: {result}")
