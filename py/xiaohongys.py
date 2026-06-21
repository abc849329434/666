# -*- coding: utf-8 -*-
# by @嗷呜
import re  # 用于正则表达式操作，例如提取字符串中的数字
import sys    #用于系统相关的操作，例如修改模块路径
from base64 import b64decode    #用于 Base64 编码和解码操作
from Crypto.Cipher import AES    #用于加密和解密操作，例如 AES 加密
from Crypto.Hash import MD5
from Crypto.Util.Padding import unpad
sys.path.append("..")
import json
import time
from pyquery import PyQuery as pq   #用于解析 HTML 文档，类似于 BeautifulSoup
from base.spider import Spider


# 继承自Spider 基类的爬虫类，用于实现具体的爬虫逻辑。
class Spider(Spider):

# 初始化方法

    def init(self, extend=""):
        pass

# 获取爬虫名称
    def getName(self):
        pass

# 检查视频格式,检查给定的 URL 是否是视频格式
    def isVideoFormat(self, url):
        pass

# 手动检查视频
    def manualVideoCheck(self):
        pass

# 动作方法,用于处理某些特定的动作
    def action(self, action):
        pass

# 销毁方法,在爬虫结束时执行清理操作
    def destroy(self):
        pass

# 爬虫配置,目标网站的 URL

    host='https://www.xiaohys.com'

# HTTP 请求头，模拟浏览器访问，避免被网站封禁
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="134", "Google Chrome";v="134"',
        'Origin': host,
        'Referer': f"{host}/",
    }

# 首页内容解析
   
 '''    • 功能：解析网站首页的内容。
     • 逻辑：1. 发起 HTTP 请求获取网站首页的 HTML 内容。
             2. 使用   PyQuery   解析 HTML，提取分类信息（例如科幻片、国产剧等）。
             3. 提取首页推荐的影视列表，并调用   getlist   方法解析列表项。
             4. 返回分类信息和影视列表。
'''  

    def homeContent(self, filter):
        data=self.getpq(self.fetch(self.host,headers=self.headers).text)
        result = {}
        classes = []
        for k in data('.head-more.box a').items():
            i=k.attr('href')
            if i and '/show' in i:
                classes.append({
                    'type_name': k.text(),
                    'type_id': i.split('/')[-1]
                })
        result['class'] = classes
        result['list']=self.getlist(data('.border-box.diy-center .public-list-div'))
        return result

    def homeVideoContent(self):
        pass


# 分类页内容解析

  '''  功能：根据分类 ID 和页码获取分类页的内容。
    • 逻辑：1. 构造 POST 请求数据，包括分类 ID 和页码。
    2. 发起 POST 请求到网站的 API 接口。
    3. 解析返回的 JSON 数据，提取影视列表。
    4. 返回影视列表和分页信息。
'''

    def categoryContent(self, tid, pg, filter, extend):
        body = {'type':tid,'class':'','area':'','lang':'','version':'','state':'','letter':'','page':pg}
        data = self.post(f"{self.host}/index.php/api/vod", headers=self.headers, data=self.getbody(body)).json()
        result = {}
        result['list'] = data['list']
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result


# 详情页内容解析
'''功能：解析影视详情页的内容。
• 逻辑：1. 发起 HTTP 请求获取详情页的 HTML 内容。
2. 使用   PyQuery   解析 HTML，提取影视的基本信息（例如年份、演员、导演等）。
3. 提取播放源信息，包括播放源名称和播放地址。
4. 返回影视详情信息。
'''

    def detailContent(self, ids):
        data = self.getpq(self.fetch(f"{self.host}/detail/{ids[0]}/", headers=self.headers).text)
        v=data('.detail-info.lightSpeedIn .slide-info')
        vod = {
            'vod_year': v.eq(-1).text(),
            'vod_remarks': v.eq(0).text(),
            'vod_actor': v.eq(3).text(),
            'vod_director': v.eq(2).text(),
            'vod_content': data('.switch-box #height_limit').text()
        }
        np=data('.anthology.wow.fadeInUp')
        ndata=np('.anthology-tab .swiper-wrapper .swiper-slide')
        pdata=np('.anthology-list .anthology-list-box ul')
        play,names=[],[]
        for i in range(len(ndata)):
            n=ndata.eq(i)('a')
            n('span').remove()
            names.append(n.text())
            vs=[]
            for v in pdata.eq(i)('li').items():
                vs.append(f"{v.text()}${v('a').attr('href')}")
            play.append('#'.join(vs))
        vod["vod_play_from"] = "$$$".join(names)
        vod["vod_play_url"] = "$$$".join(play)
        result = {"list": [vod]}
        return result

