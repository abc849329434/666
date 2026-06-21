# -*- coding: utf-8 -*-
import requests
import urllib3
from bs4 import BeautifulSoup
import re

urllib3.disable_warnings()

class Spider:
    def __init__(self):
        self.host = "https://www.tjtcdl.com"
        self.session = requests.Session()
        self.session.verify = False
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(self.headers)

    def getName(self):
        return "茶杯狐-TJTCDL"

    def init(self, extend=""):
        pass

    def homeContent(self, filter):
        """使用指定的分类格式"""
        categories_str = "电视剧$type/2#电影$type/1#动漫$type/4#综艺$type/3#腾讯VIP精选$label/qq#B站VIP精选$label/bli#优酷VIP精选$label/youku#"
        
        classes = []
        categories = categories_str.strip('#').split('#')
        
        for cat in categories:
            if '$' in cat:
                name, path = cat.split('$')
                # 使用路径作为 type_id，这样在 categoryContent 中可以直接使用
                classes.append({
                    "type_id": path,
                    "type_name": name
                })
        
        return {"class": classes}

    def categoryContent(self, cid, pg, filter, ext):
        """分类页面抓取"""
        try:
            # 直接使用 cid 作为路径
            if pg == 1:
                url = f"{self.host}/{cid}"
            else:
                # 尝试几种可能的分页格式
                url = f"{self.host}/{cid}?page={pg}"
            
            print(f"正在请求: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # 检查页面内容
            if len(response.text) < 1000:
                print(f"页面内容过短，尝试其他分页格式")
                # 尝试其他分页格式
                url = f"{self.host}/{cid}-{pg}.html"
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试多种选择器
            video_items = []
            selectors = [
                '.public-list-box',
                '.stui-vodlist__box',
                '.module-item',
                'a[href*="/play/"]',
                'a[href*="/vod/"]',
            ]
            
            for selector in selectors:
                items = soup.select(selector)
                if items and len(items) > 0:
                    print(f"使用选择器 '{selector}' 找到 {len(items)} 个项目")
                    video_items = items
                    break
            
            # 如果还没找到，尝试直接搜索所有链接
            if not video_items:
                print("尝试直接搜索所有播放链接...")
                all_links = soup.find_all('a', href=re.compile(r'/play/\d+'))
                if all_links:
                    video_items = all_links
                    print(f"直接搜索找到 {len(all_links)} 个播放链接")
            
            videos = []
            
            for item in video_items:
                try:
                    # 获取链接
                    if item.name == 'a':
                        link = item
                    else:
                        link = item.select_one('a') or item.select_one('a[href*="/play/"]')
                    
                    if not link or not link.get('href'):
                        continue
                    
                    href = link['href'].strip()
                    
                    # 构建完整URL
                    if href.startswith('//'):
                        full_url = 'https:' + href
                    elif href.startswith('/'):
                        full_url = self.host + href
                    elif not href.startswith('http'):
                        full_url = self.host.rstrip('/') + '/' + href.lstrip('/')
                    else:
                        full_url = href
                    
                    # 获取标题
                    title = ""
                    if link.get('title'):
                        title = link['title'].strip()
                    elif link.text.strip():
                        title = link.text.strip()
                    else:
                        img = link.select_one('img') or item.select_one('img')
                        if img and img.get('alt'):
                            title = img['alt'].strip()
                    
                    if not title:
                        title = "未知标题"
                    
                    # 获取图片
                    pic = ""
                    img = link.select_one('img') or item.select_one('img')
                    if img:
                        pic = img.get('data-src') or img.get('data-original') or img.get('src') or ""
                        if pic.startswith('//'):
                            pic = 'https:' + pic
                        elif pic.startswith('/'):
                            pic = self.host + pic
                    
                    # 获取备注
                    remark = ""
                    remark_elem = item.select_one('.public-list-prb') or item.select_one('.pic-text') or item.select_one('.note')
                    if remark_elem:
                        remark = remark_elem.text.strip()
                    
                    videos.append({
                        "vod_id": full_url,
                        "vod_name": title[:100],
                        "vod_pic": pic,
                        "vod_remarks": remark[:50]
                    })
                    
                except Exception as e:
                    print(f"处理项目时出错: {e}")
                    continue
            
            print(f"成功提取 {len(videos)} 个视频")
            
            return {
                'list': videos,
                'page': int(pg),
                'pagecount': 9999 if videos else 0,
                'limit': 90,
                'total': 999999 if videos else 0
            }
            
        except Exception as e:
            print(f"请求分类 {cid} 第 {pg} 页失败: {e}")
            return {'list': [], 'page': int(pg), 'pagecount': 0, 'limit': 0, 'total': 0}

    def detailContent(self, ids):
        """详情页抓取"""
        play_url = ids[0]
        try:
            response = self.session.get(play_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            play_from = []
            play_urls = []
            
            # 获取播放线路
            tabs = soup.select('.anthology-tab .swiper-slide')
            boxes = soup.select('.anthology-list-box')
            
            if not tabs or not boxes:
                # 单集视频
                play_from.append('直达线路')
                play_urls.append(f'第1集${play_url}')
            else:
                for i, tab in enumerate(tabs):
                    if i >= len(boxes):
                        break
                    
                    box = boxes[i]
                    episodes = []
                    
                    for a in box.select('li a'):
                        href = a.get('href')
                        if not href:
                            continue
                        
                        if href.startswith('http'):
                            full_url = href
                        elif href.startswith('/'):
                            full_url = self.host + href
                        else:
                            base_url = play_url.rsplit('/', 1)[0] + '/'
                            full_url = base_url + href
                        
                        episodes.append(f"{a.text.strip()}${full_url}")
                    
                    if episodes:
                        play_from.append(tab.text.strip())
                        play_urls.append('#'.join(episodes))
            
            return {'list': [{
                "vod_id": play_url,
                "vod_name": soup.select_one('h1') and soup.select_one('h1').text.strip() or play_url,
                "vod_play_from": '$$$'.join(play_from),
                "vod_play_url": '$$$'.join(play_urls)
            }]}
            
        except Exception as e:
            print(f"获取详情失败: {e}")
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        """搜索功能"""
        try:
            url = f"{self.host}/cupfox-search/-------------.html"
            params = {'wd': key}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            videos = []
            
            for item in soup.select('.public-list-box'):
                link = item.select_one('.public-list-exp')
                if not link:
                    continue
                
                href = link.get('href', '').strip()
                if not href:
                    continue
                
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    full_url = self.host + href
                else:
                    full_url = f"{self.host}/{href}"
                
                img = item.select_one('img')
                remark = item.select_one('.public-list-prb')
                
                videos.append({
                    "vod_id": full_url,
                    "vod_name": link.get('title', '').strip(),
                    "vod_pic": img.get('data-src') or img.get('src', '') if img else '',
                    "vod_remarks": remark.text.strip() if remark else ''
                })
            
            return {'list': videos, 'page': int(pg), 'pagecount': 1, 'limit': len(videos), 'total': len(videos)}
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return {'list': [], 'page': int(pg), 'pagecount': 0, 'limit': 0, 'total': 0}

# 测试代码
if __name__ == "__main__":
    spider = Spider()
    
    # 测试各个分类
    test_categories = [
        ("type/2", "电视剧"),
        ("type/1", "电影"),
        ("type/4", "动漫"),
        ("type/3", "综艺"),
        ("label/qq", "腾讯VIP精选"),
        ("label/bli", "B站VIP精选"),
        ("label/youku", "优酷VIP精选"),
    ]
    
    for cid, name in test_categories:
        print(f"\n{'='*50}")
        print(f"测试 {name} (CID: {cid})")
        print('='*50)
        
        result = spider.categoryContent(cid, 1, {}, {})
        print(f"获取到 {len(result['list'])} 个视频")
        
        if result['list']:
            first_video = result['list'][0]
            print(f"第一个视频: {first_video['vod_name']}")
            print(f"链接: {first_video['vod_id']}")
