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

xurl = "https://tv.yydsys.top"
xurl1 = "https://drive-h.quark.cn"
xurl2 = "https://pc-api.uc.cn"
xurl3 = "https://drive-social-api.quark.cn"
xurl4 = "https://pan.baidu.com"
#除UCcookie需要token开头的,其他任意填
QuarkCookie="ctoken=KnY0MBW1hG1fGJNyhhtY388Z; grey-id=b0a4a4ee-0a61-6ae4-4069-a9fe2817f1bd; grey-id.sig=7fFElXv2VhjiLvM_h-ILhYs9OPPbBQkB96qV0hK6QnQ; b-user-id=016f656a-5ae8-476c-0aaf-0af8a2ba060d; _UP_A4A_11_=wb9c817f681f4f3a8a37a19bb7bf2c81; _qk_bx_ck_v1=eyJkZXZpY2VJZCI6ImVDeSNBQU5DNFYwZjVGMHhYRjA1VkhrbGd6clU5eDU1Yy9wdDBSeHpiQkhqNHlhc01pVEUxaDJkaURUMnl4NTM4MXVNOVU0PSIsImRldmljZUZpbmdlcnByaW50IjoiZTE0MmQ5NjBjYzc3ZmFmNmU3YjA0YTY3ZTMwYjgxMDMifQ==; isQuark=true; isQuark.sig=hUgqObykqFom5Y09bll94T1sS9abT1X-4Df_lzgl8nM; __wpkreporterwid_=7ad221ff-a1a3-4cf4-3680-f3c8cfb2c843; web-grey-id=6dba1e48-b208-3bb4-8439-32db7212123f; web-grey-id.sig=KgTMa_2iFps5rLMekVpAOhrRuZ779xcQ4oICH3YFlBY; b-user-id=016f656a-5ae8-476c-0aaf-0af8a2ba060d; isg=BHt7CvSml-XnCqt2nxZ-LBDFAV3l0I_S1lq53204V3qRzJuu9aAfIpkP4ionL-fK; __sdid=AASbublk3be4UiDbqpIq1jCCMlQzb5jEWp9z+j3g0v30XOrfNMZEWWZaGXbj76Dl3gVQ6W4B4E/eTeCvS06oHuoC3UbiYjCD7betU8E0YhoTPg==; _UP_F7E_8D_=pQmsvV7eg0VJeiionGXHFWxDqKGD%2F6Qco1yYm%2Fbgl5Mj3DtPrY0aiehwKogXx4Zoo7xy8nMo2e8c8umX3Lj2gnAl%2BT0uI3e2pJuw4fApHUNvQtRjZMJ%2Bg89lnhrn%2BCkzn9yTmN52ylz2ygc6wv%2FIKg5Eh65wTlP%2Br1ItZcJOhyWzkQhnoHIwa1fugveiX1ySGhXRrsaQfg3I0yA1a12t0%2BHZ47Hvtvq2wLtchZ7GH2KZHru1xRmXkuBjb%2Fc8wRewYz9h5pffYxWK%2F0qf8QQBnEuS6L6HN6GSNeOVPJTh0g%2FdldBvB7trVMH3IhYSoUw2AYTF7eNiF%2BU9DgASvb4Vfvosp%2BEFl7vny0TNscSZMOl8DcfixlwkYTpwSCY4564fHGA9cyxKste3pBRULSTR8JY7n3P6zUYaG%2BofGCzsMul3NGY6wl6lBISYJ2cSDS100Hjqhb3FcWuLwSSSdvGDxA%3D%3D; _UP_D_=pc; _UP_30C_6A_=st9cd620112ty6rqtmez53jn3whsmm7y; _UP_TS_=sg12c71fdeb8612f2aa7ebcf605dfbe9978; _UP_E37_B7_=sg12c71fdeb8612f2aa7ebcf605dfbe9978; _UP_TG_=st9cd620112ty6rqtmez53jn3whsmm7y; _UP_335_2B_=1; tfstk=gFbnejX9je-KZB3Ix7YQvazwx_SkAeTWnT3JeUpzbdJsvpLRaUuPe_Lp4J1RILXRNp7p9pdPEOp6ypQdvgcCSt0-JJZCa4YJz-eYkrCIOUTzHXOfi0HBZIuUyHuy7eOR2TOEArCCOfS1HUxukbAj8o9eUT-F_CRkQY8y44PMQQAj4vWyz5VMGQRr8LJU7ARXMUJPUUPG_dOyzBWyz5fwCQRRrmpdL9_aUMq1iU9GxNAHxK5gq2uh-qKk36Jiwu_Mt49VTd0ryp3CFC5VEJ0XTaAhoeQzMPpkCM7yJwytrtXG0Fb9xbF9bN5F8H_8I4Syrco4M70WHPf-V0te1CvvnpMk7hk2pINgsm8kYCOaW5ViV0te1CvYs5mJUHR6_PC..; __pus=4d8926b3aba90c1901ab468c255b03f1AAR2xQueIertLfr5+mjx7XHAFjkRNLyCxHe3ayBCP0Ae/GiK8x0EMaYDTlR2HQAZ9edBGeAIMdUtFJWO13auLEfm; __kp=a8164b40-9042-11f0-afd5-0919cdaf0e7b; __kps=AASZnNyz+zYedlH7YTXJCUw9; __ktd=SEX0fsHxCagEMEEIhtgaJw==; __uid=AASZnNyz+zYedlH7YTXJCUw9; __puus=582a504f7af265e4de8fc4c834f69550AATLTdSfFNYM1NHGtnPccurQ6llush5K3/8ka13CJRuGHrxU0yvfCPD+AM9gUNSG73IERbHuRbv2XOydLlDZK1ZyEh7pq1H7zJgZCmADcdJu6pOXegUVH5ukf6rS9NTTunCxh4PyWiBKQ3VUX8GJsODdGejEw554xX4pqeNaR1VDF0r27/QTN3eWkZ8gV9z5lar4GMatqwZsnfwnwpaO3bsl"