# 搜索功能
'''   功能：根据关键词搜索影视内容。• 
   逻辑：
   1. 发起 HTTP 请求到网站的搜索接口。
   2. 解析返回的 JSON 数据，提取搜索结果。
   3. 返回搜索结果列表。
'''

    def searchContent(self, key, quick, pg="1"):
        data = self.fetch(f"{self.host}/index.php/ajax/suggest?mid=1&wd={key}&limit=9999&timestamp={int(time.time()*1000)}", headers=self.headers).json()
        videos=[]
        for i in data['list']:
            videos.append({
                'vod_id': i['id'],
                'vod_name': i['name'],
                'vod_pic': i['pic']
            })
        return {'list':videos,'page':pg}


# 播放地址解析
# 功能• 获取影视资源的播放地址。
    def playerContent(self, flag, id, vipFlags):
        h,p,url1= {"User-Agent": "okhttp/3.14.9"},1,''
        url=f"{self.host}{id}"
        data = self.getpq(self.fetch(url, headers=self.headers).text)
        try:
            jstr = data('.player .player-left script').eq(0).text()
            jsdata = json.loads(jstr.split('=',1)[-1])
            body, url1= {'url': jsdata['url'],'referer':url},jsdata['url']
            data = self.post(f"{self.host}/static/player/artplayer/api.php?ac=getdate", headers=self.headers, data=body).json()
            l=self.aes(data['data'],data['iv'])
            url=l.get('url') or l['data'].get('url')
            p = 0
            if not url:raise Exception('未找到播放地址')
        except Exception as e:
            print('错误信息：',e)
            if re.search(r'\.m3u8|\.mp4',url1):url=url1
        result = {}
        result["parse"] = p
        result["url"] = url
        result["header"] = h
        return result

   # 功能：本地代理方法（未实现）     
    def localProxy(self, param):
        pass


# 功能：生成请求参数的签名。

    def getbody(self, params):
        t=int(time.time())
        h = MD5.new()
        h.update(f"DS{t}DCC147D11943AF75".encode('utf-8'))
        key=h.hexdigest()
        params.update({'time':t,'key':key})
        return params

# 功能：解析影视列表。

    def getlist(self,data):
        videos=[]
        for i in data.items():
            id = i('a').attr('href')
            if id:
                id = re.search(r'\d+', id).group(0)
                img = i('img').attr('data-src')
                if img and 'url=' in img and 'http' not in img: img = f'{self.host}{img}'
                videos.append({
                    'vod_id': id,
                    'vod_name': i('img').attr('alt'),
                    'vod_pic': img,
                    'vod_remarks': i('.public-prt').text() or i('.public-list-prb').text()
                })
        return videos

 # 功能：将 HTML 内容解析为 PyQuery 对象。

    def getpq(self, data):
        try:
            return pq(data)
        except Exception as e:
            print(f"{str(e)}")
            return pq(data.encode('utf-8'))
            
# 使用 AES 算法解密数据。

    def aes(self, text,iv):
        key = b"d978a93ffb4d3a00"
        iv = iv.encode("utf-8")
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(b64decode(text)), AES.block_size)
        return json.loads(pt.decode("utf-8"))
