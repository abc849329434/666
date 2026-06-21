python
import requests
import uuid
import json
import re

class TencentVideoSpider:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Origin': 'https://v.qq.com',
            'Referer': 'https://v.qq.com/',
            'Content-Type': 'application/json',
            'Cookie': 'm_video_guid=29da81914f5ae216599e63ca3bb70e6e; msite_tab_experiment_str=111965983; m_video_page_id=channel; _qimei_uuid42=19b0d0a272b1007fa4e1f13910af6624113068aac4; pgv_pvid=a253e6031e25e164; video_omgid=29da81914f5ae216599e63ca3bb70e6e; video_guid=fe12d10ac3a610e7; _qimei_fingerprint=ef908c05cc6a8765525900748c5af013; _qimei_q36=11ac6d53d7c0be47956f165f10001db18114; _qimei_h38=8a7b87a3a4e1f13910af662401000005b19b0d'  # 这里可以填入浏览器复制的腾讯视频cookie，提升稳定性
        }
        self.api_search = "https://v.qq.com/trpc.videosearch.mobile_search.MultiTerminalSearch/MbSearch?vplatform=2"

    def remove_html_tags(self, text):
        if not text:
            return ''
        return re.sub(r'<[^>]+>', '', text)

    def search(self, keyword, page=1):
        body = {
            "version": "25021101",
            "clientType": 1,
            "filterValue": "",
            "uuid": str(uuid.uuid4()),
            "retry": 0,
            "query": keyword,
            "pagenum": page - 1,
            "pagesize": 30,
            "queryFrom": 0,
            "searchDatakey": "",
            "transInfo": "",
            "isneedQc": True,
            "preQid": "",
            "adClientInfo": "",
            "extraInfo": {
                "isNewMarkLabel": "1",
                "multi_terminal_pc": "1",
                "themeType": "1"
            }
        }
        try:
            resp = requests.post(self.api_search, headers=self.headers, json=body, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            # 打印调试
            print(json.dumps(data, ensure_ascii=False, indent=2))
            vlist = []
            vname = ["电视剧", "电影", "综艺", "纪录片", "动漫", "少儿", "短剧"]
            normal_list = data.get('data', {}).get('normalList', {}).get('itemList', [])
            area_box_list = data.get('data', {}).get('areaBoxList', [])
            area_items = area_box_list[0]['itemList'] if area_box_list else []
            combined_list = normal_list + area_items
            if normal_list and normal_list[0].get('doc', {}).get('id') == 'MainNeed':
                combined_list = area_items + normal_list
            for k in combined_list:
                doc = k.get('doc')
                video_info = k.get('videoInfo', {})
                if doc and video_info and doc.get('id') and '外站' not in video_info.get('subTitle', '') and video_info.get('title') and video_info.get('typeName') in vname:
                    img_tag = video_info.get('imgTag')
                    if isinstance(img_tag, str):
                        try:
                            tag = json.loads(img_tag)
                        except:
                            tag = {}
                    else:
                        tag = {}
                    vlist.append({
                        'vod_id': doc['id'],
                        'vod_name': self.remove_html_tags(video_info['title']),
                        'vod_pic': video_info.get('imgUrl', ''),
                        'vod_year': video_info.get('typeName', '') + ' ' + tag.get('tag_2', {}).get('text', ''),
                        'vod_remarks': tag.get('tag_4', {}).get('text', '')
                    })
            return vlist
        except Exception as e:
            print(f"请求异常: {e}")
            return []

if __name__ == "__main__":
    spider = TencentVideoSpider()
    keyword = input("请输入搜索关键词：")
    results = spider.search(keyword)
    if not results:
        print("未搜索到数据，建议检查请求头和cookie")
    else:
        for item in results:
            print(f"{item['vod_name']} ({item['vod_year']}) - ID: {item['vod_id']}")