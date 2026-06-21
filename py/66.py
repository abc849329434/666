import re
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 站点配置
RULE = {
    "title": "爱追剧",
    "type": "影视",
    "host": "https://www.aizju.com",
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.aizju.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    },
    "encoding": "utf-8",
    "timeout": 10,  # 延长超时时间
    "searchUrl": "/vodsearch/-------------.html?wd={}&submit="
}

# 工具函数：发送网络请求（添加重试）
def request_url(url, headers=None, retry=2):
    headers = headers or RULE["headers"]
    session = requests.Session()
    session.headers.update(headers)
    for _ in range(retry):
        try:
            resp = session.get(url, timeout=RULE["timeout"], allow_redirects=True)
            resp.encoding = RULE["encoding"] if resp.encoding == "ISO-8859-1" else resp.apparent_encoding
            return resp.text
        except Exception as e:
            print(f"请求重试 {_+1} 次失败: {e}")
    return ""

# 工具函数：安全获取元素文本/属性
def safe_extract(soup, selector, attr="text", default=""):
    elem = soup.select_one(selector)
    if not elem:
        return default
    if attr == "text":
        return elem.get_text(strip=True, separator=" ")
    return elem.get(attr, default)

# 工具函数：补全相对链接
def full_url(path):
    if path.startswith(("http://", "https://")):
        return path
    # 处理带参数的相对链接
    return urllib.parse.urljoin(RULE["host"], path.lstrip("/"))

# 解析播放地址
def play_parse(play_url):
    html = request_url(play_url)
    if not html:
        return play_url
    # 兼容不同的播放器链接格式
    match = re.search(r'src=["\']/player/mui-player\.php\?([^"\']+)["\']', html)
    if not match:
        return play_url
    kcode = match.group(1)
    kurl_list = kcode.split(",")
    if len(kurl_list) < 2:
        return play_url
    kurl = kurl_list[1]
    if kurl and (".m3u8" in kurl or ".mp4" in kurl):
        return kurl if kurl.startswith("http") else full_url(kurl)
    return play_url

# 搜索功能（优化选择器）
def search(keyword):
    search_path = RULE["searchUrl"].format(urllib.parse.quote(keyword))
    search_url = full_url(search_path)
    print(f"搜索地址: {search_url}")  # 调试用
    html = request_url(search_url)
    if not html:
        print("搜索页面加载失败")
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    # 放宽选择器匹配条件，兼容可能的类名变化
    items = soup.select(".hl-item-div, .hl-list-item, div[class*='item']")
    results = []
    for item in items:
        a_tag = item.select_one("a")
        if not a_tag:
            continue
        title = safe_extract(a_tag, "", "title") or safe_extract(a_tag, "", "text")
        cover = safe_extract(a_tag, "", "data-original") or safe_extract(a_tag, "img", "src")
        remark = safe_extract(item, ".hl-lc-1 .remarks, .remarks, span[class*='remark']")
        href = safe_extract(a_tag, "", "href")
        
        if not title or not href:
            continue
        results.append({
            "title": title,
            "cover": full_url(cover),
            "remark": remark,
            "url": full_url(href)
        })
    return results

# 解析详情页（优化选择器）
def parse_detail(detail_url):
    print(f"解析详情页: {detail_url}")  # 调试用
    html = request_url(detail_url)
    if not html:
        print("详情页加载失败")
        return {}
    
    soup = BeautifulSoup(html, "html.parser")
    vod = {}
    vod["vod_id"] = detail_url.split("/")[-1].split(".")[0] if "/" in detail_url else ""
    vod["vod_name"] = safe_extract(soup, "h1, h2, .title")
    
    # 解析类型、状态等信息（兼容不同的标签结构）
    info_items = soup.select("ul li, .info li, div[class*='info'] span")
    info_dict = {}
    for item in info_items:
        text = item.get_text(strip=True, separator=" ")
        if "：" not in text:
            continue
        key, value = text.split("：", 1)
        info_dict[key] = value
    
    vod["type_name"] = info_dict.get("类型", "").replace("/", " ")
    vod["vod_remarks"] = info_dict.get("状态", "")
    vod["vod_year"] = info_dict.get("年份", "")
    vod["vod_area"] = info_dict.get("地区", "")
    vod["vod_director"] = info_dict.get("导演", "")
    vod["vod_actor"] = info_dict.get("主演", "")
    vod["vod_content"] = safe_extract(soup, ".hl-col-xs-12.blurb, .blurb, .intro", "text").replace("简介：", "")
    vod["vod_pic"] = full_url(safe_extract(soup, "a img, .cover img", "src") or safe_extract(soup, "a", "data-original"))

    # 解析播放线路
    tabs = soup.select(".hl-plays-from .hl-tabs a, .tabs a, .play-tabs a")
    vod["vod_play_from"] = "$$$".join([safe_extract(t, "", "text") for t in tabs])

    # 解析播放集数
    play_lists = soup.select(".hl-plays-list, .play-list, div[class*='plays-list']")
    klists = []
    for pl in play_lists:
        links = pl.select("a")
        klist = []
        for link in links:
            text = safe_extract(link, "", "text")
            href = safe_extract(link, "", "href")
            if "APP播放" not in text and href:
                klist.append(f"{text}${full_url(href)}")
        klists.append("#".join(klist))
    vod["vod_play_url"] = "$$$".join(klists)
    return vod

# 测试代码
if __name__ == "__main__":
    # 测试搜索（建议先搜热门影视，比如"庆余年2"）
    keyword = input("请输入要搜索的影视名称: ").strip() or "庆余年2"
    search_res = search(keyword)
    
    if not search_res:
        print("未搜索到任何结果，请检查关键词或站点是否可访问")
    else:
        print(f"\n共搜索到 {len(search_res)} 条结果：")
        for idx, item in enumerate(search_res, 1):
            print(f"{idx}. 标题: {item['title']} | 链接: {item['url']}")
        
        # 解析第一个结果的详情
        choice = input("\n是否解析第一个结果的详情？(y/n): ").strip().lower()
        if choice == "y":
            detail_res = parse_detail(search_res[0]["url"])
            print("\n详情解析结果：")
            for k, v in detail_res.items():
                if v:
                    print(f"{k}: {v}")
            
            # 测试播放地址解析
            if "vod_play_url" in detail_res and detail_res["vod_play_url"]:
                first_play = detail_res["vod_play_url"].split("$$$")[0].split("#")[0]
                if "$" in first_play:
                    play_name, play_url = first_play.split("$", 1)
                    real_url = play_parse(play_url)
                    print(f"\n{play_name} 真实播放地址: {real_url}")
