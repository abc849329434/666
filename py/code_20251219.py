# -*- coding: utf-8 -*-
# 本资源来源于互联网公开渠道，仅可用于个人学习及爬虫技术交流。
# 严禁将其用于任何商业用途，下载后请于 24 小时内删除，搜索结果均来自源站，本人不承担任何责任。
"""
{
    "key": "xxx",
    "name": "xxx",
    "type": 3,
    "api": "./ApptoV5无加密.py",
    "ext": {
        "host": "http://domain.com",
        "排序": "mp4>saohuo>yynb>海外",
        "token": "",
        "username": "你的账号",
        "password": "你的密码"
    }
}
"""

import re,sys,uuid
from base.spider import Spider
from collections import defaultdict
sys.path.append('..')

class Spider(Spider):
    host,config,local_uuid,parsing_config,sort_rules = '','','',[],[]
    # 新增账号密码和token字段
    username = ""
    password = ""
    token = ""
    headers = {
        'User-Agent': "Dart/2.19 (dart:io)",
        'Accept-Encoding': "gzip",
        'appto-local-uuid': local_uuid
    }

    def login(self):
        """账号密码登录获取Token"""
        if not self.username or not self.password or not self.host:
            print("账号、密码或主机地址未配置，跳过登录")
            return False
        
        login_url = f"{self.host}/apptov5/v1/user/login"
        login_data = {
            "username": self.username,
            "password": self.password,
            "__platform": "android"
        }

        try:
            response = self.post(login_url, data=login_data, headers=self.headers).json()
            if response.get("code") == 200 and response.get("data"):
                self.token = response["data"].get("token", "")
                if self.token:
                    print("登录成功，获取到Token")
                    # 更新请求头
                    self.headers['Authorization'] = f"Bearer {self.token}"
                    return True
            print(f"登录失败：{response.get('msg', '未知错误')}")
            return False
        except Exception as e:
            print(f"登录接口请求异常：{e}")
            return False

    def init(self, extend=''):
        try:
            # 解析extend参数
            if extend.startswith('{') and extend.endswith('}'):
                # JSON格式的extend
                import json
                config = json.loads(extend)
                host = config.get("host", "").strip()
                self.sort_rules = config.get("排序", "")
                # 读取账号密码和token
                self.username = config.get("username", "")
                self.password = config.get("password", "")
                self.token = config.get("token", "")
            else:
                # 字符串格式的extend（保持向后兼容）
                host = extend.strip()
                self.sort_rules = ""
            
            if not host.startswith('http'):
                return {}
            if not re.match(r'^https?://[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(:\d+)?/?$', host):
                host_=self.fetch(host).json()
                self.host = host_['domain']
            else:
                self.host = host
            
            self.local_uuid = str(uuid.uuid4())
            # 更新headers中的uuid
            self.headers['appto-local-uuid'] = self.local_uuid

            # 优先使用配置的token，无则自动登录
            if self.token:
                self.headers['Authorization'] = f"Bearer {self.token}"
                print("使用配置的Token")
            else:
                self.login()

            response = self.fetch(f'{self.host}/apptov5/v1/config/get?p=android&__platform=android', headers=self.headers).json()
            config = response['data']
            self.config = config
            parsing_conf = config['get_parsing']['lists']
            parsing_config = {}
            for i in parsing_conf:
                if len(i['config']) != 0:
                    label = []
                    for j in i['config']:
                        if j['type'] == 'json':
                            label.append(j['label'])
                    parsing_config.update({i['key']:label})
            self.parsing_config = parsing_config
            return None
        except Exception as e:
            print(f'初始化异常：{e}')
            return {}

    def detailContent(self, ids):
        # 检查是否是合并的影片ID（多个ID用逗号分隔）
        if ',' in ids[0]:
            all_ids = ids[0].split(',')
        else:
            all_ids = [ids[0]]
        
        # 收集所有播放来源
        all_play_from = []
        all_play_url = []
        main_vod = None
        
        # 存储播放来源信息，用于合并同名播放来源
        play_source_info = defaultdict(list)
        
        for vid in all_ids:
            response = self.fetch(f"{self.host}/apptov5/v1/vod/getVod?id={vid}",headers=self.headers).json()
            data3 = response['data']
            
            # 设置主影片信息（只取第一个）
            if main_vod is None:
                main_vod = {
                    'vod_id': data3.get('vod_id'),
                    'vod_name': data3.get('vod_name'),
                    'vod_content': data3.get('vod_content'),
                    'vod_remarks': data3.get('vod_remarks'),
                    'vod_director': data3.get('vod_director'),
                    'vod_actor': data3.get('vod_actor'),
                    'vod_year': data3.get('vod_year'),
                    'vod_area': data3.get('vod_area')
                }
            
            # 收集播放来源
            for itt in data3["vod_play_list"]:
                source_name = itt["player_info"]["show"]
                episode_count = len(itt['urls'])
                
                # 存储播放来源信息
                play_source_info[source_name].append({
                    "episode_count": episode_count,
                    "urls": itt['urls'],
                    "player_info": itt["player_info"]
                })
        
        # 处理同名播放来源，只保留集数最多的那个
        for source_name, sources in play_source_info.items():
            # 按集数排序（降序）
            sorted_sources = sorted(sources, key=lambda x: x["episode_count"], reverse=True)
            best_source = sorted_sources[0]
            
            # 对集数进行排序
            sorted_episodes = self.sort_episodes(best_source['urls'])
            
            # 构建播放列表
            a = []
            for it in sorted_episodes:
                a.append(f"{it['name']}${best_source['player_info']['from']}@{it['url']}")
            
            # 将集数信息加入线路名称
            display_name = f"{source_name}({best_source['episode_count']}集)"
            
            # 添加到总播放列表
            all_play_from.append(display_name)
            all_play_url.append("#".join(a))
        
        # 线路排序功能
        if self.sort_rules and all_play_from:
            sort_list = [rule.strip().lower() for rule in self.sort_rules.split('>') if rule.strip()]
            
            def sort_key(item):
                line_name = item['source_key'].lower()
                # 检查线路名称是否包含排序规则中的关键词
                for priority, keyword in enumerate(sort_list):
                    if keyword in line_name:
                        return priority
                # 如果没有匹配到任何关键词，放在最后
                return len(sort_list)
            
            # 创建排序用的临时列表
            temp_sources = [{'source_key': all_play_from[i], 'play_url': all_play_url[i]} for i in range(len(all_play_from))]
            
            # 对播放源进行排序
            temp_sources.sort(key=sort_key)
            
            # 重新构建排序后的播放信息
            all_play_from = [source['source_key'] for source in temp_sources]
            all_play_url = [source['play_url'] for source in temp_sources]
        
        # 设置合并后的播放来源
        main_vod["vod_play_from"] = "$$$".join(all_play_from)
        main_vod["vod_play_url"] = "$$$".join(all_play_url)
        
        videos = [main_vod]
        return {'list': videos}

    def sort_episodes(self, episodes):
        """
        对集数进行排序，处理杂乱的集数排列
        """
        # 尝试提取集数数字进行排序
        episode_data = []
        for episode in episodes:
            name = episode['name']
            # 尝试提取集数数字
            episode_num = self.extract_episode_number(name)
            episode_data.append({
                'name': name,
                'episode_num': episode_num,
                'url': episode['url'],
                'original': episode
            })
        
        # 如果大部分集数都能提取到数字，则按数字排序
        numeric_count = sum(1 for ep in episode_data if ep['episode_num'] is not None)
        if numeric_count > len(episode_data) * 0.5:  # 超过一半的集数有数字
            # 按数字排序
            sorted_episodes = sorted(episode_data, key=lambda x: 
                x['episode_num'] if x['episode_num'] is not None else float('inf'))
        else:
            # 否则保持原始顺序
            sorted_episodes = episode_data
        
        # 返回排序后的原始数据
        return [ep['original'] for ep in sorted_episodes]

    def extract_episode_number(self, episode_name):
        """
        从集数名称中提取数字
        """
        # 常见的集数模式
        patterns = [
            r'第?(\d+)[集話话]',  # 匹配 "第1集", "1集", "第1話" 等
            r'^(\d+)$',          # 匹配纯数字
            r'EP?(\d+)',         # 匹配 "EP1", "E1" 等
            r'(\d+)',            # 匹配任何数字
        ]
        
        for pattern in patterns:
            match = re.search(pattern, episode_name)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        # 如果没有找到数字，返回None
        return None

    def searchContent(self, key, quick, pg='1'):
        url = f"{self.host}/apptov5/v1/search/lists?wd={key}&page={pg}&type=&__platform=android"
        response = self.fetch(url, headers=self.headers).json()
        data = response['data']['data']
        
        # 处理图片URL
        for i in data:
            if i.get('vod_pic', '').startswith('mac://'):
                i['vod_pic'] = i['vod_pic'].replace('mac://', 'http://', 1)
        
        # 合并搜索结果（按影片名称和提取的更新集数）
        merged_results = defaultdict(list)
        for video in data:
            # 使用影片名称和提取的更新集数作为合并键
            original_name = video["vod_name"]
            vod_remarks = video.get("vod_remarks", "")
            
            # 提取更新集数
            episode_info = self.extract_episode_info(vod_remarks)
            merge_key = (original_name, episode_info)
            
            merged_results[merge_key].append(video)
        
        # 创建合并后的结果列表
        cleaned_list = []
        for (name, episode_info), sources in merged_results.items():
            if len(sources) > 1:
                # 多个来源的影片：合并播放来源
                # 创建合并后的影片条目
                merged_video = sources[0].copy()
                merged_video["vod_name"] = name
                
                # 合并所有ID（用于详情页获取所有播放来源）
                merged_video["vod_id"] = ",".join([str(v["vod_id"]) for v in sources])
                
                # 添加来源数量标记
                if episode_info:
                    merged_video["vod_remarks"] = f"{episode_info} ({len(sources)}个来源)"
                else:
                    merged_video["vod_remarks"] = f"{len(sources)}个来源"
                
                cleaned_list.append(merged_video)
            else:
                # 单个来源的影片：直接使用
                cleaned_list.append(sources[0])
        
        result = {'list': cleaned_list, 'page': pg, 'total': response['data']['total']}
        return result

    def extract_episode_info(self, remarks):
        """
        从vod_remarks中提取更新集数信息
        """
        if not remarks:
            return ""
        
        patterns = [
            r'更新至\s*(\d+)\s*集',
            r'更新至\s*第\s*(\d+)\s*集',
            r'全\s*(\d+)\s*集',
            r'(\d+)\s*集全',
            r'第\s*(\d+)\s*集',
            r'(\d+)\s*集'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, remarks)
            if match:
                episode_num = match.group(1)
                return f"{episode_num}集"
        
        return ""

    def playerContent(self, flag, id, vipflags):
        default_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
        parsing_config = self.parsing_config
        parts = id.split('@')
        if len(parts) != 2:
            return {'parse': 0, 'url': id, 'header': {'User-Agent': default_ua}}
        playfrom, rawurl = parts
        label_list = parsing_config.get(playfrom)
        if not label_list:
            return {'parse': 0, 'url': rawurl, 'header': {'User-Agent': default_ua}}
        result = {'parse': 1, 'url': rawurl, 'header': {'User-Agent': default_ua}}
        for label in label_list:
            payload = {
                'play_url': rawurl,
                'label': label,
                'key': playfrom
            }
            try:
                response = self.post(
                    f"{self.host}/apptov5/v1/parsing/proxy?__platform=android",
                    data=payload,
                    headers=self.headers
                ).json()
            except Exception as e:
                print(f"请求异常: {e}")
                continue
            if not isinstance(response, dict):
                continue
            if response.get('code') == 422:
                continue
            data = response.get('data')
            if not isinstance(data, dict):
                continue
            url = data.get('url')
            if not url:
                continue
            ua = data.get('UA') or data.get('UserAgent') or default_ua
            result = {
                'parse': 0,
                'url': url,
                'header': {'User-Agent': ua}
            }
            break
        return result

    def homeContent(self, filter):
        config = self.config
        if not config:
            return {}
        home_cate = config['get_home_cate']
        classes = []
        for i in home_cate:
            if isinstance(i.get('extend', []),dict):
                classes.append({'type_id': i['cate'], 'type_name': i['title']})
        return {'class': classes}

    def homeVideoContent(self):
        response = self.fetch(f'{self.host}/apptov5/v1/home/data?id=1&mold=1&__platform=android',headers=self.headers).json()
        data = response['data']
        vod_list = []
        for i in data['sections']:
            for j in i['items']:
                vod_pic = j.get('vod_pic')
                if vod_pic.startswith('mac://'):
                    vod_pic = vod_pic.replace('mac://', 'http://', 1)
                vod_list.append({
                    "vod_id": j.get('vod_id'),
                    "vod_name": j.get('vod_name'),
                    "vod_pic": vod_pic,
                    "vod_remarks": j.get('vod_remarks')
                })
        return {'list': vod_list}

    def categoryContent(self, tid, pg, filter, extend):
        response = self.fetch(f"{self.host}/apptov5/v1/vod/lists?area={extend.get('area','')}&lang={extend.get('lang','')}&year={extend.get('year','')}&order={extend.get('sort','time')}&type_id={tid}&type_name=&page={pg}&pageSize=21&__platform=android", headers=self.headers).json()
        data = response['data']
        data2 = data['data']
        for i in data['data']:
            if i.get('vod_pic','').startswith('mac://'):
                i['vod_pic'] = i['vod_pic'].replace('mac://', 'http://', 1)
        return {'list': data2, 'page': pg, 'total': data['total']}

    def getName(self):
        return "ApptoV5无加密爬虫"

    def isVideoFormat(self, url):
        video_ext = ['.mp4', '.mkv', '.flv', '.avi', '.mov', '.wmv', '.m3u8']
        return any(url.lower().endswith(ext) for ext in video_ext)

    def manualVideoCheck(self):
        return True

    def destroy(self):
        self.host = ""
        self.config = ""
        self.local_uuid = ""
        self.token = ""

    def localProxy(self, param):
        return {}
