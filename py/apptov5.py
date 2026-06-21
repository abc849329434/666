# -*- coding: utf-8 -*-
# 七月专用版 Spider（完整版 · 含 sign）
import sys
import uuid
import time
import random
import hashlib
import json
from base.spider import Spider

sys.path.append('..')


class Spider(Spider):
    local_uuid = ''
    config = ''
    parsing_config = []
    headers = {
        'User-Agent': "Dart/2.19 (dart:io)",
        'Accept-Encoding': "gzip",
        'appto-local-uuid': ''
    }
    account = ''
    password = ''
    token = ''
    secret = ''  # ✅ 新增

    def init(self, extend=""):
        try:
            if isinstance(extend, dict):
                self.host = extend.get('host', '').strip()
                self.account = extend.get('account', '')
                self.password = extend.get('password', '')
                self.token = extend.get('token', '')
                self.secret = extend.get('secret', '')  # ✅ 必填
            else:
                self.host = str(extend).strip()

            if not self.host.startswith('http'):
                return {}

            # UUID
            self.local_uuid = str(uuid.uuid4())
            self.headers['appto-local-uuid'] = self.local_uuid

            # 获取配置
            url = self._with_auth(f'{self.host}/apptov5/v1/config/get?p=android&__platform=android')
            res = self.fetch(url, headers=self.headers).json()
            self.config = res['data']

            # 解析配置
            parsing_conf = self.config['get_parsing']['lists']
            parsing_config = {}
            for i in parsing_conf:
                if i['config']:
                    labels = [j['label'] for j in i['config'] if j['type'] == 'json']
                    parsing_config[i['key']] = labels
            self.parsing_config = parsing_config

        except Exception as e:
            print(f'初始化异常：{e}')
            return {}

    # ✅ sign 生成
    def _make_sign(self, params: dict) -> str:
        sign_str = '&'.join(
            f'{k}={params[k]}' for k in sorted(params.keys())
        ) + f'&key={self.secret}'
        return hashlib.md5(sign_str.encode()).hexdigest()

    # ✅ 自动拼 account / token / sign
    def _with_auth(self, url: str) -> str:
        t = str(int(time.time()))
        r = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))

        params = {
            't': t,
            'r': r,
            'account': self.account,
            'password': self.password,
            'token': self.token
        }

        params['sign'] = self._make_sign(params)

        sep = '&' if '?' in url else '?'
        auth_str = '&'.join(f'{k}={v}' for k, v in params.items() if v)
        return f'{url}{sep}{auth_str}'

    # 图片修复
    def fix_pic(self, url):
        if url and url.startswith('mac://'):
            return url.replace('mac://', 'http://', 1)
        return url

    # 详情
    def detailContent(self, ids):
        url = self._with_auth(f"{self.host}/apptov5/v1/vod/getVod?id={ids[0]}")
        res = self.fetch(url, headers=self.headers).json()
        d = res['data']

        play_from, play_url = [], []

        for pl in d['vod_play_list']:
            urls = ''.join(
                f"{u['name']}${pl['player_info']['from']}@{u['url']}#"
                for u in pl['urls']
            )
            play_from.append(pl['player_info']['from'])
            play_url.append(urls.rstrip('#'))

        vod_remarks = '|'.join(filter(None, [
            d.get('vod_remarks', ''),
            str(d.get('vod_year', '')),
            d.get('vod_area', ''),
            ','.join(d.get('vod_type', []))
        ]))

        return {'list': [{
            'vod_id': d.get('vod_id'),
            'vod_name': d.get('vod_name'),
            'vod_content': d.get('vod_content'),
            'vod_remarks': vod_remarks,
            'vod_director': d.get('vod_director'),
            'vod_actor': d.get('vod_actor'),
            'vod_year': d.get('vod_year'),
            'vod_area': d.get('vod_area'),
            'vod_play_from': '$$$'.join(play_from),
            'vod_play_url': '$$$'.join(play_url)
        }]}

    # 搜索
    def searchContent(self, key, quick, pg='1'):
        url = self._with_auth(
            f"{self.host}/apptov5/v1/search/lists?wd={key}&page={pg}&__platform=android"
        )
        res = self.fetch(url, headers=self.headers).json()
        data = res['data']['data']
        for i in data:
            i['vod_pic'] = self.fix_pic(i.get('vod_pic', ''))
        return {'list': data, 'page': pg, 'total': res['data']['total']}

    # 播放解析
    def playerContent(self, flag, id, vipflags):
        default_ua = (
            'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 '
            'Mobile/15E148 Safari/604.1'
        )

        if '@' not in id:
            return {'parse': 0, 'url': id, 'header': {'User-Agent': default_ua}}

        playfrom, rawurl = id.split('@', 1)
        labels = self.parsing_config.get(playfrom, [])

        for label in labels:
            try:
                res = self.post(
                    self._with_auth(f"{self.host}/apptov5/v1/parsing/proxy?__platform=android"),
                    data={'play_url': rawurl, 'label': label, 'key': playfrom},
                    headers=self.headers
                ).json()
                url = res.get('data', {}).get('url')
                if url:
                    ua = res['data'].get('UA') or res['data'].get('UserAgent') or default_ua
                    return {'parse': 0, 'url': url, 'header': {'User-Agent': ua}}
            except Exception:
                continue

        return {'parse': 1, 'url': rawurl, 'header': {'User-Agent': default_ua}}

    # 首页分类
    def homeContent(self, filter):
        if not self.config:
            return {}
        return {'class': [
            {'type_id': i['cate'], 'type_name': i['title']}
            for i in self.config['get_home_cate']
        ]}

    # 首页推荐
    def homeVideoContent(self):
        url = self._with_auth(
            f'{self.host}/apptov5/v1/home/data?id=1&mold=1&__platform=android'
        )
        res = self.fetch(url, headers=self.headers).json()
        data = res['data']

        videos = []
        for sec in data['sections']:
            for v in sec['items']:
                videos.append({
                    'vod_id': v.get('vod_id'),
                    'vod_name': v.get('vod_name'),
                    'vod_pic': self.fix_pic(v.get('vod_pic', '')),
                    'vod_remarks': v.get('vod_remarks')
                })
        return {'list': videos}

    # 分类
    def categoryContent(self, tid, pg, filter, extend):
        url = (
            f"{self.host}/apptov5/v1/vod/lists?"
            f"type_id={tid}&page={pg}&pageSize=21"
            f"&area={extend.get('area','')}"
            f"&year={extend.get('year','')}"
            f"&order={extend.get('sort','time')}"
            f"&__platform=android"
        )
        res = self.fetch(self._with_auth(url), headers=self.headers).json()
        data = res['data']['data']
        for i in data:
            i['vod_pic'] = self.fix_pic(i.get('vod_pic', ''))
        return {'list': data, 'page': pg, 'total': res['data']['total']}

    def destroy(self):
        self.config = None
        self.parsing_config.clear()
