const axios = require("axios");
const CryptoJS = require("crypto-js");

const HOSTS = [
"http://cms339.lyyytv.cn",
"http://pgcms.lyyytv.cn",
"http://cms4kzj.lyyytv.cn",
"http://cms.lygdyy.cn"
];

const CMS_KEY = "wP5btxoc3yv8FoBQENFZumF0EUYr4LTy";

const COMMON_HEADERS = {
"User-Agent": "okhttp/4.12.0"
};

const PLAY_NAME_POOL = [
"爱你4K",
"爱你4K2",
"爱你4K3",
"爱你4K4",
"哈基米",
"小南北",
"绿豆"
];

const DOMAIN_REPLACE = {
"ym4kjx.lyyytv.cn": "am4kjx.lyyytv.cn"
};

const meta = {
key: "影探",
name: "影探T4",
type: 4,
api: "/video/影探",
searchable: 1,
quickSearch: 1,
filterable: 1,
changeable: 0
};

const http = axios.create({
timeout: 10000,
headers: COMMON_HEADERS
});

// =====================================================
// host轮询
// =====================================================

const requestWithFallback = async (path) => {

let lastErr = null;  

const hosts = [...HOSTS].sort(  
    () => Math.random() - 0.5  
);  

for (const host of hosts) {  

    try {  

        const url =  
            host.replace(/\/$/, "") +  
            "/" +  
            path.replace(/^\//, "");  

        const { data } = await http.get(url);  

        return data;  

    } catch (e) {  

        lastErr = e;  
    }  
}  

throw lastErr || new Error("全部域名失效");

};

// =====================================================
// AES解密
// =====================================================

const lvdou = (text) => {

const prefix = "lvdou+";  

// 非加密  
if (!text.startsWith(prefix)) {  

    Object.keys(DOMAIN_REPLACE).forEach(k => {  
        text = text.replace(  
            k,  
            DOMAIN_REPLACE[k]  
        );  
    });  

    return text;  
}  

try {  

    const key = CryptoJS.enc.Utf8.parse(  
        CMS_KEY.slice(0, 16)  
    );  

    const iv = CryptoJS.enc.Utf8.parse(  
        CMS_KEY.slice(-16)  
    );  

    const encrypted = text.slice(  
        prefix.length  
    );  

    const decrypted = CryptoJS.AES.decrypt(  
        {  
            ciphertext: CryptoJS.enc.Base64.parse(  
                encrypted  
            )  
        },  
        key,  
        {  
            iv,  
            mode: CryptoJS.mode.CBC,  
            padding: CryptoJS.pad.Pkcs7  
        }  
    );  

    let realUrl = decrypted.toString(  
        CryptoJS.enc.Utf8  
    );  

    Object.keys(DOMAIN_REPLACE).forEach(k => {  

        realUrl = realUrl.replace(  
            k,  
            DOMAIN_REPLACE[k]  
        );  
    });  

    return realUrl;  

} catch (e) {  

    return text;  
}

};

// =====================================================
// 检测视频
// =====================================================

const checkPlayUrl = (url) => {

return /\.(mp4|m3u8|flv|avi|mkv|ts|mov|wmv|webm)(\?.*)?$/i  
    .test(url);

};

// =====================================================
// 首页分类
// =====================================================

const homeContent = async () => {

try {  

    const data = await requestWithFallback(  
        "api.php/app/nav?token="  
    );  

    const classes = [];  
    const filters = {};  

    const keys = [  
        "class",  
        "area",  
        "lang",  
        "year",  
        "letter",  
        "by",  
        "sort"  
    ];  

    for (const item of data.list || []) {  

        classes.push({  
            type_name: item.type_name,  
            type_id: item.type_id.toString()  
        });  

        const ext = item.type_extend || {};  

        const hasFilter = keys.some(  
            k => ext[k] && ext[k].trim()  
        );  

        if (!hasFilter) continue;  

        filters[item.type_id] = [];  

        for (const k of keys) {  

            if (!ext[k]) continue;  

            const arr = ext[k]  
                .split(",")  

                .filter(Boolean)  

                .map(v => ({  
                    n: v.trim(),  
                    v: v.trim()  
                }));  

            filters[item.type_id].push({  
                key: k,  
                name: k,  
                value: arr  
            });  
        }  
    }  

    return {  
        class: classes,  
        filters  
    };  

} catch (e) {  

    return {  
        class: []  
    };  
}

};

// =====================================================
// 首页推荐
// =====================================================

const homeVideoContent = async () => {

try {  

    const data = await requestWithFallback(  
        "api.php/app/index_video?token="  
    );  

    const list = [];  

    for (const item of data.list || []) {  

        list.push(  
            ...(item.vlist || [])  
        );  
    }  

    return {  
        list  
    };  

} catch (e) {  

    return {  
        list: []  
    };  
}

};

// =====================================================
// 分类
// =====================================================

const categoryContent = async (
tid,
pg,
extend = {}
) => {

try {  

    const params = [  
        `tid=${tid}`,  
        `pg=${pg || 1}`,  
        "limit=18"  
    ];  

    if (extend.class) {  
        params.push(  
            `class=${encodeURIComponent(  
                extend.class  
            )}`  
        );  
    }  

    if (extend.area) {  
        params.push(  
            `area=${encodeURIComponent(  
                extend.area  
            )}`  
        );  
    }  

    if (extend.lang) {  
        params.push(  
            `lang=${encodeURIComponent(  
                extend.lang  
            )}`  
        );  
    }  

    if (extend.year) {  
        params.push(  
            `year=${encodeURIComponent(  
                extend.year  
            )}`  
        );  
    }  

    const data = await requestWithFallback(  
        "api.php/app/video?" +  
        params.join("&")  
    );  

    return data;  

} catch (e) {  

    return {  
        list: []  
    };  
}

};

// =====================================================
// 搜索
// =====================================================

const searchContent = async (
wd,
pg
) => {

try {  

    const data = await requestWithFallback(  
        `api.php/app/search?text=${encodeURIComponent(wd)}&pg=${pg || 1}`  
    );  

    const list = (data.list || []).map(  
        item => {  

            delete item.type;  

            return item;  
        }  
    );  

    return {  
        list,  
        page: parseInt(pg || 1),  
        pagecount: 999,  
        limit: 20,  
        total: list.length  
    };  

} catch (e) {  

    return {  
        list: []  
    };  
}

};

// =====================================================
// 详情
// =====================================================

const detailContent = async (id) => {

try {  

    const data = await requestWithFallback(  
        `api.php/app/video_detail?id=${id}`  
    );  

    const item =  
        data.data ||  
        (data.list && data.list[0]) ||  
        data;  

    if (!item) {  
        return {  
            list: []  
        };  
    }  

    const playFrom = [];  
    const playUrls = [];  

    let idx = 0;  

    for (const source of item.vod_url_with_player || []) {  

        const urls = [];  

        for (const ep of source.url.split("#")) {  

            if (!ep) continue;  

            const parts = ep.split("$");  

            if (parts.length < 2) continue;  

            const epName = parts[0];  
            const epUrl = lvdou(parts[1]);  

            urls.push(  
                `${epName}$${epUrl}`  
            );  
        }  

        if (urls.length === 0) {  
            continue;  
        }  

        playFrom.push(  
            PLAY_NAME_POOL[  
                idx % PLAY_NAME_POOL.length  
            ]  
        );  

        playUrls.push(  
            urls.join("#")  
        );  

        idx++;  
    }  

    delete item.vod_url_with_player;  

    item.vod_play_from =  
        playFrom.join("$$$");  

    item.vod_play_url =  
        playUrls.join("$$$");  

    return {  
        list: [item]  
    };  

} catch (e) {  

    return {  
        list: []  
    };  
}

};

// =====================================================
// 播放
// =====================================================

const playerContent = async (
flag,
play
) => {

try {  

    let jx = 0;  

    if (  
        /(iqiyi|qq\.com|youku|mgtv|bilibili)/i  
        .test(play)  
    ) {  

        jx = 1;  
    }  

    return {  
        jx,  
        parse: 0,  
        playUrl: "",  
        url: play,  
        header: COMMON_HEADERS  
    };  

} catch (e) {  

    return {  
        jx: 0,  
        parse: 0,  
        url: play  
    };  
}

};

// =====================================================
// 主入口
// =====================================================

module.exports = async (app, opt) => {

app.get(meta.api, async (req, res) => {  

    try {  

        const {  
            ac,  
            t,  
            pg,  
            ids,  
            wd,  
            play,  
            flag,  
            extend  
        } = req.query;  

        // 播放  
        if (play) {  

            return await playerContent(  
                flag,  
                play  
            );  
        }  

        // 搜索  
        if (wd) {  

            return await searchContent(  
                wd,  
                pg  
            );  
        }  

        // 首页  
        if (!ac) {  

            const home =  
                await homeContent();  

            const videos =  
                await homeVideoContent();  

            return {  
                class: home.class,  
                filters: home.filters,  
                list: videos.list  
            };  
        }  

        // 分类  
        if (  
            ac === "list" ||  
            (t && !ids)  
        ) {  

            return await categoryContent(  
                t,  
                pg,  
                extend  
                    ? JSON.parse(extend)  
                    : {}  
            );  
        }  

        // 详情  
        if (  
            ac === "detail" &&  
            ids  
        ) {  

            return await detailContent(  
                ids  
            );  
        }  

        return {  
            code: 404  
        };  

    } catch (e) {  

        return {  
            code: 500,  
            msg: e.message  
        };  
    }  
});  

opt.sites.push(meta);

};