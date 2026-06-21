const axios = require("axios");
const BASE_URL = "http://cmsok.lyyytv.cn";

const COMMON_HEADERS = {
    "User-Agent": "okhttp/4.9.1"
};

const PLAY_LINES = [
    { id: "4K(UC)", name: "光头强" },
    { id: "4K(BD)", name: "熊大" },
    { id: "4K(YD)", name: "熊二" },
    { id: "4K(123)", name: "吉吉国王" }
];

const _getCategories = async () => {
    const { data } = await axios.get(`${BASE_URL}/api.php/app/nav?token`, {
        headers: COMMON_HEADERS
    });
    
    const dy = {
        "class": "类型",
        "area": "地区",
        "lang": "语言", 
        "year": "年份",
        "letter": "字母",
        "by": "排序"
    };
    
    const categories = [];
    const filters = {};
    let filterUrl = '';
    
    data.list.forEach((item, index) => {
        categories.push({
            type_id: item.type_id.toString(),
            type_name: item.type_name
        });
        
        const hasFilter = Object.keys(dy).some(key => 
            item.type_extend[key] && item.type_extend[key].trim() !== ""
        );
        
        if (hasFilter) {
            filters[item.type_id] = [];
            Object.keys(dy).forEach(key => {
                if (item.type_extend[key] && item.type_extend[key].trim() !== "") {
                    const values = item.type_extend[key].split(',').map(v => v.trim());
                    filters[item.type_id].push({
                        key: key,
                        name: dy[key],
                        value: values.map(v => ({ n: v, v: v }))
                    });
                    
                    if (index === 0) {
                        filterUrl += `&${key}={{fl.${key}}}`;
                    }
                }
            });
        }
    });

    const classNames = categories.map(cat => cat.type_name).join("&");
    const classIds = categories.map(cat => cat.type_id).join("&");
    
    return { 
        categories, 
        filters,
        classNames,
        classIds,
        filterUrl
    };
};

const _home = async () => {
    const { categories } = await _getCategories();
    
    const { data } = await axios.get(`${BASE_URL}/api.php/app/index_video`, {
        headers: COMMON_HEADERS
    });
    
    let recommendVods = [];
    if (data.list && Array.isArray(data.list)) {
        data.list.forEach(item => {
            if (item.vlist && Array.isArray(item.vlist) && item.vlist.length !== 0) {
                recommendVods = recommendVods.concat(item.vlist.map(vod => ({
                    vod_id: vod.vod_id,
                    vod_name: vod.vod_name,
                    vod_pic: vod.vod_pic,
                    vod_remarks: vod.vod_remarks || ""
                })));
            }
        });
    }
    
    return {
        class: categories,
        list: recommendVods
    };
};

const _category = async ({ id, page, filter }) => {
    let url = `${BASE_URL}/api.php/app/video?tid=${id}&limit=20&pg=${page || 1}`;
    
    if (filter) {
        Object.keys(filter).forEach(key => {
            if (filter[key]) {
                url += `&${key}=${encodeURIComponent(filter[key])}`;
            }
        });
    }
    
    const { data } = await axios.get(url, {
        headers: COMMON_HEADERS
    });
    
    return {
        list: data.list.map(item => ({
            vod_id: item.vod_id,
            vod_name: item.vod_name,
            vod_pic: item.vod_pic,
            vod_remarks: item.vod_remarks || ""
        })),
        page: parseInt(page) || 1,
        pagecount: Math.ceil(data.total / 20),
        total: data.total
    };
};

const _isAllowedDomain = (url) => {
    if (!url) return false;
    return /(lz4kjx|wx4kjx|am4kjx|yx4kjx)/.test(url);
};

const _filterEpisodes = (playUrl) => {
    if (!playUrl) return "";
    
    const episodes = playUrl.split('#');
    const validEpisodes = episodes.filter(episode => {
        const parts = episode.split('$');
        if (parts.length < 2) return false;
        
        const episodeName = parts[0].trim();
        const episodeUrl = parts[1].trim();
        
        if (!_isAllowedDomain(episodeUrl)) {
            return false;
        }
        
        const hasValidEpisodeName = !/^\d+$/.test(episodeName);
        
        return hasValidEpisodeName;
    });
    
    return validEpisodes.join('#');
};

const _mapLineNames = (originalPlayFrom) => {
    if (!originalPlayFrom) return "";
    
    const fromParts = originalPlayFrom.split('$$$');
    const mappedParts = [];
    
    for (let i = 0; i < fromParts.length; i++) {
        const originalName = fromParts[i];
        if (originalName.includes("UC") || originalName.includes("光头强")) {
            mappedParts.push(PLAY_LINES[0].name);
        } else if (originalName.includes("BD") || originalName.includes("熊大")) {
            mappedParts.push(PLAY_LINES[1].name);
        } else if (originalName.includes("YD") || originalName.includes("熊二")) {
            mappedParts.push(PLAY_LINES[2].name);
        } else if (originalName.includes("123") || originalName.includes("吉吉国王")) {
            mappedParts.push(PLAY_LINES[3].name);
        } else {
            if (i < PLAY_LINES.length) {
                mappedParts.push(PLAY_LINES[i].name);
            } else {
                mappedParts.push(originalName);
            }
        }
    }
    
    return mappedParts.join('$$$');
};

