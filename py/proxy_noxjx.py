import requests
import json
from urllib.parse import urlparse, parse_qs, unquote, quote

class NoxProxyParser:
    def __init__(self):
        # 1. 这里填入你图片中的配置信息
        self.config = {
            "追片喵": {
                "host": "https://svip.2video.cc",
                "headers": {
                    "userId": "xxxx", # 替换为你的真实ID
                    "verCode": "56",
                    "verName": "1.2.6",
                    "deviceId": "xxxxxxx",
                    "package": "com.ds.wlss",
                    "signature": "70:DF:B1:2A:AE:C3:E3:73:6E:23:0F:67:B9:3B:C5:63:2D:EA:2A:2C:9E:9D:52:82:1D:3F:3C:3C:B9:10:9E:EE",
                    "User-Agent": "okhttp/3.12.0",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            }
        }

    def parse(self, proxy_url):
        """
        核心解析函数
        """
        try:
            # 兼容处理：将自定义协议转为标准格式以便解析参数
            if proxy_url.startswith("Proxy://"):
                proxy_url = proxy_url.replace("Proxy://", "http://", 1)
            
            parsed_url = urlparse(proxy_url)
            # 获取所有参数
            query_params = parse_qs(parsed_url.query)
            params = {k: v[0] for k, v in query_params.items()}

            source_name = params.get("source")
            target_url = params.get("url")

            if not source_name or not target_url:
                return {"error": "缺少参数 source 或 url"}

            # 检查是否有对应站点的配置
            if source_name not in self.config:
                return {"error": f"配置中未找到站点: {source_name}"}

            site_config = self.config[source_name]
            
            # --- 关键逻辑：构造最终请求 ---
            # 如果 url 参数是完整的 https 链接（如芒果TV），我们需要将其作为参数传给接口
            # 假设该接口的解析路径是 /api/parse (请根据实际抓包修改)
            api_endpoint = f"{site_config['host']}/api/video/parse" 
            
            payload = {
                "url": target_url,  # 这里的 target_url 是完整的芒果TV地址
                "type": params.get("type", "nox_jx"),
                "siteKey": params.get("siteKey", "")
            }

            print(f"[*] 正在通过 [{source_name}] 解析链接: {target_url}")

            # 发起 POST 或 GET 请求 (根据该站点的 API 习惯，通常是 POST)
            response = requests.post(
                api_endpoint, 
                data=payload, 
                headers=site_config["headers"], 
                timeout=15
            )

            if response.status_code == 200:
                return response.json() # 返回解析后的 JSON 数据（包含播放地址）
            else:
                return {"error": f"服务器返回错误: {response.status_code}", "detail": response.text}

        except Exception as e:
            return {"error": f"解析发生异常: {str(e)}"}

# --- 使用示例 ---
if __name__ == "__main__":
    parser = NoxProxyParser()
    
    # 模拟你的输入（注意：实际使用时，url后面的链接最好手动进行一次 urlencode）
    test_link = "Proxy://do=py&siteKey=proxy_noxjx&type=nox_jx&source=追片喵&url=https://www.mgtv.com/b/613743/23658804.html"
    
    result = parser.parse(test_link)
    
    print("\n--- 解析结果 ---")
    print(json.dumps(result, indent=4, ensure_ascii=False))
