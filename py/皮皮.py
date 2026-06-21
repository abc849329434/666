import requests
import uuid

HOST = 'http://38.55.237.41:8762'
DEFAULT_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'

device_uuid = str(uuid.uuid4())

def get_headers():
    return {
        'User-Agent': "Dart/2.19 (dart:io)",
        'Accept-Encoding': "gzip",
        'appto-local-uuid': device_uuid
    }

global_config = None
parsing_config = {}

def init():
    global global_config, parsing_config
    if global_config is not None:
        return
    try:
        url = f"{HOST}/apptov5/v1/config/get?p=android&__platform=android"
        resp = requests.get(url, headers=get_headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data and data.get('data'):
            global_config = data['data']
            parsing_config.clear()
            lists = global_config.get('get_parsing', {}).get('lists', [])
            for item in lists:
                if item.get('config'):
                    labels = [c['label'] for c in item['config'] if c.get('type') == 'json']
                    parsing_config[item['key']] = labels
        else:
            print("初始化失败：接口返回无data字段")
    except Exception as e:
        print(f"初始化异常: {e}")

def home():
    init()
    if not global_config:
        return {'class': []}
    classes = []
    for item in global_config.get('get_home_cate', []):
        if isinstance(item.get('extend'), dict):
            classes.append({
                'type_id': str(item.get('cate')),
                'type_name': item.get('title')
            })
    return {'class': classes}

def home_video():
    try:
        url = f"{HOST}/apptov5/v1/home/data?id=1&mold=1&__platform=android"
        resp = requests.get(url, headers=get_headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json().get('data', {})
        vod_list = []
        for section in data.get('sections', []):
            for item in section.get('items', []):
                pic = item.get('vod_pic', '')
                if pic.startswith('mac://'):
                    pic = pic.replace('mac://', 'http://', 1)
                vod_list.append({
                    'vod_id': item.get('vod_id'),
                    'vod_name': item.get('vod_name'),
                    'vod_pic': pic,
                    'vod_remarks': item.get('vod_remarks')
                })
        return {'list': vod_list}
    except Exception as e:
        print(f"首页视频异常: {e}")
        return {'list': []}

def category(tid, pg=1, extend=None):
    if extend is None:
        extend = {}
    try:
        area = extend.get('area', '')
        lang = extend.get('lang', '')
        year = extend.get('year', '')
        sort = extend.get('sort', 'time')

        url = f"{HOST}/apptov5/v1/vod/lists?area={area}&lang={lang}&year={year}&order={sort}&type_id={tid}&page={pg}&pageSize=21&__platform=android"
        resp = requests.get(url, headers=get_headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json().get('data', {})
        vod_data = data.get('data', [])
        for item in vod_data:
            pic = item.get('vod_pic', '')
            if pic.startswith('mac://'):
                item['vod_pic'] = pic.replace('mac://', 'http://', 1)
        return {
            'list': vod_data,
            'page': pg,
            'total': data.get('total', 0)
        }
    except Exception as e:
        print(f"分类异常: {e}")
        return {'list': []}

def detail(id):
    try:
        url = f"{HOST}/apptov5/v1/vod/getVod?id={id}"
        resp = requests.get(url, headers=get_headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json().get('data', {})
        play_from_list = []
        play_url_list = []
        for line in data.get('vod_play_list', []):
            play_from_list.append(line['player_info']['show'])
            urls = [f"{u['name']}${line['player_info']['from']}@{u['url']}" for u in line.get('urls', [])]
            play_url_list.append('#'.join(urls))
        return {
            'list': [{
                'vod_id': data.get('vod_id'),
                'vod_name': data.get('vod_name'),
                'vod_content': data.get('vod_content'),
                'vod_remarks': data.get('vod_remarks'),
                'vod_director': data.get('vod_director'),
                'vod_actor': data.get('vod_actor'),
                'vod_year': data.get('vod_year'),
                'vod_area': data.get('vod_area'),
                'vod_play_from': '$$$'.join(play_from_list),
                'vod_play_url': '$$$'.join(play_url_list)
            }]
        }
    except Exception as e:
        print(f"详情异常: {e}")
        return {'list': []}

def search(wd, pg=1):
    try:
        url = f"{HOST}/apptov5/v1/search/lists?wd={wd}&page={pg}&__platform=android"
        resp = requests.get(url, headers=get_headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json().get('data', {})
        vod_list = []
        for item in data.get('data', []):
            pic = item.get('vod_pic', '')
            if pic.startswith('mac://'):
                pic = pic.replace('mac://', 'http://', 1)
            item['vod_pic'] = pic
            vod_list.append(item)
        return {
            'list': vod_list,
            'page': pg,
            'total': data.get('total', 0)
        }
    except Exception as e:
        print(f"搜索异常: {e}")
        return {'list': []}

def play(id):
    init()
    default_ua = DEFAULT_UA
    parts = id.split('@')
    if len(parts) != 2:
        return {'parse': 0, 'url': id, 'header': {'User-Agent': default_ua}}
    play_from, raw_url = parts
    label_list = parsing_config.get(play_from)
    if not label_list:
        return {'parse': 0, 'url': raw_url, 'header': {'User-Agent': default_ua}}
    result = {'parse': 1, 'url': raw_url, 'header': {'User-Agent': default_ua}}
    for label in label_list:
        payload = {
            'play_url': raw_url,
            'label': label,
            'key': play_from
        }
        try:
            resp = requests.post(f"{HOST}/apptov5/v1/parsing/proxy?__platform=android",
                                 data=payload, headers=get_headers(), timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, dict):
                continue
            if data.get('code') == 422:
                continue
            d = data.get('data', {})
            url = d.get('url')
            if not url:
                continue
            ua = d.get('UA') or d.get('UserAgent') or default_ua
            result = {
                'parse': 0,
                'url': url,
                'header': {'User-Agent': ua}
            }
            break
        except Exception as e:
            print(f"解析异常: {e}")
            continue
    return result

if __name__ == "__main__":
    print("初始化并获取首页分类:")
    print(home())
    print("\n首页视频推荐:")
    print(home_video())
    print("\n分类内容示例:")
    print(category('1', 1))
    print("\n搜索示例:")
    print(search("测试", 1))
    # detail和play需要真实id才能测试