const _filterPlaySources = (playFrom, playUrl) => {
    if (!playFrom || !playUrl) return { playFrom: "", playUrl: "" };
    
    const fromParts = playFrom.split('$$$');
    const urlParts = playUrl.split('$$$');
    
    const validFromParts = [];
    const validUrlParts = [];
    
    for (let i = 0; i < fromParts.length; i++) {
        const from = fromParts[i];
        const url = urlParts[i] || "";
        
        const filteredEpisodes = _filterEpisodes(url);
        
        if (filteredEpisodes && filteredEpisodes.trim() !== "") {
            let mappedName = from;
            if (from.includes("UC") || from.includes("光头强")) {
                mappedName = PLAY_LINES[0].name;
            } else if (from.includes("BD") || from.includes("熊大")) {
                mappedName = PLAY_LINES[1].name;
            } else if (from.includes("YD") || from.includes("熊二")) {
                mappedName = PLAY_LINES[2].name;
            } else if (from.includes("123") || from.includes("吉吉国王")) {
                mappedName = PLAY_LINES[3].name;
            } else if (i < PLAY_LINES.length) {
                mappedName = PLAY_LINES[i].name;
            }
            
            validFromParts.push(mappedName);
            validUrlParts.push(filteredEpisodes);
        }
    }
    
    return {
        playFrom: validFromParts.join('$$$'),
        playUrl: validUrlParts.join('$$$')
    };
};

const _detail = async ({ id }) => {
    const { data } = await axios.get(`${BASE_URL}/api.php/app/video_detail?id=${id}`, {
        headers: COMMON_HEADERS
    });
    
    const item = data.data;
    
    let playFrom = item.vod_play_from || "";
    let playUrl = item.vod_play_url || "";
    
    const filtered = _filterPlaySources(playFrom, playUrl);
    playFrom = filtered.playFrom;
    playUrl = filtered.playUrl;
    
    return {
        list: [{
            vod_id: item.vod_id,
            vod_name: item.vod_name,
            vod_pic: item.vod_pic,
            vod_content: item.vod_content,
            vod_actor: item.vod_actor,
            vod_director: item.vod_director,
            vod_area: item.vod_area,
            vod_year: item.vod_year,
            vod_remarks: item.vod_remarks,
            vod_play_from: playFrom,
            vod_play_url: playUrl
        }]
    };
};

const _play = async ({ flag, play }) => {
    let playUrl = play;
    
    playUrl = playUrl.replace('lz4kjx', 'wx4kjx').replace('am4kjx', 'yx4kjx');
    
    const isDirectVideo = /\.(m3u8|mp4)/.test(playUrl);
    
    if (isDirectVideo) {
        return {
            parse: 0,
            url: playUrl,
            header: COMMON_HEADERS
        };
    } else {
        return {
            parse: 0,
            url: playUrl
        };
    }
};

const _search = async ({ page, wd }) => {
    try {
        console.log(`搜索关键词: ${wd}, 页码: ${page || 1}`);
        
        const { data } = await axios.get(`${BASE_URL}/api.php/app/search`, {
            params: {
                text: wd,
                pg: page || 1
            },
            headers: {
                'User-Agent': 'okhttp/4.9.1',
                'Accept': 'application/json, text/plain, */*'
            },
            timeout: 10000
        });
        
        console.log(`搜索返回数据条数: ${data.list ? data.list.length : 0}`);
        
        return {
            list: data.list ? data.list.map(item => ({
                vod_id: item.vod_id,
                vod_name: item.vod_name,
                vod_pic: item.vod_pic,
                vod_remarks: item.vod_remarks || "",
                vod_year: item.vod_year || ""
            })) : [],
            page: parseInt(page) || 1,
            pagecount: data.total ? Math.ceil(data.total / 20) : 1,
            total: data.total || 0
        };
    } catch (error) {
        console.error("搜索请求失败:", error.message);
        return {
            list: [],
            page: parseInt(page) || 1,
            pagecount: 1,
            total: 0
        };
    }
};

const meta = {
    key: "xcm",
    name: "熊出没4K",
    type: 4,
    api: "/video/xcm",
    searchable: 1,
    quickSearch: 1,
    changeable: 0,
    filterable: 1,
    headers: {
        'User-Agent': 'okhttp/4.9.1'
    }
};

module.exports = async (app, opt) => {
    app.get(meta.api, async (req, reply) => {
        try {
            const { ac, t, pg, ids, flag, play, wd, filter } = req.query;
            
            if (play) return await _play({ flag, play });
            if (wd) return await _search({ page: pg || 1, wd });
            if (!ac) return await _home();
            if (ac === "detail" && t) return await _category({ id: t, page: pg || 1, filter: filter ? JSON.parse(filter) : {} });
            if (ac === "detail" && ids) return await _detail({ id: ids });
            
            return { code: 404 };
        } catch (e) {
            console.error("请求处理异常:", e.message);
            return { code: 500, message: e.message };
        }
    });
    opt.sites.push(meta);
};