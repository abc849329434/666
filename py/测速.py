# coding = utf-8
#!/usr/bin/python
import re, sys, uuid, json, base64, urllib3, random, time, hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base.spider import Spider

sys.path.append('..')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Spider(Spider):
    xurl = ''
    key = ''
    token = ''
    device_id = ''
    header = {}
    available_domains = []
    current_domain_index = 0
    init_data = None  # 你初始化拿到的配置数据

    def __init__(self):
        self.header = {'User-Agent': self._generate_random_ua()}
        self.current_domain_index = 0
        self.available_domains = []

    def init(self, extend=''):
        try:
            ext_json = json.loads(extend)
        except Exception as e:
            print(f"init解析extend失败: {e}")
            return

        ext = ext_json.get('ext', ext_json)

        host = ext.get('host') or ext.get('url') or ''
        datakey = ext.get('datakey') or ext.get('key') or ''
        token = ext.get('token') or ''
        device_id = ext.get('devideid') or ext.get('deviceid') or ''

        if not host or not datakey:
            print("init失败: host或datakey参数缺失")
            return

        self.xurl = host.rstrip('/')
        self.key = datakey
        self.token = token
        self.device_id = device_id

        if self.device_id:
            self.header['app-user-device-id'] = self.device_id
        else:
            self.device_id = str(uuid.uuid4()).replace('-', '')
            self.header['app-user-device-id'] = self.device_id

        if self.token:
            self.header['app-user-token'] = self.token

        self.available_domains = [self.xurl]
        self.current_domain_index = 0

        print(f"初始化完成，host: {self.xurl}, key: {self.key}, token: {self.token}, device_id: {self.device_id}")

        # 示例: 请求初始化接口拿配置数据（可根据你的接口调整）
        try:
            url = f"{self.xurl}/apptov5/v1/config/get?p=android&__platform=android"
            resp = self.fetch(url, headers=self.header, verify=False)
            if resp.status_code == 200:
                data = resp.json()
                self.init_data = data.get('data')
                print("配置初始化成功")
            else:
                print(f"配置初始化接口返回状态码: {resp.status_code}")
        except Exception as e:
            print(f"配置初始化失败: {e}")

    def fetch(self, url, **kwargs):
        # 这里简单用requests实现，或调用父类fetch方法
        import requests
        headers = kwargs.get('headers', {})
        if 'User-Agent' not in headers:
            headers['User-Agent'] = self.header.get('User-Agent', self._generate_random_ua())
        kwargs['headers'] = headers
        return requests.get(url, **kwargs)

    def post(self, url, data=None, **kwargs):
        import requests
        headers = kwargs.get('headers', {})
        if 'User-Agent' not in headers:
            headers['User-Agent'] = self.header.get('User-Agent', self._generate_random_ua())
        kwargs['headers'] = headers
        return requests.post(url, data=data, **kwargs)

    def _generate_random_ua(self):
        android_versions = ["14", "13", "12", "11", "10"]
        devices = ["SM-G9910", "Mi 11", "Redmi K40", "V2148A", "PCT-AL10"]
        android_version = random.choice(android_versions)
        device = random.choice(devices)
        return f"Dalvik/2.1.0 (Linux; U; Android {android_version}; {device} Build/SKQ1.211006.001)"

    def decrypt(self, encrypted_data_b64):
        key_bytes = self.key.encode('utf-8')
        iv_bytes = self.key.encode('utf-8')  # 你原代码iv用key代替了
        encrypted_data = base64.b64decode(encrypted_data_b64)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        decrypted_padded = cipher.decrypt(encrypted_data)
        decrypted = unpad(decrypted_padded, AES.block_size)
        return decrypted.decode('utf-8')

    def encrypt(self, plain_text):
        key_bytes = self.key.encode('utf-8')
        iv_bytes = self.key.encode('utf-8')
        data_bytes = plain_text.encode('utf-8')
        padded_data = pad(data_bytes, AES.block_size)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        encrypted_bytes = cipher.encrypt(padded_data)
        encrypted_data_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')
        return encrypted_data_b64

if __name__ == '__main__':
    spider = Spider()
    init_param = json.dumps({
        "ext": {
            "host": "http://qfys.myqf.asia/getapp.txt",
            "datakey": "vpsj6z4e7scbjbis",
            "token": "a4b9ec2a575629bcc70a8b22b20ec0701747b20e71a9659f8c33fd5a162748f0",
            "devideid": "4b899a2c-d338-4fb6-9ab2-53028081a3ee"
        }
    })
    spider.init(init_param)
