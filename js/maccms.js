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
const urlPattern1 = /api\.php\/.*?\/vod/;
const urlPattern2 = /api\.php\/.+?\.vod/;
const parsePattern = /\/.+\\?.+=/;
const parsePattern1 = /.*(url|v|vid|php\?id)=/;
const parsePattern2 = /https?:\/\/[^\/]*/;
const htmlVideoKeyMatch = [
    /player=new/,
    /<div id="video"/,
    /<div id="[^"]*?player"/,
    /\/\/视频链接/,
    /HlsJsPlayer\(/,
    /<iframe[\s\S]*?src="[^"]+?"/,
    /<video[\s\S]*?src="[^"]+?"/,
];

async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    host = cfg.ext;
    if (cfg.ext.hasOwnProperty('host')) {
        host = cfg.ext.host;
        siteJx = cfg.ext;
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

// 苹果CMS V10分类接口（ac=class）
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
                const typePid = item.type_pid;

                // 跳过敏感分类
                if (isBan(typeName)) {
                    continue;
                }

                // 处理去重逻辑
                if (!uniqueClasses[typeName]) {
                    uniqueClasses[typeName] = item;
                } else {
                    if (typePid !== 0 && uniqueClasses[typeName].type_pid === 0) {
                        uniqueClasses[typeName] = item;
                    }
                }
            }

            // 将去重后的对象转为数组，添加到结果中
            result.class = Object.values(uniqueClasses).map(item => ({
                type_id: item.type_id,
                type_name: item.type_name
            }));
        }

        return JSON.stringify(result);
    } catch (e) {
        SpiderDebug.log("分类接口错误：" + e);
    }
    return JSON.stringify({
        class: []
    });
}

// 苹果CMS V10首页推荐（ac=list&t=1，t=1为推荐）
async function homeVod() {
    try {
        const url = `${host}?ac=videolist&t=1&pg=1`; // t=1表示推荐
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
        SpiderDebug.log(e);
    }
    return "";
}

// 苹果CMS V10分类列表（ac=list&class=类型ID）
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
            pagecount: obj.pagecount || 1, // 苹果V10总页数在pagecount
            limit: obj.limit || 20,
            total: obj.total || 0, // 苹果V10总条数在total
            list: videos
        });
    } catch (e) {
        SpiderDebug.log(e);
    }
    return "";
}

// 苹果CMS V10详情接口（ac=detail&ids=视频ID）
async function detail(ids) {
    try {
        const url = `${host}?ac=detail&ids=${ids}`; // 苹果V10详情参数ids
        const json = await request(url, getHeaders(url));
        const obj = JSON.parse(json);
        const result = {
            list: []
        };
        const vod = {};
        const data = obj.list && obj.list[0] ? obj.list[0] : {};
        vod.vod_id = data.vod_id || ids;
        vod.vod_name = data.vod_name || "";
        vod.vod_pic = data.vod_pic || "";
        vod.type_name = data.type_name || "";
        vod.vod_year = data.vod_year || "";
        vod.vod_area = data.vod_area || "";
        vod.vod_remarks = data.vod_remarks || "";
        vod.vod_actor = data.vod_actor || "";
        vod.vod_director = data.vod_director || "";
        vod.vod_content = data.vod_content || "";

        // 苹果V10播放源字段：vod_play_from和vod_play_url
        vod.vod_play_from = data.vod_play_from || "";
        vod.vod_play_url = data.vod_play_url || "";

        result.list.push(vod);
        return JSON.stringify(result);
    } catch (e) {
        SpiderDebug.log(e);
    }
    return "";
}

// 播放接口适配苹果V10的播放地址格式
async function play(flag, id, vipFlags) {
    try {
        let parseUrls = siteJx[flag];
        if (!parseUrls) {
            parseUrls = siteJx['*'] || [];
        }

        if (parseUrls.length > 0) {
            const result = await getFinalVideo(flag, parseUrls, id);
            if (result !== null) {
                return JSON.stringify(result);
            }
        }

        return JSON.stringify({
            parse: 0,
            url: id
        });
    } catch (e) {
        SpiderDebug.log(e);
    }
    return "";
}

// 苹果CMS V10搜索接口（ac=list&wd=关键词）
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
        SpiderDebug.log(error);
    }
    return "";
}

// 辅助函数保持不变
async function getFinalVideo(flag, parseUrls, url) {
    for (const parseUrl of parseUrls) {
        if (!parseUrl) continue;
        let playUrl = parseUrl + url; // 拼接完整的playUrl
        if (playUrl.startsWith("sniff")) {
            playUrl = playUrl.replace("sniff:", "");
            return {
                parse: 1,
                url: playUrl // 返回拼接后的完整playUrl
            };
        }
        else{
        //const playUrl = "https://cn.211dm.com/anime/1c77d481f81224e6445c3848/play/3/4.html";
        const content = await request(playUrl, null, 10000);

        try {
            const tryJson = JSON.parse(content);
            if (tryJson.url) {
                return {
                    url: tryJson.url,
                    header: tryJson.header ? JSON.stringify(tryJson.header) : ""
                };
            }
        } catch (error) {}
        }
    }
    

    // 所有解析接口都失败时返回null
    return null;
}

function isBan(key) {
    return key === "伦理" || key === "情色" || key === "福利";
}

function getHeaders(URL) {
    const headers = {};
    headers["User-Agent"] = URL.includes("api.php") ? "okhttp/3.12.11" : "Mozilla/5.0";
    return headers;
}

function isVideoFormat(url) {
    const snifferMatch = /http.*?\.(m3u8|mp4|flv|avi|mkv)/;
    return snifferMatch.test(url);
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