UCCookie = "ctoken=vnWqk-bpZteBH4ZAeY9MdWgn; b-user-id=03bae751-8dba-4d8a-a7a2-55c9466b3997; UDRIVE_TRANSFER_SESS=fRl9i6apw5YVUM0DBnED79XJXgPti3PmgIK1MFJjo7U1FptJ3Z_D5dibhrdoNXZcF-Rjbshs9COXC1JxR3M24aL6N1fiV0IyzC6ZYqzzSN_7ckOZUdwUvj3W_stlyKtL-hJQPKvgydv1Td2vCCwaK2oYVPdKPIlp6cBI0eyfOlUFbie7LdOrXcqbn_kDsj-p; HMACCOUNT=B1C9964B4485E53F; b-user-id=03bae751-8dba-4d8a-a7a2-55c9466b3997; __itrace_wid=71e40cf0-e890-4414-2bd8-b427ba3e028f; _UP_A4A_11_=wb9ca10c40724777be5ce4dccfc24b89; CwsSessionId=4a6aef92-22e6-4366-bcb9-cd53ab3e2df3; tfstk=gRVnUgqtIXkpr2dBKacCdFIWKQyodXGScud-2bnPQco1R0eLzu4zDlHypMarq8maVwOKTMOr4rZspDr-93fujXk7p0nKqb47mNIAMsUQRbGFDiCxckvotjpea3HrQFl-r82g9paQRbT11GPcyyTlzCnt4brr_Pu-zburYukwbcgSzHuyTN4ZfcurzQlr_cujPHRU4b7g7cgra0rrLN4Zf4lr4Q02HDEUA5SkcSrinJvT_2Dn0yoU7rPZ0nng8cAybD0nKFUEjQRz182Wi7ml_nm7_ucqKRsMdr2m1oDaCiAI2YVgx8DBuIhuYlPm35I6w0SyFdJVkaASD14JFLME5VmAF1tWKEKo_P_GSKloLVgN6NbMFLME5VmASNv-4vus71C..; __pus=87a2fb7577588f40a987aa43a9883c8fAARNU+1Ts+sCXT7h+RCd3pEpDtV58pg5jd4yJUE3bfql3Bz8mcRB14G4ikEvsH3Qg3udDebRZZDOnX++WT7RfxrG; __kp=a7d77250-8622-11f0-a959-83c103186cd8; __kps=AATeKAB/h4QziTQbWlGrG2iO; __ktd=X6DFrD+hVdVH47schrdJPQ==; __uid=AATeKAB/h4QziTQbWlGrG2iO; Hm_lvt_d2853e18bbb01bff13374d73c9fd1e3d=1757727829; Hm_lpvt_d2853e18bbb01bff13374d73c9fd1e3d=1757727855; __puus=d0d6bbd3c408671d0b98baf357fd56f2AASWTh9LH2v8c5Hm+drdn3X2mj7emf4+l8NzEnuza7gpke5WkDrRIwqY2ZeAn0xnH0eMtuswpoE9pjlK2R1H0u2YAiQ7Vs8N2WmsJQFa+oUrKbdEvLt3vfIAg7Kegcysc0Lm5ELWs5Yzsxj1pVX/4V0sO1VSc8di1W88LsPBi1K55dVwrNJV9ofmJtDFU2stbm0="

