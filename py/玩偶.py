# coding = utf-8
#!/usr/bin/python
from urllib.parse import unquote
from urllib.parse import quote
from base.spider import Spider
from bs4 import BeautifulSoup
from collections import Counter
import urllib.request
import urllib.parse
import threading
import requests
import binascii
import base64
import json
import time
import sys
import re
import os

sys.path.append('..')

xurl = "https://wogg.xxooo.cf/"
xurl1 = "https://drive-h.quark.cn"
xurl2 = "https://pc-api.uc.cn"
QuarkCookie="_UP_A4A_11_=wb9cc16cf7e54cac9272373d5c2cf782; _UP_D_=pc; _UP_F7E_8D_=pQmsvV7eg0X%2F%2FDMR7Wxd1%2BWZ9BPJddRRSI0k5gRbY6749pLGwj583jFyGEyXQv3MQSGQCUEWHd1D8CizlW8ST3INEc0DyOip6k%2BUgbm9KlWusPXMzAkWOyfUGq5bWAvmmQx2ziIybUCbiS4zE6RzqsjWxZaSxVV%2FpJB8QGhoKxfqC5wVx4%2FSnMDHsk0IVO3eZx8LET8RCgn42kZuLkLGu4Vo4l4jGw6mPauAKsNEnj96TT3Gj7VyGemIsTRvs43kkIsxkhIUn8wMe9tBaz8CBvMXfo5Mk0CUK6HNjLd%2FF9D77OC0X2%2F%2BmWWutwXda1RiXySEw8oDUvHASvhlLpYuxYgDRhHgIqYHw4ra%2BbHqXZ3%2FmGNxf47%2BvaAKmH6USzl4rPsU17bDenK4nunnfzPgTNpD11QN53WY7DRrgLIM5vau2prpuIWh1lv6kSia5V2g; _UP_30C_6A_=st9cc620131jp2hskas0vhkulw5yfsv5; _UP_TS_=sg158a118cb18d10331464784a651cee280; _UP_E37_B7_=sg158a118cb18d10331464784a651cee280; _UP_TG_=st9cc620131jp2hskas0vhkulw5yfsv5; __pus=1417350461fd2ecd2e2e0f6c95c8e87aAAR97MDYeimk1tjkwGVFikdwdm1XvPt11AlGYz5cecawIDnklmZ3VWlg6y9zjV3uAmstpy4vNvU93owvuytPlMkG; __kp=a4871210-8562-11f0-95f2-33f6cf6f0737; __kps=AASZnNyz+zYedlH7YTXJCUw9; __ktd=SEX0fsHxCagEMEEIhtgaJw==; __uid=AASZnNyz+zYedlH7YTXJCUw9; tfstk=gSbxeNa4X-rDW3HqMOqoso13iX5Txufqyt5ISdvmfTBRtTJMfnADWh6XEZxMl-89CL6ZmqvMoNBRUTWci1bO4VCF_ZV2SS8VgF8_KJ4hWs527DpV5K7vVLOCNIMscuYWqZRtgJ43-s6o3UOTKNxQ_WJW1FOX5dT7wIJSlI66h3MW9B86CO66PbODMAMslqO7PLR65d6657CWUCL6COT_w_OkSWJZfL0ODW_7Qbqg3V3OyIKvB29KW2FM6npCG3yQda36Dp1XeV2Luk8XhB_QEmRpDssHvilbAi5fwMxR78zeD6O6jatzP0dfc6QeYNwR4cQhJjXmKQ8-D7F-bc-XaIFe-uClo6J6wpVkfcowDkRJK7F-bc-XaQp3awnZbnEF.; __puus=39eefcfd60e038e42816202830d185d2AATLTdSfFNYM1NHGtnPccurQ5PpZODwHE2PRiCPKoqP/5tKyYLQ24JivdlwOHiLOsKxQd2Z9EpVIP3Z+eLHND4OQf6pCy1zYFW2oJKBkAA/A4106RWFOl/0gRAOpGGL/slulom3Do0g+kHicwTtYu4Lu5S0HUAXsMq7ArIxQoGJLrr/Lp+kTqCAOoISVr8YGDqH/F/0czRHD8yvf3E+6SBks"
UCCookie = "ctoken=vnWqk-bpZteBH4ZAeY9MdWgn; b-user-id=03bae751-8dba-4d8a-a7a2-55c9466b3997; UDRIVE_TRANSFER_SESS=fRl9i6apw5YVUM0DBnED79XJXgPti3PmgIK1MFJjo7U1FptJ3Z_D5dibhrdoNXZcF-Rjbshs9COXC1JxR3M24aL6N1fiV0IyzC6ZYqzzSN_7ckOZUdwUvj3W_stlyKtL-hJQPKvgydv1Td2vCCwaK2oYVPdKPIlp6cBI0eyfOlUFbie7LdOrXcqbn_kDsj-p; HMACCOUNT=B1C9964B4485E53F; b-user-id=03bae751-8dba-4d8a-a7a2-55c9466b3997; __itrace_wid=71e40cf0-e890-4414-2bd8-b427ba3e028f; _UP_A4A_11_=wb9ca10c40724777be5ce4dccfc24b89; CwsSessionId=4a6aef92-22e6-4366-bcb9-cd53ab3e2df3; _UP_28A_52_=381; _UP_F7E_8D_=84%2BjZ7SHtvbpAJFBPQj8IZHO4V5ln6s6GUOU%2BWEa1%2FD0I6yjWETtNDMsMpNb24iWrrD1zMwJFjsIpxEoAQFoJnzxAz3%2BQ%2Bs6sDzKXdPuwWWq5ceSNFpeZw7BtOQn%2FKUWcGQ8wd6GAjLdkfon2LwbsekaBxJH%2FMFX7dOZNOZ4JBsh7CGpGW4wTEJcFtTopA7%2BS%2F8fgyhKYsYB7Vy6ciZLQNKESyHBpjG%2FcVMCH1n8GGxfCGoj%2FYwTeaz7FNe2w3pyo%2FoZt5lWEwUkCOA5RlG7T2fxgNZDJAIdI7Q%2FbnxqpO%2FVMYtMRzqrGaAINyd%2BnUvWnYXOVU57%2Fo1kqY%2FtL%2FWqkKAINyd%2BnUvWFakRTfo4KfnCAxJ6fs0%2FZekBWv7p6n%2FqTZLRf7JESgiTxjcavbjWVg%3D%3D; _UP_D_=pc; tfstk=gRVnUgqtIXkpr2dBKacCdFIWKQyodXGScud-2bnPQco1R0eLzu4zDlHypMarq8maVwOKTMOr4rZspDr-93fujXk7p0nKqb47mNIAMsUQRbGFDiCxckvotjpea3HrQFl-r82g9paQRbT11GPcyyTlzCnt4brr_Pu-zburYukwbcgSzHuyTN4ZfcurzQlr_cujPHRU4b7g7cgra0rrLN4Zf4lr4Q02HDEUA5SkcSrinJvT_2Dn0yoU7rPZ0nng8cAybD0nKFUEjQRz182Wi7ml_nm7_ucqKRsMdr2m1oDaCiAI2YVgx8DBuIhuYlPm35I6w0SyFdJVkaASD14JFLME5VmAF1tWKEKo_P_GSKloLVgN6NbMFLME5VmASNv-4vus71C..; __pus=87a2fb7577588f40a987aa43a9883c8fAARNU+1Ts+sCXT7h+RCd3pEpDtV58pg5jd4yJUE3bfql3Bz8mcRB14G4ikEvsH3Qg3udDebRZZDOnX++WT7RfxrG; __kp=a7d77250-8622-11f0-a959-83c103186cd8; __kps=AATeKAB/h4QziTQbWlGrG2iO; __ktd=X6DFrD+hVdVH47schrdJPQ==; __uid=AATeKAB/h4QziTQbWlGrG2iO; Hm_lvt_d2853e18bbb01bff13374d73c9fd1e3d=; Hm_lpvt_d2853e18bbb01bff13374d73c9fd1e3d=1756614385; __puus=056b53ce7cd15929551fbcfb841dc1efAASWTh9LH2v8c5Hm+drdn3X2z7Xt2xNapxycO9DcPS9+vYcYN2VsRVf7rbYZba2A1pUcMzO1XDNf97J/0q/HEdKw5z0mQc32zPnBsBdXsrrq8gEyTiNEiTkRXVE2CT8fbA8beoD0fw8kDRK8SK34oC4aT8Hq81OisuIV5Eryisj2IvSpNOi7eSOZsd+ewkt0lx4="
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) uc-cloud-drive/1.8.7 Chrome/100.0.4896.160 Electron/18.3.5.16-b62cf9c50d Safari/537.36 Channel/ucpan_other_ch",
    'Referer': "https://drive.uc.cn",
    'Cookie': UCCookie
}
header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
}
headerx = {
  'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/2.5.20 Chrome/100.0.4896.160 Electron/18.3.5.12-a038f7b798 Safari/537.36 Channel/pckk_other_ch",
  'Content-Type': "",
  'Referer': "https://pan.quark.cn/",
  'Cookie':QuarkCookie
}
pus_match = re.search(r'__pus=([^;]*)', QuarkCookie)
if pus_match:
    QuarkSet="__pus="+ pus_match.group(1)
    url = "https://drive-pc.quark.cn/1/clouddrive/file/search"
    params = {
      'pr': "ucpro",
      'fr': "pc",
      'q': "TV"
    }
    headers1 = {
      'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/3.0.1 Chrome/100.0.4896.160 Electron/18.3.5.12-a038f7b798 Safari/537.36 Channel/pckk_other_ch",
      'Cookie': QuarkSet
    }
    response = requests.get(url, params=params, headers=headers1)
    res = response.headers
    SetCookie = res.get('Set-Cookie').split(';')[0]
    # print(SetCookie)
    new_pus= SetCookie.split('=', 1)[1]
    old_cookie = headerx['Cookie']
    qp_cookie = re.sub(r'__puus=[^;]*', f'__puus={new_pus}', old_cookie)
    headerx['Cookie'] = qp_cookie
