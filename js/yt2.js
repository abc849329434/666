// 小心儿悠悠 - 带验证绕过版本
import { Crypto, _ } from 'assets://js/lib/cat.js'

const FIXED_CONFIG = {
    host: 'http://cs119.lyyytv.cn',
    cmskey: 'z0afJ9wfCMEuLwDMJCFHwFQmaxCzC5zM',
    RawPlayUrl: 0
};

// 增强的请求头，模拟真实浏览器
const headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
};

// 存储cookies和token的全局变量
let globalCookies = '';
let antiAntiCrawlerEnabled = true;

// 反反爬虫功能
function enableAntiAntiCrawler() {
    antiAntiCrawlerEnabled = true;
}

function disableAntiAntiCrawler() {
    antiAntiCrawlerEnabled = false;
}

// 生成随机IP
function getRandomIP() {
    return `112.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
}

// 生成随机User-Agent
function getRandomUA() {
    const uaList = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
    ];
    return uaList[Math.floor(Math.random() * uaList.length)];
}

// 增强的请求函数，带验证绕过
async function enhancedRequest(reqUrl, options = {}) {
    const {
        ua = null,
        timeout = 30000,
        retryCount = 3,
        method = 'get',
        data = null,
        referer = null
    } = options;
    
    let currentHeaders = { ...headers };
    
    // 添加反爬虫头信息
    if (antiAntiCrawlerEnabled) {
        currentHeaders['X-Forwarded-For'] = getRandomIP();
        currentHeaders['X-Real-IP'] = getRandomIP();
        currentHeaders['X-Requested-With'] = 'XMLHttpRequest';
        currentHeaders['User-Agent'] = getRandomUA();
        
        if (referer) {
            currentHeaders['Referer'] = referer;
        }
        
        // 添加cookies
        if (globalCookies) {
            currentHeaders['Cookie'] = globalCookies;
        }
    }
    
    // 合并自定义UA
    if (ua) {
        currentHeaders['User-Agent'] = ua['User-Agent'] || ua;
    }
    
    for (let attempt = 0; attempt < retryCount; attempt++) {
        try {
            const requestOptions = {
                method: method,
                headers: currentHeaders,
                timeout: timeout,
                data: data
            };
            
            let res = await req(reqUrl, requestOptions);
            
            // 保存cookies
            if (res.headers && res.headers['set-cookie']) {
                globalCookies = res.headers['set-cookie'];
            } else if (res.headers && res.headers['Set-Cookie']) {
                globalCookies = res.headers['Set-Cookie'];
            }
            
            return res;
            
        } catch (error) {
            console.log(`请求失败，第${attempt + 1}次重试:`, error);
            
            if (attempt === retryCount - 1) {
                throw error;
            }
            
            // 等待一段时间后重试
            await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
        }
    }
}

function lvdou(text) {
    try {
        const keyStr = FIXED_CONFIG.cmskey;
        const original_text = text;
        const url_prefix = "lvdou+";
        
        if (!original_text.startsWith(url_prefix)) {
            return original_text;
        }
        
        const ciphertext_b64 = original_text.substring(url_prefix.length);
        const key = Crypto.enc.Utf8.parse(keyStr.substring(0, 16));
        const iv = Crypto.enc.Utf8.parse(keyStr.substring(keyStr.length - 16));
        
        const decrypted = Crypto.AES.decrypt(ciphertext_b64, key, {
            iv: iv,
            mode: Crypto.mode.CBC,
            padding: Crypto.pad.Pkcs7
        });
        
        return decrypted.toString(Crypto.enc.Utf8);
    } catch (e) {
        return text;
    }
}

function completeUrl(url) {
    if (!url || typeof url !== 'string') return url;
    
    if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
    }
    
    if (url.startsWith('//')) {
        return 'http:' + url;
    }
    
    if (url.startsWith('/')) {
        return FIXED_CONFIG.host + url;
    }
    
    if (url.includes('.m3u8') || url.includes('.mp4')) {
        return FIXED_CONFIG.host + '/' + url;
    }
    
    return url;
}

// 使用增强的请求函数
async function request(reqUrl, ua, timeout = 60000) {
    try {
        const res = await enhancedRequest(reqUrl, {
            ua: ua,
            timeout: timeout,
            referer: FIXED_CONFIG.host
        });
        return res.content;
    } catch (error) {
        console.error('请求错误:', error);
        return null;
    }
}

async function home(filter) {
    try {
        let url = FIXED_CONFIG.host + "/api.php/app/nav?token=";
        const json = await request(url, headers);
        if (!json) {
            return JSON.stringify({ class: [] });
        }
        
        const obj = JSON.parse(json);
        let jsonArray = obj.list || (obj.data && obj.data.list) || obj.data;
        const result = { class: [] };
        
        if (jsonArray != null) {
            for (let i = 0; i < jsonArray.length; i++) {
                const jObj = jsonArray[i];
                const typeName = jObj.type_name;
                const typeId = jObj.type_id;
                const newCls = {
                    type_id: typeId,
                    type_name: typeName,
                };
                const typeExtend = jObj.type_extend;
                if (filter) {
                    const filterArr = [];
                    if (typeExtend) {
                        for (let key in typeExtend) {
                            if (key === "class" || key === "area" || key === "lang" || key === "year") {
                                const jOne = {
                                    key: key,
                                    name: key === "class" ? "类型" : 
                                          key === "area" ? "地区" : 
                                          key === "lang" ? "语言" : "年份",
                                    value: [],
                                };
                                const values = typeExtend[key].split(',');
                                jOne.value.push({ n: "全部", v: "" });
                                for (let val of values) {
                                    jOne.value.push({ n: val, v: val });
                                }
                                filterArr.push(jOne);
                            }
                        }
                    }
                    filterArr.push({
                        key: "排序",
                        name: "排序",
                        value: [
                            { n: "最新", v: "time" },
                            { n: "最热", v: "hits" },
                            { n: "评分", v: "score" }
                        ]
                    });
                    if (!result.hasOwnProperty("filters")) {
                        result.filters = {};
                    }
                    result.filters[typeId] = filterArr;
                }
                result.class.push(newCls);
            }
        }
        return JSON.stringify(result);
    } catch (e) {
        console.error('首页错误:', e);
        return JSON.stringify({ class: [] });
    }
}

async function homeVod() {
    try {
        const url = FIXED_CONFIG.host + "/api.php/app/index_video?token=";
        const json = await request(url, headers);
        if (!json) {
            return JSON.stringify({ list: [] });
        }
        
        const obj = JSON.parse(json);
        const videos = [];
        
        if (obj.list && Array.isArray(obj.list)) {
            for (let i = 0; i < obj.list.length; i++) {
                const section = obj.list[i];
                if (section.vlist && Array.isArray(section.vlist)) {
                    for (let j = 0; j < section.vlist.length; j++) {
                        const vObj = section.vlist[j];
                        videos.push({
                            vod_id: vObj.vod_id,
                            vod_name: vObj.vod_name,
                            vod_pic: vObj.vod_pic,
                            vod_remarks: vObj.vod_remarks || vObj.vod_time
                        });
                    }
                } else {
                    videos.push({
                        vod_id: section.vod_id,
                        vod_name: section.vod_name,
                        vod_pic: section.vod_pic,
                        vod_remarks: section.vod_remarks || section.vod_time
                    });
                }
            }
        }
        
        return JSON.stringify({ list: videos });
    } catch (e) {
        console.error('首页推荐错误:', e);
        return JSON.stringify({ list: [] });
    }
}

async function category(tid, pg, filter, extend) {
    try {
        let url = `${FIXED_CONFIG.host}/api.php/app/video?tid=${tid}&class=${extend?.class||''}&area=${extend?.area||''}&lang=${extend?.lang||''}&year=${extend?.year||''}&by=${extend?.排序||'time'}&limit=18&pg=${pg}`;
        const json = await request(url, headers);
        if (!json) {
            return JSON.stringify({
                page: pg,
                pagecount: 0,
                list: []
            });
        }
        
        const obj = JSON.parse(json);
        const videos = [];
        const jsonArray = obj.list || (obj.data && obj.data.list) || obj.data;
        if (jsonArray) {
            for (let i = 0; i < jsonArray.length; i++) {
                const vObj = jsonArray[i];
                videos.push({
                    vod_id: vObj.vod_id,
                    vod_name: vObj.vod_name,
                    vod_pic: vObj.vod_pic,
                    vod_remarks: vObj.vod_remarks
                });
            }
        }
        return JSON.stringify({
            page: pg,
            pagecount: obj.pagecount || 1000,
            list: videos
        });
    } catch (e) {
        console.error('分类错误:', e);
        return JSON.stringify({
            page: pg,
            pagecount: 0,
            list: []
        });
    }
}

async function detail(ids) {
    try {
        const url = FIXED_CONFIG.host + "/api.php/app/video_detail?id=" + ids;
        const json = await request(url, headers);
        if (!json) {
            return JSON.stringify({ list: [] });
        }
        
        const obj = JSON.parse(json);
        const data = obj.data || obj;
        const vod = {
            vod_id: data.vod_id || ids,
            vod_name: data.vod_name,
            vod_pic: data.vod_pic,
            vod_remarks: data.vod_remarks,
            vod_actor: data.vod_actor,
            vod_director: data.vod_director,
            vod_content: data.vod_content,
            vod_play_from: "",
            vod_play_url: ""
        };
        
        const playFrom = [];
        const playUrl = [];
        
        if (data.vod_url_with_player) {
            for (let item of data.vod_url_with_player) {
                let lineName = item.name || item.code || '';
                playFrom.push(lineName);
                
                let playUrlItem = item.url || '';
                
                if (playUrlItem.includes('#')) {
                    const urls = playUrlItem.split('#');
                    const decryptedUrls = [];
                    
                    for (let url of urls) {
                        if (url && url.trim()) {
                            if (url.includes('$')) {
                                const parts = url.split('$', 2);
                                if (parts.length === 2) {
                                    const episodeName = parts[0].trim();
                                    let playAddress = parts[1].trim();
                                    
                                    playAddress = lvdou(playAddress);
                                    playAddress = completeUrl(playAddress);
                                    
                                    decryptedUrls.push(episodeName + '$' + playAddress);
                                } else {
                                    decryptedUrls.push(url);
                                }
                            } else {
                                let decryptedUrl = lvdou(url);
                                decryptedUrl = completeUrl(decryptedUrl);
                                decryptedUrls.push(decryptedUrl);
                            }
                        }
                    }
                    playUrlItem = decryptedUrls.join('#');
                } else {
                    playUrlItem = lvdou(playUrlItem);
                    playUrlItem = completeUrl(playUrlItem);
                }
                
                playUrl.push(playUrlItem);
            }
        }
        
        if (playUrl.length === 0 && data.vod_play_url) {
            const playUrls = data.vod_play_url.split('$$$');
            const playFroms = data.vod_play_from ? data.vod_play_from.split('$$$') : ['默认'];
            
            for (let i = 0; i < playFroms.length; i++) {
                playFrom.push(playFroms[i]);
                if (i < playUrls.length) {
                    let urlItem = playUrls[i];
                    if (urlItem.includes('#')) {
                        const episodes = urlItem.split('#');
                        const processedEpisodes = [];
                        
                        for (let ep of episodes) {
                            if (ep.includes('$')) {
                                const epParts = ep.split('$', 2);
                                if (epParts.length === 2) {
                                    let epUrl = lvdou(epParts[1]);
                                    epUrl = completeUrl(epUrl);
                                    processedEpisodes.push(epParts[0] + '$' + epUrl);
                                } else {
                                    processedEpisodes.push(ep);
                                }
                            } else {
                                let epUrl = lvdou(ep);
                                epUrl = completeUrl(epUrl);
                                processedEpisodes.push(epUrl);
                            }
                        }
                        playUrl.push(processedEpisodes.join('#'));
                    } else {
                        let epUrl = lvdou(urlItem);
                        epUrl = completeUrl(epUrl);
                        playUrl.push(epUrl);
                    }
                }
            }
        }
        
        vod.vod_play_from = playFrom.join("$$$");
        vod.vod_play_url = playUrl.join("$$$");
        
        return JSON.stringify({ list: [vod] });
    } catch (e) {
        console.error('详情页错误:', e);
        return JSON.stringify({ list: [] });
    }
}

function checkPlayUrl(content) {
    if (!content) return false;
    const pattern = /(https?:\/\/[^\s]+|m3u8|\.mp4|\.flv|\.avi|\.mkv|\.m3u8)/i;
    return pattern.test(content);
}

async function getRawUrl(original_url) {
    try {
        const response = await enhancedRequest(original_url, {
            timeout: 20000,
            method: 'get'
        });
        
        if (response.status >= 300 && response.status < 400) {
            const redirect_location = response.headers['Location'] || response.headers['location'];
            if (redirect_location) {
                if (redirect_location.startsWith('http')) {
                    return redirect_location;
                } else {
                    const baseUrl = original_url.split('/').slice(0, 3).join('/');
                    return baseUrl + redirect_location;
                }
            }
        }
        return original_url;
    } catch (e) {
        return original_url;
    }
}

async function play(flag, id, vipFlags) {
    try {
        let finalUrl = id;
        let jx = 0;
        let parse = 0;
        
        console.log('原始播放ID:', id);
        
        finalUrl = completeUrl(finalUrl);
        console.log('补全后URL:', finalUrl);
        
        if (checkPlayUrl(finalUrl)) {
            if (FIXED_CONFIG.RawPlayUrl === 1) {
                finalUrl = await getRawUrl(finalUrl);
                console.log('获取原始URL后:', finalUrl);
            }
            parse = 0;
        } else if (/(?:www\.iqiyi|v\.qq|v\.youku|www\.mgtv|www\.bilibili|\.m3u8)\.com|m3u8/i.test(finalUrl)) {
            jx = 1;
            parse = 1;
        }
        
        if (finalUrl.includes('.m3u8')) {
            jx = 1;
            parse = 1;
        }
        
        console.log('最终播放参数:', { jx, parse, url: finalUrl });
        
        return JSON.stringify({
            jx: jx,
            playUrl: '',
            parse: parse,
            url: finalUrl,
            header: headers
        });
        
    } catch (e) {
        console.error('播放错误:', e);
        try {
            const completedUrl = completeUrl(id);
            return JSON.stringify({
                jx: 0,
                playUrl: '',
                parse: 0,
                url: completedUrl
            });
        } catch (error) {
            return JSON.stringify({
                jx: 0,
                playUrl: '',
                parse: 0,
                url: id
            });
        }
    }
}

async function search(key, quick) {
    try {
        const url = FIXED_CONFIG.host + "/api.php/app/search?text=" + encodeURIComponent(key) + "&pg=1";
        const json = await request(url, headers);
        if (!json) {
            return JSON.stringify({ list: [] });
        }
        
        const obj = JSON.parse(json);
        const jsonArray = obj.list || (obj.data && obj.data.list) || obj.data;
        const videos = [];
        if (jsonArray) {
            for (let i = 0; i < jsonArray.length; i++) {
                const vObj = jsonArray[i];
                videos.push({
                    vod_id: vObj.vod_id,
                    vod_name: vObj.vod_name,
                    vod_pic: vObj.vod_pic,
                    vod_remarks:vObj.vod_remarks
                });
            }
        }
        return JSON.stringify({ list: videos });
    } catch (error) {
        console.error('搜索错误:', error);
        return JSON.stringify({ list: [] });
    }
}

// 新增：验证绕过控制函数
function setAntiCrawler(enabled) {
    antiAntiCrawlerEnabled = enabled;
    return `反反爬虫功能已${enabled ? '开启' : '关闭'}`;
}

// 新增：清除cookies
function clearCookies() {
    globalCookies = '';
    return 'Cookies已清除';
}

export function __jsEvalReturn() {
    return {
        home: home,
        homeVod: homeVod,
        category: category,
        detail: detail,
        play: play,
        search: search,
        setAntiCrawler: setAntiCrawler, // 导出控制函数
        clearCookies: clearCookies      // 导出清除cookies函数
    };
}
