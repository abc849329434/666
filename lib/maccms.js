import {
    Crypto,
    _
} from 'assets://js/lib/cat.js'
let host = '';
let header = {
    'User-Agent': 'okhttp/3.12.11'
};
let siteKey = '';
let siteType = '';
let siteJx = '';
// 线路名称映射字典
let lineNameMapping = {
    'youku': '优酷',
    'qq': '腾讯',
    'qiyi': '爱奇艺',
    'mgtv': '芒果TV',
    'sohu': '搜狐',
    'letv': '乐视',
    'pptv': 'PP',
    'bilibili': '哔哩哔哩',
    'wasu': '华数TV',
    'migu': '咪咕',
    'tt': '天堂',
    '4K': '4K',
    '2K': '2K',
    'bfzy': '暴风',
    '1080zyk': '优质',
    'kuaikan': '快看',
    'lz': '量子',
    'ff': '非凡',
    'fs': '飞速',
    'ry': '如意',
    'haiwaikan': '海外看',
    'gs': '光速',
    'zuida': '最大',
    'bj': '八戒',
    'sn': '索尼',
    'wolong': '卧龙',
    'xl': '新浪',
    'yh': '樱花',
    'tk': '天空',
    'js': '极速',
    'wj': '无尽',
    'sd': '闪电',
    'kc': '快车',
    'jinying': '金鹰',
    'tp': '淘片',
    'le': '鱼乐',
    'db': '百度',
    'tom': '番茄',
    'uk': 'U酷',
    'ik': '爱坤',
    'hn': '红牛',
    '68zy_': '68',
    'kd': '酷点',
    'bdx': '北斗星',
    'qh': '奇虎',
    'hh': '豪华',
    'kb': '快播',
    '原始名称': '修改名称'
};
// 线路排序基准
let lineOrder = ["4K", "2K", "优酷", "腾讯", "爱奇艺", "芒果TV", "自定义线路1"];
// 排除线路配置
let lineExclude = ["广告", "测试", "备用"];
async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    host = cfg.ext; // 初始赋值
    if (cfg.ext && typeof cfg.ext === 'object') {
        // 优先使用 host 字段
        if (cfg.ext.hasOwnProperty('host')) {
            host = cfg.ext.host;
        }
        // 若 host 不存在，尝试使用 url 字段
        else if (cfg.ext.hasOwnProperty('url')) {
            host = cfg.ext.url;
        }
        siteJx = cfg.ext;
        if (cfg.ext.hasOwnProperty('lineMapping')) {
            lineNameMapping = {
                ...lineNameMapping,
                ...cfg.ext.lineMapping
            };
        }
        if (cfg.ext.hasOwnProperty('lineOrder')) {
            lineOrder = cfg.ext.lineOrder;
        }
        if (cfg.ext.hasOwnProperty('lineExclude')) {
            lineExclude = cfg.ext.lineExclude;
        }
    }
};