pus1_match = re.search(r'__pus=([^;]*)', UCCookie)
if pus1_match:
    UCSet = "__pus=" + pus1_match.group(1)
    url = "https://pc-api.uc.cn/1/clouddrive/file/search"
    params = {
        'pr': "UCBrowser",
         'fr': "pc",
        'q': "TV"
    }
    headers1 = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/3.0.1 Chrome/100.0.4896.160 Electron/18.3.5.12-a038f7b798 Safari/537.36 Channel/pckk_other_ch",
        'Cookie': UCSet
    }
    response = requests.get(url, params=params, headers=headers1)
    res = response.headers
    SetCookie = res.get('Set-Cookie').split(';')[0]
    # print(SetCookie)
    new_pus = SetCookie.split('=', 1)[1]
    old_cookie = headers['Cookie']
    up_cookie = re.sub(r'__puus=[^;]*', f'__puus={new_pus}', old_cookie)
    headers['Cookie'] = up_cookie
pm = ''


class Spider(Spider):
    global xurl
    global headerx
    global headers
    global header

    def getName(self):
        return "首页"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        result = {}
        result = {"class": [{"type_id": "1", "type_name": "玩偶电影片库"},
                            {"type_id": "2", "type_name": "玩偶剧集片库"},
                            {"type_id": "44", "type_name": "臻彩视界片库"},
                            {"type_id": "3", "type_name": "动漫片库"},
                            {"type_id": "6", "type_name": "短剧片库"},
                            {"type_id": "4", "type_name": "综艺片库"},
                            {"type_id": "46", "type_name": "纪录片片库"},
                            {"type_id": "5", "type_name": "音乐片片库"}
                            ],
                  }

        return result
    def homeVideoContent(self):
        pass

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []
        url = f'{xurl}/vodshow/{cid}--------{pg}---.html'
        res = requests.get(url=url, headers=header)
        res.encoding = "utf-8"
        doc = BeautifulSoup(res.text, 'lxml')
        soups = doc.find_all('div', class_='module-item')
        for i in soups:
            id = i.find('a')['href']
            match = re.search(r'/voddetail/(\d+)', id)
            if match:
                bid = match.group(1)
            name = i.find('a')['title']
            pic = i.find('img')['data-src']
            remarks = i.find('div', class_='module-item-text').text

            video = {
                "vod_id": bid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remarks
            }
            videos.append(video)
        result = {'list': videos}
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        result = {}
        videos = []
        play_form = ""
        play_url1 = ""
        play_kurl = []
        play_urls = []
        did = ids[0]
        url = f'{xurl}/voddetail/{did}.html'
        res = requests.get(url=url, headers=header)
        res.encoding = "utf-8"
        doc = BeautifulSoup(res.text, 'lxml')
        soups = doc.find('div', class_='video-info')
        name = soups.find('h1').text
        actor = soups.find_all('div', class_='video-info-items')
        if len(actor) > 1:
            actor = actor[1].text.replace('\n', '')
        director = soups.find('div', class_='video-info-items').text.replace('\n', '')
        content = soups.find('p', class_='zkjj_a').text.replace('\u3000', '')
        remarks = soups.find('div', class_='tag-link').text.replace('\n', '')
        tag_links = soups.find_all('a', class_='tag-link')
        year = ""
        area = ""
        if len(tag_links) > 1:
            year = tag_links[1].text.strip()
        if len(tag_links) > 1:
            area = tag_links[2].text.strip()
        kjson = doc.find('div', id='download-list')
        if kjson:
            tab_content = kjson.find('div', class_='module-tab-content')
            if tab_content:
                tabs = tab_content.find_all('div', class_='module-tab-item')
                sources = []
                for item in tabs:
                    span = item.find('span')
                    if span and span.get('data-dropdown-value'):
                        source_name = span.get('data-dropdown-value')
                        sources.append(source_name)
                count = Counter(sources)
                result_sources = []
                name_index = {}
                for source in sources:
                    if count[source] > 1:
                        if source not in name_index:
                            name_index[source] = 1
                        else:
                            name_index[source] += 1
                        result_sources.append(f"{source}{name_index[source]}")
                    else:
                        result_sources.append(source)

                play_form = '$$$'.join(result_sources)

            row = kjson.find('div', class_='scroll-box-y')
            if row:
                kurl = row.find_all('div', class_='module-row-info')
                for k in kurl:
                    p_tags = k.find_all('p')
                    for p in p_tags:
                        urls = p.text.strip()
                        if 'quark.cn' in urls:
                            id = 'http://sspa8.top:8100/api/parse_share.php?url=' + urls
                            res = requests.get(url=id, headers=headerx)
                            kjson= res.json()
                            play_urls = kjson['list'][0]['vod_play_url']
                            play_kurl.append(''.join(play_urls).rstrip('#'))
                        else:
                            if 'uc.cn' in urls:
                                id = 'http://sspa8.top:8100/api/parse_share.php?url=' + urls
                                res = requests.get(url=id, headers=headers)
                                kjson = res.json()
                                play_urls = kjson['list'][0]['vod_play_url']
                                play_kurl.append(''.join(play_urls).rstrip('#'))
                play_url1 = '$$$'.join(play_kurl)
        video = {
            "vod_id": did,
            "vod_name": name,
            "vod_actor": actor.replace('主演：', ''),
            "vod_director": director.replace('导演：', ''),
            "vod_content": content,
            "vod_remarks": remarks,
            "vod_year": year,
            "vod_area": area,
            "vod_play_from": play_form,
            "vod_play_url": play_url1
        }
        videos.append(video)

        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):
        ids = binascii.unhexlify(id).decode('utf-8')
        if 'quark' in ids:
            bid = "http://sspa8.top:8100/api/parse.php?url=" + id
            res = requests.get(url=bid, headers=headerx)
            if res.status_code == 200:
                kjson = res.json()
                url = kjson['url']
                result = {}
                result["parse"] = 0
                result["playUrl"] = ''
                result["url"] = url
                result["header"] = headerx
                return result
        else:
            if 'UC' in ids:
                id = "http://sspa8.top:8100/api/parse.php?url=" + id
                res = requests.get(url=id, headers=headers)
                if res.status_code == 200:
                    kjson = res.json()
                    url = kjson['url']
                    result = {}
                    result["parse"] = 0
                    result["playUrl"] = ''
                    result["url"] = url
                    result["header"] = headers
                    return result
    def searchContentPage(self, key, quick, page):
        result = {}
        videos = []
        if not page:
            page = 1
        url = f'{xurl}/vodsearch/-------------.html?wd={key}'
        res = requests.get(url=url, headers=header)
        res.encoding = "utf-8"
        res = res.text
        doc = BeautifulSoup(res, 'lxml')
        soups = doc.find_all('div', class_='module-search-item')
        for i in soups:
            img_tag = i.find('img')
            info_tag = i.find('div', class_='video-info')

            if img_tag and info_tag:
                pic = img_tag.get('data-src') or img_tag.get('src')
            id = i.find('a')['href']
            match = re.search(r'/voddetail/(\d+)', id)
            if match:
                bid = match.group(1)
            name = i.find('img')['alt']
            remarks = info_tag.find('a', class_='video-serial').text
            video = {
                "vod_id": bid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remarks
            }
            videos.append(video)
        result = {'list': videos}
        result['page'] = page
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def searchContent(self, key, quick, pg="1"):
        return self.searchContentPage(key, quick, '1')

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None
