#coding=utf-8
#!/usr/bin/python
# 熊修改 
import sys
import json
import time
import requests
from urllib.parse import quote
import hashlib
import os
import tempfile

sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return "Emby(token版-修复版)"

    def init(self, extend):
        self._default_config = {
            'token': "74d1af8a-8026-4b65-b5c6-3da8368731cc",
            'user_id': "cc0a52fd-4d06-4e69-a378-7447263f9f4b",
            'device_id': "74d1af8a-8026-4b65-b5c6-3da8368731cc",
            'device_id_alt': "74d1af8a-8026-4b65-b5c6-3da8368731cc",
            'client': "Hills Windows",
            'device_name': "MyComputer"",
            'client_version': "0.2.2",
            'baseUrl': "https://link00.okemby.org:8443",
            'proxy': "",
            'thread': 0
        }
        
        self.cache_dir = os.path.join(tempfile.gettempdir(), 'emby_cache')
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
        
        self.category_cache = {}
        
        try:
            extendDict = json.loads(extend)
            
            self.baseUrl = extendDict.get('server', '').strip('/')
            if not self.baseUrl:
                self.baseUrl = self._default_config['baseUrl']
                print("服务器地址为空，使用默认服务器")
            
            self.proxy = extendDict.get('proxy', self._default_config['proxy'])
            self.thread = extendDict.get('thread', self._default_config['thread'])
            
            self.token = self._default_config['token']
            self.user_id = self._default_config['user_id']
            self.device_id = self._default_config['device_id']
            self.device_id_alt = self._default_config['device_id_alt']
            self.client = self._default_config['client']
            self.device_name = self._default_config['device_name']
            self.client_version = self._default_config['client_version']
            
            print(f"使用自定义配置: baseUrl={self.baseUrl}")
            
        except:
            print("使用全部默认配置")
            for key, value in self._default_config.items():
                setattr(self, key, value)
        
        self._setup_header()
        
    def _setup_header(self):
        self.header = {
            "User-Agent": f"{self.client}/{self.client_version}".replace(' ', '+'),
            "X-Emby-Client": self.client,
            "X-Emby-Device-Name": self.device_name,
            "X-Emby-Device-Id": self.device_id,
            "X-Emby-Client-Version": self.client_version,
            "X-Emby-Token": self.token,
            "X-Emby-Language": "zh-cn"
        }

    def destroy(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    
    def get_cached_data(self, key, callback, ttl=300):
        cache_file = os.path.join(self.cache_dir, f"{hashlib.md5(key.encode()).hexdigest()}.cache")
        
        if os.path.exists(cache_file) and time.time() - os.path.getmtime(cache_file) < ttl:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        data = callback()
        if data is not None:
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False)
            except:
                pass
        return data
    
    def analyze_category_status(self, category_id):
        def callback():
            try:
                url = f"{self.baseUrl}/emby/Users/{self.user_id}/Items/{category_id}"
                r = self.fetch(url, headers=self.header)
                if r.status_code != 200:
                    return {
                        'has_data': False,
                        'is_empty': True,
                        'has_images': False,
                        'item_count': 0,
                        'category_type': 'unknown',
                        'category_name': '未知分类'
                    }
                
                category_info = r.json()
                category_name = category_info.get('Name', '未命名')
                category_type = category_info.get('Type', 'unknown')
                collection_type = category_info.get('CollectionType', '')
                
                url = f"{self.baseUrl}/emby/Users/{self.user_id}/Items"
                params = {
                    "ParentId": category_id,
                    "Recursive": "true",
                    "IncludeItemTypes": "Movie,Series,Video,Audio,Episode",
                    "Limit": "5",
                    "Fields": "BasicSyncInfo,PrimaryImageAspectRatio"
                }
                
                r = self.fetch(url, params=params, headers=self.header)
                if r.status_code != 200:
                    return {
                        'has_data': False,
                        'is_empty': True,
                        'has_images': False,
                        'item_count': 0,
                        'category_type': category_type,
                        'category_name': category_name
                    }
                
                items_data = r.json()
                total_items = items_data.get('TotalRecordCount', 0)
                
                has_images = False
                valid_items = []
                
                if total_items > 0 and 'Items' in items_data:
                    for item in items_data['Items']:
                        if 'ImageTags' in item and 'Primary' in item['ImageTags']:
                            has_images = True
                            break
                    
                    for item in items_data['Items']:
                        item_type = item.get('Type', '')
                        if item_type not in ['Folder', 'CollectionFolder', 'PhotoAlbum', 'Playlist']:
                            valid_items.append(item)
                
                subcategories = []
                if total_items == 0:
                    url = f"{self.baseUrl}/emby/Users/{self.user_id}/Items"
                    params = {
                        "ParentId": category_id,
                        "Recursive": "false",
                        "IncludeItemTypes": "Folder,CollectionFolder,MusicArtist,MusicAlbum",
                        "Limit": "10",
                        "Fields": "ChildCount,PrimaryImageAspectRatio"
                    }
                    
                    try:
                        r = self.fetch(url, params=params, headers=self.header)
                        if r.status_code == 200:
                            sub_data = r.json()
                            if 'Items' in sub_data:
                                for sub_item in sub_data['Items']:
                                    child_count = sub_item.get('ChildCount', 0)
                                    if child_count > 0:
                                        subcategories.append({
                                            'id': sub_item['Id'],
                                            'name': sub_item.get('Name', '未命名'),
                                            'child_count': child_count
                                        })
                    except:
                        pass
                
                return {
                    'has_data': (total_items > 0 and len(valid_items) > 0) or bool(subcategories),
                    'is_empty': total_items == 0 and not subcategories,
                    'has_images': has_images,
                    'item_count': len(valid_items),
                    'subcategory_count': len(subcategories),
                    'subcategories': subcategories,
                    'category_type': collection_type or category_type,
                    'category_name': category_name,
                    'total_record_count': total_items
                }
                
            except Exception as e:
                print(f"分析分类状态出错: {e}")
                return {
                    'has_data': False,
                    'is_empty': True,
                    'has_images': False,
                    'item_count': 0,
                    'category_type': 'error',
                    'category_name': '错误'
                }
        
        cache_key = f"category_status_{category_id}"
        return self.get_cached_data(cache_key, callback, 300)
    
    def get_default_image_for_category(self, category_id):
        def callback():
            try:
                status = self.analyze_category_status(category_id)
                category_type = status.get('category_type', '').lower()
                
                default_images = {
                    'movies': 'https://via.placeholder.com/200x300/333333/FFFFFF?text=MOVIE',
                    'tvshows': 'https://via.placeholder.com/200x300/333333/FFFFFF?text=TV+SHOW',
                    'series': 'https://via.placeholder.com/200x300/333333/FFFFFF?text=SERIES',
                    'music': 'https://via.placeholder.com/200x300/333333/FFFFFF?text=MUSIC',
                    'books': 'https://via.placeholder.com/200x300/333333/FFFFFF?text=BOOK',
                    'default': 'https://via.placeholder.com/200x300/333333/FFFFFF?text=MEDIA'
                }
                
                return default_images.get(category_type, default_images['default'])
            except:
                return 'https://via.placeholder.com/200x300/333333/FFFFFF?text=MEDIA'
        
        cache_key = f"category_default_image_{category_id}"
        return self.get_cached_data(cache_key, callback, 3600) or 'https://via.placeholder.com/200x300/333333/FFFFFF?text=MEDIA'
    
    def get_default_image_for_item(self, item_type):
        default_images = {
            'Movie': 'https://via.placeholder.com/200x300/333333/FFFFFF?text=MOVIE',
            'Series': 'https://via.placeholder.com/200x300/333333/FFFFFF?text=SERIES',
            'Episode': 'https://via.placeholder.com/200x300/333333/FFFFFF?text=EPISODE',
            'MusicAlbum': 'https://via.placeholder.com/200x300/333333/FFFFFF?text=ALBUM',
            'MusicArtist': 'https://via.placeholder.com/200x300/333333/FFFFFF?text=ARTIST',
            'Book': 'https://via.placeholder.com/200x300/333333/FFFFFF?text=BOOK',
            'default': 'https://via.placeholder.com/200x300/333333/FFFFFF?text=MEDIA'
        }
        return default_images.get(item_type, default_images['default'])
    
    def handle_subcategories(self, parent_id, subcategories, page):
        try:
            videos = []
            
            for subcat in subcategories:
                video_info = {
                    "vod_id": subcat['id'],
                    "vod_name": self.clean_text(subcat['name']),
                    "vod_remarks": f"{subcat.get('child_count', 0)}项",
                    "vod_pic": ""
                }
                
                try:
                    url = f"{self.baseUrl}/emby/Users/{self.user_id}/Items/{subcat['id']}"
                    r = self.fetch(url, headers=self.header)
                    if r.status_code == 200:
                        item_data = r.json()
                        if 'ImageTags' in item_data and 'Primary' in item_data['ImageTags']:
                            video_info['vod_pic'] = f"{self.baseUrl}/emby/Items/{subcat['id']}/Images/Primary?maxHeight=300&maxWidth=200&tag={item_data['ImageTags']['Primary']}&quality=90"
                except:
                    pass
                
                if not video_info['vod_pic']:
                    video_info['vod_pic'] = self.get_default_image_for_category(parent_id)
                
                videos.append(video_info)
            
            return {
                'list': videos,
                'page': page,
                'pagecount': 1,
                'limit': 50,
                'total': len(videos)
            }
            
        except Exception as e:
            print(f"处理子分类出错: {e}")
            return {'list': [], 'page': page, 'pagecount': 0}
    
    
    def homeContent(self, filter):
        try:
            url = f"{self.baseUrl}/emby/Users/{self.user_id}/Views"
            params = {
                "X-Emby-Client": self.client.replace(' ', '+'),
                "X-Emby-Device-Name": self.device_name.replace(' ', '+'),
                "X-Emby-Device-Id": self.device_id,
                "X-Emby-Client-Version": self.client_version,
                "X-Emby-Token": self.token,
                "X-Emby-Language": "zh-cn"
            }
            
            r = self.fetch(url, params=params, headers=self.header, timeout=10)
            if r.status_code != 200:
                return {'class': []}
            
            data = r.json()
            if "Items" not in data:
                return {'class': []}
            
            class_list = []
            exclude_keywords = ['播放列表', '相机', '照片', '游戏']
            
            temp_categories = []
            for item in data["Items"]:
                item_name = item.get('Name', '')
                item_id = item.get('Id', '')
                
                should_exclude = False
                for keyword in exclude_keywords:
                    if keyword in item_name:
                        should_exclude = True
                        break
                
                if should_exclude:
                    continue
                
                temp_categories.append({
                    'name': item_name,
                    'id': item_id
                })
            
            max_check = min(3, len(temp_categories))
            for i, category in enumerate(temp_categories):
                item_name = category['name']
                item_id = category['id']
                
                if i < max_check:
                    try:
                        status = self.analyze_category_status(item_id)
                        if status['has_data']:
                            class_list.append({
                                "type_name": item_name,
                                "type_id": item_id,
                                "has_images": status['has_images'],
                                "item_count": status['item_count']
                            })
                    except:
                        class_list.append({
                            "type_name": item_name,
                            "type_id": item_id,
                            "has_images": True,
                            "item_count": 1
                        })
                else:
                    class_list.append({
                        "type_name": item_name,
                        "type_id": item_id,
                        "has_images": True,
                        "item_count": 1
                    })
            
            if not class_list:
                class_list = [
                    {"type_id": "movies", "type_name": "电影", "has_images": True},
                    {"type_id": "series", "type_name": "剧集", "has_images": True}
                ]
            
            return {'class': class_list}
            
        except Exception as e:
            print(f"获取首页分类出错: {e}")
            return {'class': []}
    
    def categoryContent(self, cid, page, filter, ext):
        try:
            page = int(page) if page else 1
            
            status = self.analyze_category_status(cid)
            
            if not status['has_data']:
                if status['subcategories']:
                    result = self.handle_subcategories(cid, status['subcategories'], page)
                    return {
                        'list': result.get('list', []),
                        'page': result.get('page', page),
                        'pagecount': result.get('pagecount', 1),
                        'limit': result.get('limit', 50),
                        'total': result.get('total', 0)
                    }
                
                return {'list': [], 'page': page, 'pagecount': 0, 'limit': 50, 'total': 0}
            
            start_index = (page - 1) * 50
            url = f"{self.baseUrl}/emby/Users/{self.user_id}/Items"
            
            params = {
                "ParentId": cid,
                "Recursive": "true",
                "SortBy": "DateCreated,SortName",
                "SortOrder": "Descending",
                "Fields": "BasicSyncInfo,PrimaryImageAspectRatio,ProductionYear,CommunityRating,UserData,MediaSources",
                "StartIndex": str(start_index),
                "Limit": "50",
                "ImageTypeLimit": 1,
                "EnableImageTypes": "Primary,Backdrop,Thumb"
            }
            
            category_type = status.get('category_type', '').lower()
            if category_type in ['movies', 'movie']:
                params["IncludeItemTypes"] = "Movie"
            elif category_type in ['tvshows', 'series']:
                params["IncludeItemTypes"] = "Series"
            elif category_type == 'music':
                params["IncludeItemTypes"] = "Audio,MusicAlbum,MusicArtist"
            elif category_type == 'books':
                params["IncludeItemTypes"] = "Book"
            else:
                params["IncludeItemTypes"] = "Movie,Series,Episode,Video"
            
            r = self.fetch(url, params=params, headers=self.header)
            if r.status_code != 200:
                return {'list': [], 'page': page, 'pagecount': 0}
            
            data = r.json()
            total_count = data.get('TotalRecordCount', 0)
            
            videos = []
            has_images = False
            
            if 'Items' in data:
                for item in data['Items']:
                    item_type = item.get('Type', '')
                    
                    if item_type in ['Folder', 'CollectionFolder'] and item_type not in ['MusicArtist', 'MusicAlbum']:
                        continue
                    
                    video_info = {
                        "vod_id": item.get('Id', ''),
                        "vod_name": self.clean_text(item.get('Name', '')),
                        "vod_remarks": "",
                        "vod_pic": ""
                    }
                    
                    if 'ProductionYear' in item:
                        video_info['vod_remarks'] += str(item['ProductionYear'])
                    
                    if 'CommunityRating' in item:
                        if video_info['vod_remarks']:
                            video_info['vod_remarks'] += ' | '
                        video_info['vod_remarks'] += f"⭐{item['CommunityRating']}"
                    
                    if item_type == 'Series' and 'UserData' in item and 'UnplayedItemCount' in item['UserData']:
                        if video_info['vod_remarks']:
                            video_info['vod_remarks'] += ' | '
                        video_info['vod_remarks'] += f"{item['UserData']['UnplayedItemCount']}集"
                    
                    if 'ImageTags' in item and 'Primary' in item['ImageTags']:
                        video_info['vod_pic'] = f"{self.baseUrl}/emby/Items/{item['Id']}/Images/Primary?maxHeight=300&maxWidth=200&tag={item['ImageTags']['Primary']}&quality=90"
                        has_images = True
                    elif 'BackdropImageTags' in item and item['BackdropImageTags']:
                        video_info['vod_pic'] = f"{self.baseUrl}/emby/Items/{item['Id']}/Images/Backdrop?maxHeight=300&tag={item['BackdropImageTags'][0]}&quality=90"
                        has_images = True
                    else:
                        video_info['vod_pic'] = self.get_default_image_for_item(item_type)
                    
                    videos.append(video_info)
            
            if not status['has_images'] and not has_images:
                default_image = self.get_default_image_for_category(cid)
                for video in videos:
                    if not video['vod_pic'] or 'placeholder.com' in video['vod_pic']:
                        video['vod_pic'] = default_image
            
            pagecount = (total_count + 49) // 50 if total_count > 0 else 1
            
            return {
                'list': videos,
                'page': page,
                'pagecount': pagecount,
                'limit': 50,
                'total': total_count
            }
            
        except Exception as e:
            print(f"获取分类内容出错: {e}")
            return {'list': [], 'page': page, 'pagecount': 0}
    
    def detailContent(self, did):
        try:
            item_id = did[0] if isinstance(did, list) else did
            
            url = f"{self.baseUrl}/emby/Users/{self.user_id}/Items/{item_id}"
            params = {
                "Fields": "Genres,Overview,ProductionYear,CommunityRating,IsFolder,Type"
            }
            
            r = self.fetch(url, params=params, headers=self.header)
            if r.status_code != 200:
                return {'list': []}
            
            info = r.json()
            
            vod = {
                "vod_id": item_id,
                "vod_name": self.clean_text(info.get('Name', '')),
                "vod_pic": "",
                "vod_type_name": "",
                "vod_year": info.get('ProductionYear', ''),
                "vod_content": self.clean_text(info.get('Overview', '')),
                "vod_remarks": f"评分：{info['CommunityRating']}" if 'CommunityRating' in info else "",
                "vod_play_from": "EMBY",
                "vod_play_url": ""
            }
            
            if 'Genres' in info:
                vod['vod_type_name'] = ' '.join(info['Genres'])
            
            if 'ImageTags' in info and 'Primary' in info['ImageTags']:
                vod['vod_pic'] = f"{self.baseUrl}/emby/Items/{item_id}/Images/Primary?maxWidth=400&tag={info['ImageTags']['Primary']}&quality=90"
            else:
                vod['vod_pic'] = self.get_default_image_for_item(info.get('Type', 'default'))
            
            item_type = info.get('Type', '')
            is_folder = info.get('IsFolder', False)
            
            if item_type == "Series":
                seasons_url = f"{self.baseUrl}/emby/Shows/{item_id}/Seasons"
                seasons_params = {
                    "UserId": self.user_id,
                    "Fields": "BasicSyncInfo"
                }
                
                r2 = self.fetch(seasons_url, params=seasons_params, headers=self.header)
                if r2.status_code == 200:
                    seasons_data = r2.json()
                    play_from = []
                    play_urls = []
                    
                    if 'Items' in seasons_data:
                        for season in seasons_data['Items']:
                            season_name = self.clean_text(season.get('Name', 'Season')).replace('#', '-').replace('$', '|')
                            play_from.append(season_name)
                            
                            episodes_url = f"{self.baseUrl}/emby/Shows/{item_id}/Episodes"
                            episodes_params = {
                                "SeasonId": season['Id'],
                                "UserId": self.user_id,
                                "Limit": "1000"
                            }
                            
                            r3 = self.fetch(episodes_url, params=episodes_params, headers=self.header)
                            if r3.status_code == 200:
                                episodes_data = r3.json()
                                episode_list = []
                                
                                if 'Items' in episodes_data:
                                    for episode in episodes_data['Items']:
                                        episode_name = self.clean_text(episode.get('Name', 'Episode'))
                                        episode_list.append(f"{episode_name}${episode['Id']}")
                                
                                play_urls.append('#'.join(episode_list))
                        
                        vod['vod_play_from'] = "$$$".join(play_from)
                        vod['vod_play_url'] = "$$$".join(play_urls)
                    else:
                        vod['vod_play_url'] = f"暂无剧集信息${item_id}"
                else:
                    vod['vod_play_url'] = f"暂无剧集信息${item_id}"
                    
            elif is_folder and item_type != 'Series':
                items_url = f"{self.baseUrl}/emby/Users/{self.user_id}/Items"
                items_params = {
                    "ParentId": item_id,
                    "Fields": "BasicSyncInfo,PrimaryImageAspectRatio,ProductionYear,CommunityRating",
                    "ImageTypeLimit": "1",
                    "StartIndex": "0",
                    "EnableUserData": "true"
                }
                
                r4 = self.fetch(items_url, params=items_params, headers=self.header)
                if r4.status_code == 200:
                    items_data = r4.json()
                    play_list = []
                    
                    if 'Items' in items_data:
                        for item in items_data['Items']:
                            item_name = self.clean_text(item.get('Name', '未知项目')).replace('#', '-').replace('$', '|')
                            play_list.append(f"{item_name}${item['Id']}")
                    
                    if play_list:
                        vod['vod_play_url'] = '#'.join(play_list)
                    else:
                        vod['vod_play_url'] = f"暂无内容${item_id}"
                else:
                    vod['vod_play_url'] = f"暂无内容${item_id}"
            else:
                vod['vod_play_url'] = f"正片${item_id}"
            
            return {'list': [vod]}
            
        except Exception as e:
            print(f"获取详情出错: {e}")
            return {'list': []}
    
    
    def homeVideoContent(self):
        return {}
    
    def searchContent(self, key, quick, pg="1"):
        return self.searchContentPage(key, quick, pg)
    
    def searchContentPage(self, keywords, quick, page):
        try:
            page = int(page) if page else 1
            start_index = (page - 1) * 50
            
            url = f"{self.baseUrl}/emby/Users/{self.user_id}/Items"
            params = {
                "SortBy": "SortName",
                "SortOrder": "Ascending",
                "Fields": "BasicSyncInfo,ProductionYear",
                "StartIndex": str(start_index),
                "Recursive": "true",
                "SearchTerm": keywords,
                "IncludeItemTypes": "Movie,Series",
                "Limit": "50"
            }
            
            r = self.fetch(url, params=params, headers=self.header, timeout=15)
            
            if not r or r.status_code != 200:
                return {'list': []}
            
            try:
                data = r.json()
            except:
                return {'list': []}
            
            videos = []
            
            if "Items" in data:
                for item in data["Items"]:
                    if item.get('Type') in ['Movie', 'Series']:
                        video_info = {
                            "vod_id": item.get('Id', ''),
                            "vod_name": self.clean_text(item.get('Name', '')),
                            "vod_pic": "",
                            "vod_remarks": item.get('ProductionYear', '')
                        }
                        
                        if 'ImageTags' in item and 'Primary' in item['ImageTags']:
                            video_info['vod_pic'] = f"{self.baseUrl}/emby/Items/{item['Id']}/Images/Primary?maxWidth=400&tag={item['ImageTags']['Primary']}&quality=90"
                        else:
                            video_info['vod_pic'] = self.get_default_image_for_item(item.get('Type', 'default'))
                        
                        videos.append(video_info)
            
            return {'list': videos}
            
        except Exception as e:
            print(f"搜索出错: {e}")
            return {'list': []}
    
    def playerContent(self, flag, pid, vipFlags):
        try:
            url = f"{self.baseUrl}/emby/Items/{pid}/PlaybackInfo"
            params = {
                "UserId": self.user_id,
                "MaxStreamingBitrate": "140000000"
            }
            
            device_profile = {
                "DeviceProfile": {
                    "MaxStaticBitrate": 140000000,
                    "MaxStreamingBitrate": 140000000,
                    "DirectPlayProfiles": [
                        {"Container": "mp4,m4v", "Type": "Video"},
                        {"Container": "mkv", "Type": "Video"},
                        {"Container": "mov", "Type": "Video"}
                    ]
                }
            }
            
            r = requests.post(
                url, 
                params=params, 
                json=device_profile, 
                headers={"X-Emby-Token": self.token},
                timeout=30
            )
            
            if r.status_code != 200:
                return {'parse': 0, 'jx': 0, 'url': ''}
            
            data = r.json()
            if 'MediaSources' in data and data['MediaSources']:
                media_source = data['MediaSources'][0]
                
                if 'DirectStreamUrl' in media_source:
                    play_url = media_source['DirectStreamUrl']
                    if not play_url.startswith('http'):
                        play_url = self.baseUrl + play_url
                elif 'Path' in media_source:
                    play_url = media_source['Path']
                else:
                    return {'parse': 0, 'jx': 0, 'url': ''}
                
                if int(self.thread) > 0:
                    try:
                        self.fetch('http://127.0.0.1:7777', timeout=5)
                        play_url = f'http://127.0.0.1:7777/?url={quote(play_url)}&thread={self.thread}'
                    except:
                        try:
                            self.fetch('http://127.0.0.1:9978/go', timeout=5)
                            play_url = f'http://127.0.0.1:9978/?url={quote(play_url)}&thread={self.thread}'
                        except:
                            pass
                
                return {
                    "parse": 0,
                    "jx": 0,
                    "url": play_url,
                    "header": self.header
                }
            
            return {'parse': 0, 'jx': 0, 'url': ''}
            
        except Exception as e:
            print(f"播放出错: {e}")
            return {'parse': 0, 'jx': 0, 'url': ''}
    
    def localProxy(self, params):
        pass
    
    def clean_text(self, text):
        if not text:
            return ""
        return text.replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()
    
    def fetch(self, url, params=None, headers=None, timeout=30, method='GET', data=None, json_data=None):
        proxies = None
        if self.proxy:
            proxies = {"http": self.proxy, "https": self.proxy}
        
        headers = headers or self.header
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=timeout, proxies=proxies)
            else:
                response = requests.post(url, params=params, headers=headers, data=data, json=json_data, timeout=timeout, proxies=proxies)
            
            return response
            
        except Exception as e:
            print(f"请求失败: {url}, 错误: {e}")
            class MockResponse:
                def __init__(self):
                    self.status_code = 500
                def json(self):
                    return {}
            return MockResponse()