async function request(reqUrl, ua, timeout = 60000) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: ua ? ua : {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        },
        timeout: timeout,
    });
    return res.content;
}
// 分类接口
async function home(filter) {
    try {
        const url = host;
        const json = await request(url, getHeaders(url));
        const obj = JSON.parse(json);
        const result = {
            class: []
        };
        const uniqueClasses = {};
        if (obj.class && Array.isArray(obj.class)) {
            for (const item of obj.class) {
                const typeName = item.type_name;
                if (isBan(typeName)) continue;
                if (!uniqueClasses[typeName]) {
                    uniqueClasses[typeName] = item;
                }
            }
            result.class = Object.values(uniqueClasses).map(item => ({
                type_id: item.type_id,
                type_name: item.type_name
            }));
        }
        return JSON.stringify(result);
    } catch (e) {
        return JSON.stringify({
            class: []
        });
    }
}
// 首页推荐
async function homeVod() {
    try {
        const url = `${host}?ac=videolist&t=1&pg=1`;
        const json = await request(url, getHeaders(url));
        const obj = JSON.parse(json);
        const videos = [];
        if (obj.list && Array.isArray(obj.list)) {
            for (const item of obj.list) {
                videos.push({
                    vod_id: item.vod_id,
                    vod_name: item.vod_name,
                    vod_pic: item.vod_pic || "",
                    vod_remarks: item.vod_remarks || ""
                });
            }
        }
        return JSON.stringify({
            list: videos
        });
    } catch (e) {
        return "";
    }
}
// 分类列表
async function category(tid, pg, filter, extend) {
    try {
        const url = `${host}?ac=videolist&t=${tid}&pg=${pg}`;
        const json = await request(url, getHeaders(url));
        const obj = JSON.parse(json);
        const videos = [];
        if (obj.list && Array.isArray(obj.list)) {
            for (const item of obj.list) {
                videos.push({
                    vod_id: item.vod_id,
                    vod_name: item.vod_name,
                    vod_pic: item.vod_pic || "",
                    vod_remarks: item.vod_remarks || ""
                });
            }
        }
        return JSON.stringify({
            page: pg,
            pagecount: obj.pagecount || 1,
            limit: obj.limit || 20,
            total: obj.total || 0,
            list: videos
        });
    } catch (e) {
        return "";
    }
}
// 详情接口 - 修复线路排序逻辑
async function detail(ids) {
    try {
        const url = `${host}?ac=detail&ids=${ids}`;
        const json = await request(url, getHeaders(url));
        const obj = JSON.parse(json);
        const vod = obj.list && obj.list[0] ? obj.list[0] : {};

        // 基础信息
        const resultVod = {
            vod_id: vod.vod_id || ids,
            vod_name: vod.vod_name || "",
            vod_pic: vod.vod_pic || "",
            type_name: vod.type_name || "",
            vod_year: vod.vod_year || "",
            vod_area: vod.vod_area || "",
            vod_remarks: vod.vod_remarks || "",
            vod_actor: vod.vod_actor || "",
            vod_director: vod.vod_director || "",
            vod_content: vod.vod_content || "",
            vod_play_from: vod.vod_play_from || "",
            vod_play_url: vod.vod_play_url || ""
        };

        // 处理播放线路
        if (resultVod.vod_play_from && resultVod.vod_play_url) {
            const sources = resultVod.vod_play_from.split('$$$');
            const urls = resultVod.vod_play_url.split('$$$');

            // 收集所有有效线路
            const allLines = [];
            for (let i = 0; i < sources.length; i++) {
                const sourceLines = sources[i].split('#');
                const sourceUrls = urls[i].split('#');

                for (let j = 0; j < sourceLines.length; j++) {
                    const lineName = sourceLines[j];
                    const lineUrl = sourceUrls[j];

                    // 1. 映射线路名称
                    let mappedName = lineName;
                    for (const [key, value] of Object.entries(lineNameMapping)) {
                        if (lineName.toLowerCase().includes(key.toLowerCase())) {
                            mappedName = value;
                            break;
                        }
                    }

                    // 2. 检查是否排除
                    let isExcluded = false;
                    for (const ex of lineExclude) {
                        if (mappedName.toLowerCase().includes(ex.toLowerCase())) {
                            isExcluded = true;
                            break;
                        }
                    }
                    if (isExcluded) continue;

                    allLines.push({
                        name: mappedName,
                        url: lineUrl,
                        sourceIndex: i // 保留原始源索引用于分组
                    });
                }
            }

            // 3. 按排序基准排序
            allLines.sort((a, b) => {
                const orderA = getLineOrder(a.name);
                const orderB = getLineOrder(b.name);
                // 先按排序优先级
                if (orderA !== orderB) {
                    return orderA - orderB;
                }
                // 再按名称拼音
                return a.name.localeCompare(b.name, 'zh-CN');
            });

            // 4. 重新分组组装
            const sourceMap = new Map();
            allLines.forEach(line => {
                if (!sourceMap.has(line.sourceIndex)) {
                    sourceMap.set(line.sourceIndex, {
                        names: [],
                        urls: []
                    });
                }
                const group = sourceMap.get(line.sourceIndex);
                group.names.push(line.name);
                group.urls.push(line.url);
            });

            // 5. 转换为最终格式
            const sortedSources = [];
            const sortedUrls = [];
            sourceMap.forEach(group => {
                sortedSources.push(group.names.join('#'));
                sortedUrls.push(group.urls.join('#'));
            });

            resultVod.vod_play_from = sortedSources.join('$$$');
            resultVod.vod_play_url = sortedUrls.join('$$$');
        }

        return JSON.stringify({
            list: [resultVod]
        });
    } catch (e) {
        return JSON.stringify({
            list: []
        });
    }
}
// 获取线路排序优先级
function getLineOrder(lineName) {
    const lowerName = lineName.toLowerCase();
    // 精确匹配优先
    const exactIndex = lineOrder.findIndex(order => order.toLowerCase() === lowerName);
    if (exactIndex !== -1) {
        return exactIndex;
    }
    // 包含匹配次之
    for (let i = 0; i < lineOrder.length; i++) {
        if (lowerName.includes(lineOrder[i].toLowerCase())) {
            return i;
        }
    }
    return 999; // 未匹配的线路放在最后
}
// 播放接口
async function play(flag, id, vipFlags) {
    try {
        let parseUrls = siteJx[flag] || siteJx['*'] || [];
        if (parseUrls.length > 0) {
            for (const parseUrl of parseUrls) {
                if (!parseUrl) continue;
                const playUrl = parseUrl + id;
                const content = await request(playUrl, null, 10000);
                try {
                    const tryJson = JSON.parse(content);
                    if (tryJson.url) {
                        return JSON.stringify({
                            url: tryJson.url,
                            header: tryJson.header ? JSON.stringify(tryJson.header) : ""
                        });
                    }
                } catch (error) {}
            }
        }
        return JSON.stringify({
            parse: 0,
            url: id
        });
    } catch (e) {
        return JSON.stringify({
            parse: 0,
            url: id
        });
    }
}
// 搜索接口
async function search(key, quick) {
    try {
        const url = `${host}?ac=videolist&wd=${encodeURIComponent(key)}&pg=1`;
        const json = await request(url, getHeaders(url));
        const obj = JSON.parse(json);
        const videos = [];
        if (obj.list && Array.isArray(obj.list)) {
            for (const item of obj.list) {
                videos.push({
                    vod_id: item.vod_id,
                    vod_name: item.vod_name,
                    vod_pic: item.vod_pic || "",
                    vod_remarks: item.vod_remarks || ""
                });
            }
        }
        return JSON.stringify({
            list: videos
        });
    } catch (error) {
        return "";
    }
}
// 敏感分类过滤
function isBan(key) {
    return key === "伦理" || key === "情色" || key === "福利";
}
// 获取请求头
function getHeaders(URL) {
    return {
        "User-Agent": URL.includes("api.php") ?
            "okhttp/3.12.11" :
            "Mozilla/5.0"
    };
}
export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        homeVod: homeVod,
        category: category,
        detail: detail,
        play: play,
        search: search,
    };
}