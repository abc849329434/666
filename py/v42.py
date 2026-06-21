# -*- coding: utf-8 -*-
import sys
import uuid
import json
import base64

from base.spider import Spider
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

sys.path.append('..')


class Spider(Spider):

    def __init__(self):
        self.local_uuid = ''
        self.config = {}
        self.parsing_config = {}

        self.host = ''
        self.token = ''

        self.aes_key = None
        self.aes_iv = None
        self.use_encrypt = False

        self.line_order = []
        self.block_keywords = []

        self.headers = {
            'User-Agent': 'Dart/2.19 (dart:io)',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/x-www-form-urlencoded',
            'appto-local-uuid': '',
            'token': ''
        }

    def aes_decrypt(self, encrypted_data):
        if not (self.use_encrypt and self.aes_key and self.aes_iv):
            return None

        try:
            if isinstance(encrypted_data, str):
                encrypted_data = base64.b64decode(encrypted_data)

            cipher = AES.new(
                self.aes_key,
                AES.MODE_CBC,
                self.aes_iv
            )

            decrypted = unpad(
                cipher.decrypt(encrypted_data),
                AES.block_size
            )

            return decrypted.decode('utf-8')

        except:
            return None

    def fetch_with_decrypt(
            self,
            url,
            params=None,
            headers=None,
            method='GET'
    ):

        try:
            if method.upper() == 'GET':
                response = self.fetch(
                    url,
                    params=params,
                    headers=headers or self.headers
                )
            else:
                response = self.post(
                    url,
                    data=params,
                    headers=headers or self.headers
                )

            raw_text = response.text.strip()

            if not raw_text:
                return {}

            # 非加密
            if not self.use_encrypt:
                try:
                    return json.loads(raw_text)
                except:
                    return {'code': -1, 'msg': raw_text}

            # json解析
            try:
                json_data = json.loads(raw_text)

                # data加密
                if isinstance(json_data, dict):

                    if (
                            'data' in json_data and
                            isinstance(json_data['data'], str)
                    ):

                        decrypted = self.aes_decrypt(
                            json_data['data']
                        )

                        if decrypted:
                            try:
                                json_data['data'] = json.loads(decrypted)
                            except:
                                json_data['data'] = decrypted

                    return json_data

                # 整体字符串加密
                elif isinstance(json_data, str):

                    decrypted = self.aes_decrypt(json_data)

                    if decrypted:
                        return json.loads(decrypted)

            except:

                decrypted = self.aes_decrypt(raw_text)

                if decrypted:
                    return json.loads(decrypted)

            return {'code': -1, 'msg': '解密失败'}

        except Exception as e:
            return {
                'code': -1,
                'msg': str(e)
            }

    def parse_config_str(self, config_str):

        if not config_str:
            return [], []

        config_str = config_str.strip()

        order_part, block_part = (
            config_str.split('@', 1) + ['']
        )[:2]

        line_order = []
        block_keywords = []

        if order_part:
            line_order = [
                i.strip().lower()
                for i in order_part.split(',')
                if i.strip()
            ]

        if block_part:
            block_keywords = [
                i.strip().lower()
                for i in block_part.split(',')
                if i.strip()
            ]

        return (
            list(dict.fromkeys(line_order)),
            list(dict.fromkeys(block_keywords))
        )

    def init(self, extend=""):

        try:

            # ===== 默认内置配置 =====
            default_ext = {
                "host": "http://ys04-dns.lwgzs.cn",
                "key": "4Rk247ppxHcadJRwcnp8dPyY2ybEXHP7",
                "iv": "1238389483762837",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJBcHBUbyIsImlhdCI6MTc3OTI3NzI4NywiZXhwIjoxNzc5ODgyMDg3LCJuYmYiOjE3NzkyNzcyODcsInN1YiI6IkFwcFRvIiwianRpIjoiODYxYjkyOTEzOGRmNzY5N2JlYjAyYjkwN2I1MDcwNDQiLCJkYXRhIjp7InVzZXJfaWQiOjM2Mzg2LCJ1c2VyX2NoZWNrIjoiYjJlMzBmZmNmZTljZDU5NTI3YTFlNTkyNzhiOGZkMDYiLCJ1c2VyX25hbWUiOiJ3ZW45NzAwODgifX0.uIhwHtLt1wBPGLBhBb9OzKkn2HsSOWkM6nUAYvqqJiU"
            }

            ext_dict = default_ext.copy()

            # ===== 外部配置覆盖 =====
            if extend:

                try:

                    if (
                            extend.strip().startswith('{') and
                            extend.strip().endswith('}')
                    ):

                        user_ext = json.loads(extend.strip())
                        ext_dict.update(user_ext)

                    elif extend.startswith('http'):
                        ext_dict['host'] = extend.strip()

                except:
                    pass

            self.host = ext_dict.get('host', '').strip()
            self.token = ext_dict.get('token', '').strip()

            key_str = ext_dict.get('key', '').strip()
            iv_str = ext_dict.get('iv', '').strip()

            from_config = ext_dict.get('from', '')
            line_order_input = ext_dict.get('line_order', '')

            if from_config:

                self.line_order, self.block_keywords = \
                    self.parse_config_str(from_config)

            elif line_order_input:

                if isinstance(line_order_input, list):
                    line_order_input = ','.join(line_order_input)

                self.line_order, self.block_keywords = \
                    self.parse_config_str(line_order_input)

            # AES
            if key_str and iv_str:

                self.use_encrypt = True

                self.aes_key = key_str.encode('utf-8')
                self.aes_iv = iv_str.encode('utf-8')

            else:
                self.use_encrypt = False

            if not self.host.startswith('http'):
                return {}

            self.local_uuid = str(uuid.uuid4())

            self.headers.update({
                'appto-local-uuid': self.local_uuid,
                'token': self.token
            })

            url = (
                f'{self.host}'
                '/addons/apptov4/app.php/v1/config/get'
                '?p=android&__platform=android'
            )

            response_data = self.fetch_with_decrypt(
                url,
                headers=self.headers
            )

            data = (
                response_data.get('data', {})
                if 'data' in response_data
                else response_data
            )

            self.config = data

            parsing_conf = data.get('get_parsing', [])

            self.parsing_config = {
                i['key']: [
                    j['label']
                    for j in i['config']
                    if j.get('type') == 'json'
                ]
                for i in parsing_conf
                if i.get('config')
            }

            return {}

        except Exception as e:
            print('init error:', e)
            return {}

    def homeContent(self, filter):

        classes = []
        filters = {}

        home_cate = self.config.get('get_home_cate', [])

        classes = [
            {
                'type_id': str(i['cate']),
                'type_name': i.get('title', '')
            }
            for i in home_cate
            if i.get('cate') and str(i.get('cate')) != '0'
        ]

        # fallback
        if not classes:

            types = self.config.get('get_type', [])

            classes = [
                {
                    'type_id': str(t['type_id']),
                    'type_name': t.get('type_name', '').strip()
                }
                for t in types
                if (
                        t.get('type_pid') == 0 and
                        t.get('type_name') != '全部'
                )
            ]

        # filters
        for t in self.config.get('get_type', []):

            t_id = str(t.get('type_id'))

            extend = t.get('type_extend', {})

            f_list = []

            for f_key, f_name in [
                ('type_name', '分类'),
                ('area', '地区'),
                ('lang', '语言'),
                ('year', '年份')
            ]:

                raw_str = extend.get(f_key)

                if raw_str:

                    items = [
                        {'n': '全部', 'v': ''}
                    ]

                    items += [
                        {
                            'n': i.strip(),
                            'v': i.strip()
                        }
                        for i in raw_str.split(',')
                        if i.strip()
                    ]

                    f_list.append({
                        'key': f_key,
                        'name': f_name,
                        'value': items
                    })

            f_list.append({
                'key': 'order',
                'name': '排序',
                'value': [
                    {'n': '最新', 'v': 'time'},
                    {'n': '最热', 'v': 'hits'},
                    {'n': '高分', 'v': 'score'}
                ]
            })

            if f_list:
                filters[t_id] = f_list

        return {
            'class': classes,
            'filters': filters
        }

    def homeVideoContent(self):

        try:

            url = (
                f'{self.host}'
                '/addons/apptov4/app.php/v1/home/cateData'
                '?id=2&__platform=android'
            )

            data = self.fetch_with_decrypt(
                url,
                headers=self.headers
            ).get('data', {})

            vod_list = []

            for sec in data.get('sections', []):

                for item in sec.get('items', []):

                    vod_list.append({
                        'vod_id': str(item.get('vod_id')),
                        'vod_name': item.get('vod_name'),
                        'vod_pic': item.get('vod_pic'),
                        'vod_remarks': (
                                item.get('vod_remarks')
                                or item.get('vod_score')
                                or ''
                        )
                    })

            return {
                'list': vod_list[:30]
            }

        except:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):

        limit = 21

        params = {
            'type_id': tid,
            'page': pg,
            'pageSize': limit,
            '__platform': 'android',
            'type_name': extend.get('type_name', ''),
            'area': extend.get('area', ''),
            'lang': extend.get('lang', ''),
            'year': extend.get('year', ''),
            'order': extend.get('order', 'time'),
            'sort': 'desc'
        }

        url = (
            f'{self.host}'
            '/addons/apptov4/app.php/v1/vod/getLists'
        )

        data = self.fetch_with_decrypt(
            url,
            params=params,
            headers=self.headers
        ).get('data', {})

        total = int(data.get('total', 0))
        pagecount = (total + limit - 1) // limit

        return {
            'list': data.get('data', []),
            'page': int(pg),
            'pagecount': pagecount,
            'limit': limit,
            'total': total
        }

    def filter_and_sort_playlist(self, vod_play_list):

        if not vod_play_list:
            return vod_play_list

        # 屏蔽
        if self.block_keywords:

            vod_play_list = [
                item for item in vod_play_list
                if not any(
                    kw and kw in (
                        item.get(
                            'player_info',
                            {}
                        ).get(
                            'show',
                            ''
                        ).lower()
                    )
                    for kw in self.block_keywords
                )
            ]

        # 排序
        if self.line_order:

            def get_priority(item):

                show_val = item.get(
                    'player_info',
                    {}
                ).get(
                    'show',
                    ''
                ).lower()

                for idx, kw in enumerate(self.line_order):

                    if kw and kw in show_val:
                        return idx

                return 9999

            vod_play_list.sort(key=get_priority)

        return vod_play_list

    def detailContent(self, ids):

        url = (
            f'{self.host}'
            '/addons/apptov4/app.php/v1/vod/getVod'
            f'?id={ids[0]}&__platform=android'
        )

        data = self.fetch_with_decrypt(
            url,
            headers=self.headers
        ).get('data', {})

        vod_play_list = self.filter_and_sort_playlist(
            data.get('vod_play_list', [])
        )

        vod_play_from = []
        vod_play_url = []

        for i in vod_play_list:

            player_info = i.get('player_info', {})

            line_name = player_info.get(
                'show',
                '未知线路'
            )

            from_value = player_info.get('from', '')

            display_name = (
                f'{line_name}({from_value})'
                if from_value
                else line_name
            )

            play_urls = []

            for j in i.get('urls', []):

                play_name = j.get('name', '播放')
                play_url = j.get('url', '')

                if not play_url:
                    continue

                if from_value:
                    play_urls.append(
                        f'{play_name}${from_value}@{play_url}'
                    )
                else:
                    play_urls.append(
                        f'{play_name}${play_url}'
                    )

            if play_urls:
                vod_play_from.append(display_name)
                vod_play_url.append('#'.join(play_urls))

        video = {
            'vod_id': data.get('vod_id'),
            'vod_name': data.get('vod_name'),
            'vod_pic': data.get('vod_pic'),
            'vod_content': data.get('vod_content', ''),
            'vod_remarks': data.get('vod_remarks', ''),
            'vod_director': data.get('vod_director', ''),
            'vod_actor': data.get('vod_actor', ''),
            'vod_year': data.get('vod_year', ''),
            'vod_area': data.get('vod_area', ''),
            'vod_play_from': '$$$'.join(vod_play_from),
            'vod_play_url': '$$$'.join(vod_play_url)
        }

        return {'list': [video]}

    def searchContent(self, key, quick, pg='1'):

        limit = 20

        url = (
            f'{self.host}'
            '/addons/apptov4/app.php/v1/vod/getVodSearch'
            f'?wd={key}&page={pg}&pageSize={limit}'
            '&__platform=android'
        )

        data = self.fetch_with_decrypt(
            url,
            headers=self.headers
        ).get('data', {})

        total = int(data.get('total', 0))
        pagecount = (total + limit - 1) // limit

        return {
            'list': data.get('data', []),
            'page': int(pg),
            'pagecount': pagecount,
            'limit': limit,
            'total': total
        }

    def playerContent(self, flag, id, vipflags):

        default_ua = (
            'Mozilla/5.0 '
            '(iPhone; CPU iPhone OS 13_2_3 like Mac OS X) '
            'AppleWebKit/605.1.15 '
            '(KHTML, like Gecko) '
            'Version/13.0.3 Mobile/15E148 Safari/604.1'
        )

        # 非解析链接
        if '@' not in id:

            return {
                'parse': 0,
                'url': id,
                'header': {
                    'User-Agent': default_ua
                }
            }

        playfrom, rawurl = id.split('@', 1)

        label_list = self.parsing_config.get(
            playfrom,
            ['默认']
        )

        for label in label_list:

            payload = {
                'play_url': rawurl,
                'label': label,
                'key': playfrom
            }

            try:

                proxy_url = (
                    f'{self.host}'
                    '/addons/apptov4/app.php/v1/parsing/proxy'
                )

                response = self.fetch_with_decrypt(
                    proxy_url,
                    params=payload,
                    method='POST'
                )

                if response and response.get('code') in [1, 200]:

                    data = (
                        response
                        if response.get('code') == 200
                        else response.get('data', {})
                    )

                    play_url = data.get('url')

                    if play_url:

                        ua = (
                                data.get('ua')
                                or data.get('UserAgent')
                                or data.get('UA')
                                or default_ua
                        )

                        return {
                            'parse': 0,
                            'url': play_url,
                            'header': {
                                'User-Agent': ua
                            }
                        }

            except:
                continue

        return {
            'parse': 1,
            'url': rawurl,
            'header': {
                'User-Agent': default_ua
            }
        }

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def localProxy(self, param):
        pass