BaiduCookie = "BDUSS=2VIemJDMFN0Q09nZGpKUTlKZ1FiZ1gwN2ZaOVd0VURxa2w4N2poZEJWSnhMczlvRVFBQUFBJCQAAAAAAAAAAAEAAAA9049Sa2hqbXRqbWRqdHdtZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHGhp2hxoadoR;STOKEN=c75b6422e15bbd064dc2c1d3cd1b1c4e48943394f0721f5e6e15ebb8f3cca633"

headers = {
    'Content-Type': "",
    'referer': 'https://drive.uc.cn/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Cookie': UCCookie
}
headerx = {
  'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/2.5.20 Chrome/100.0.4896.160 Electron/18.3.5.12-a038f7b798 Safari/537.36 Channel/pckk_other_ch",
  'referer': "https://pan.quark.cn/",
  'Cookie': QuarkCookie
}
headerz = {
    'User-Agent': "netdisk;1.4.2;22021211RC;android-android;12;JSbridge4.4.0;jointBridge;1.1.0;",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Referer': "https://pan.baidu.com",
    'Cookie': BaiduCookie
}
header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
}
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
        result = {"class": [{"type_id": "1", "type_name": "多多电影"},
                            {"type_id": "2", "type_name": "多多剧集"},
                            {"type_id": "3", "type_name": "综艺"},
                            {"type_id": "4", "type_name": "动漫"},
                            {"type_id": "5", "type_name": "短剧"},
                            {"type_id": "20", "type_name": "纪录片"}
                            ],
                  }

        return result
    def homeVideoContent(self):
        pass

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []
        url = f'{xurl}/index.php/vod/show/id/{cid}.html'
        res = requests.get(url=url, headers=header)
        res.encoding = "utf-8"
        doc = BeautifulSoup(res.text, 'lxml')
        soups = doc.find_all('div', class_='module-item')
        for i in soups:
            id = i.find('a')['href']
            match = re.search(r'/id/(\d+)', id)
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
        play_kurl = []
        play_urls = []
        did = ids[0]
        url = f'{xurl}/index.php/vod/detail/id/{did}.html'
        res = requests.get(url=url, headers=header)
        res.encoding = "utf-8"
        doc = BeautifulSoup(res.text, 'lxml')
        soups = doc.find('div', class_='video-info')
        # print(soups)
        name = soups.find('h1').text
        actors_title = soups.find('span', class_='video-info-itemtitle', string='主演：')
        if actors_title:
            actors_container = actors_title.find_next('div', class_='video-info-item')
            actor_links = actors_container.find_all('a', target='_blank')
            actors = ' / '.join([actor.text.strip() for actor in actor_links])
        director = soups.find('span', class_='video-info-items')
        content = soups.find('p').text
        remarks = soups.find('div', class_='tag-link').text.replace('\n', '')
        tag_links = soups.find_all('a', class_='tag-link')
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
                play_form = '$$$'.join(sources)
            row = kjson.find('div', class_='scroll-box-y')
            if row:
                kurl = row.find_all('div', class_='module-row-info')
                for k in kurl:
                    urls = k.find('p').text.strip()
                    id = 'http://sspa8.top:8100/api/vips.php?url=' + urls
                    res = requests.get(url=id, headers=header)
                    kjson = res.json()
                    if 'list' in kjson and kjson['list']:
                        for i in kjson['list']:
                            play_urls = i['vod_play_url']
                            play_kurl.append(''.join(play_urls).rstrip('#'))
                play_url1 = '$$$'.join(play_kurl)
            video = {
                "vod_id": did,
                "vod_name": name,
                "vod_actor": actors,
                "vod_director": director.text if director else "",
                "vod_content": '臻彩视界',
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
        if 'baidu' in id:
            uid = "http://sspa8.top:8100/api/%E7%99%BE%E5%BA%A6/jx.php?url=" + id
            res = requests.get(url=uid, headers=headerz)
            if res.status_code == 200:
                kjson = res.json()
                url = kjson['url']
                result = {}
                result["parse"] = 0
                result["playUrl"] = ''
                result["url"] = url
                result["header"] = headerz
                return result
        elif 'quark' in id:
            bid = "http://sspa8.top:8100/api/vips.php?url=" + id
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
        elif 'UC' in id:
                id = "http://sspa8.top:8100/api/vips.php?url=" + id
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
        url = f'{xurl}/index.php/vod/search/wd/{key}.html'
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
            match = re.search(r'/id/(\d+)', id)
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