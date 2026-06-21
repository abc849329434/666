import { Crypto, load, _ } from 'assets://js/lib/cat.js';
let HOST = 'http://202.189.9.236:12345/mtq.php/v6';
let siteKey = "", siteType = "", sourceKey = "", ext = "";
const UA = 'Dart/3.8 (dart:io)';
async function request(reqUrl, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'User-Agent': UA,
            'Referer': HOST
        }
    };
    const mergedOptions = {...defaultOptions, ...options};
    let res = await req(reqUrl, mergedOptions);
    return res.content;
}
function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    sourceKey = cfg.sourceKey;
    ext = cfg.ext;
    if (ext && ext.indexOf('http') == 0) {
        root = ext;
    }
}
async function home(filter) {
    const link = `${HOST}/nav?token=`;
    try {
        const response = await request(link);
        if (!response) return "{}";
        const data = JSON.parse(response);
        let classes = [];
        let filterObj = {};
        if (data.code === 1 && data.data && Array.isArray(data.data)) {
            data.data.forEach(item => {
                if (item.type_id && item.type_name) {
                    classes.push({
                        "type_id": item.type_id.toString(),
                        "type_name": item.type_name
                    });
                    const filters = [];
                    if (item.type_extend && item.type_extend.class) {
                        const classValues = item.type_extend.class.split(',').map(c => c.trim()).filter(c => c);
                        if (classValues.length > 0) {
                            const classOptions = [{"n": "全部", "v": ""}];
                            classValues.forEach(c => {
                                classOptions.push({"n": c, "v": c});
                            });
                            filters.push({
                                "key": "class",
                                "name": "类型", 
                                "value": classOptions
                            });
                        }
                    }
                    if (item.type_extend && item.type_extend.area) {
                        const areaValues = item.type_extend.area.split(',').map(a => a.trim()).filter(a => a);
                        if (areaValues.length > 0) {
                            const areaOptions = [{"n": "全部", "v": ""}];
                            areaValues.forEach(a => {
                                areaOptions.push({"n": a, "v": a});
                            });
                            filters.push({
                                "key": "area",
                                "name": "地区",
                                "value": areaOptions
                            });
                        }
                    }
                    if (item.type_extend && item.type_extend.lang) {
                        const langValues = item.type_extend.lang.split(',').map(l => l.trim()).filter(l => l);
                        if (langValues.length > 0) {
                            const langOptions = [{"n": "全部", "v": ""}];
                            langValues.forEach(l => {
                                langOptions.push({"n": l, "v": l});
                            });
                            filters.push({
                                "key": "lang",
                                "name": "语言",
                                "value": langOptions
                            });
                        }
                    }
                    if (item.type_extend && item.type_extend.year) {
                        const yearValues = item.type_extend.year.split(',').map(y => y.trim()).filter(y => y);
                        if (yearValues.length > 0) {
                            const yearOptions = [{"n": "全部", "v": ""}];
                            yearValues.forEach(y => {
                                yearOptions.push({"n": y, "v": y});
                            });
                            filters.push({
                                "key": "year", 
                                "name": "年份",
                                "value": yearOptions
                            });
                        }
                    }
                    if (item.type_extend && item.type_extend.state) {
                        const stateValues = item.type_extend.state.split(',').map(s => s.trim()).filter(s => s);
                        if (stateValues.length > 0) {
                            const stateOptions = [{"n": "全部", "v": ""}];
                            stateValues.forEach(s => {
                                stateOptions.push({"n": s, "v": s});
                            });
                            filters.push({
                                "key": "state",
                                "name": "状态",
                                "value": stateOptions
                            });
                        }
                    }
                    if (item.type_extend && item.type_extend.version) {
                        const versionValues = item.type_extend.version.split(',').map(v => v.trim()).filter(v => v);
                        if (versionValues.length > 0) {
                            const versionOptions = [{"n": "全部", "v": ""}];
                            versionValues.forEach(v => {
                                versionOptions.push({"n": v, "v": v});
                            });
                            filters.push({
                                "key": "version",
                                "name": "版本",
                                "value": versionOptions
                            });
                        }
                    }
                    filters.push({
                        "key": "by",
                        "name": "排序",
                        "value": [
                            {"n": "全部", "v": ""},
                            {"n": "最新", "v": "time"},
                            {"n": "最热", "v": "hits"}, 
                            {"n": "评分", "v": "score"}
                        ]
                    });
                    filterObj[item.type_id.toString()] = filters;
                }
            });
        }
        return JSON.stringify({
            class: classes,
            filters: filterObj
        });
    } catch (error) {
        return "{}";
    }
}
async function homeVod() {
    const link = `${HOST}/index_video?token=`;
    try {
        const response = await request(link);
        if (!response) return JSON.stringify({ list: [] });
        if (response.trim().startsWith('<')) return JSON.stringify({ list: [] });
        const data = JSON.parse(response);
        let videos = [];
        if (data.code === 1 && data.data && Array.isArray(data.data)) {
            data.data.forEach(category => {
                if (category.vlist && Array.isArray(category.vlist)) {
                    category.vlist.forEach(item => {
                        if (item.vod_id) {
                            videos.push({
                                'vod_id': item.vod_id.toString(),
                                'vod_name': item.vod_name || '',
                                'vod_pic': item.vod_pic || '',
                                'vod_remarks': item.vod_remarks || '',
                                'vod_year': item.vod_year || '',
                                'vod_area': item.vod_area || '',
                                'vod_actor': item.vod_actor || '',
                                'vod_director': item.vod_director || '',
                                'vod_content': item.vod_content || '',
                                'type_id': item.type_id || category.type_id || '',
                                'vod_time_add': item.vod_time_add || ''
                            });
                        }
                    });
                }
            });
        }
        const detailData = {
            list: videos.slice(0, 40)
        };
        return JSON.stringify({
            list: detailData.list
        });
    } catch (error) {
        return JSON.stringify({list: []});
    }
}
async function category(tid, pg, filter, extend) {
    if (pg <= 0) pg = 1;
    let queryParams = `pg=${pg}&tid=${tid}`;
    if (extend) {
        if (extend.class) queryParams += `&class=${encodeURIComponent(extend.class)}`;
        if (extend.area) queryParams += `&area=${encodeURIComponent(extend.area)}`;
        if (extend.lang) queryParams += `&lang=${encodeURIComponent(extend.lang)}`;
        if (extend.year) queryParams += `&year=${encodeURIComponent(extend.year)}`;
        if (extend.by) {
            queryParams += `&order=${encodeURIComponent(extend.by)}`;
        }
    }
    queryParams += '&token=';
    const link = `${HOST}/video?${queryParams}`;
    try {
        const response = await request(link);
        if (!response) return JSON.stringify({list: []});
        if (response.trim().startsWith('<')) return JSON.stringify({list: []});
        const data = JSON.parse(response);
        if (data.code !== 1 || !data.data || !Array.isArray(data.data)) return JSON.stringify({list: []});
        const videos = data.data.map(item => {
            return {
                'vod_id': item.vod_id.toString(),
                'vod_name': item.vod_name || '',
                'vod_pic': item.vod_pic || '',
                'vod_remarks': item.vod_remarks || '',
                'vod_score': item.vod_score || '0.0',
                'vod_year': item.vod_year || '',
                'vod_area': item.vod_area || '',
                'vod_actor': item.vod_actor || '',
                'vod_director': item.vod_director || '',
                'vod_content': item.vod_content || '',
                'type_id': item.type_id || tid,
                'vod_time_add': item.vod_time_add || ''
            };
        });
        const result = {
            list: videos,
            page: parseInt(data.page) || pg,
            pagecount: parseInt(data.pagecount) || 1,
            limit: parseInt(data.limit) || 20,
            total: parseInt(data.total) || videos.length
        };
        return JSON.stringify(result);
    } catch (error) {
        return JSON.stringify({
            list: [],
            error: '处理过程出现错误：' + error.message
        });
    }
}
//http://202.189.9.236:12345/mtq.php/v6/search?pg=1&tid=0&text=%E6%A2%85%E6%A0%B9&token=&csrf=Ize0z068hA6DN291X%2FykS%2BWgYkbm%2FR4VBfwUzqNeNp2LxpquVAy4LPn6dRIKL6%2Bly8NHXhMdvw3jiZwwYOoktNy1yDv6Py5gqME9cjqpYphSG9p%2B4WdzbJBD4jBlkSFBSm3sGabREO3LRXuUvuYbh8NK%2Br0tcPlHAUN8ZUmxxKU%3D
async function search(wd, quick) {
    const searchUrl = `${HOST}/search?pg=1&tid=0&text=${encodeURIComponent(wd)}&token=`;
    try {
        const response = await request(searchUrl);
        if (!response) return JSON.stringify({list: []});
        const data = JSON.parse(response);
        if (data.code !== 1 || !data.data || !Array.isArray(data.data)) return JSON.stringify({list: []});
        
        const videos = data.data.map(item => {
            return {
                'vod_id': item.vod_id.toString(),
                'vod_name': item.vod_name || '',
                'vod_pic': item.vod_pic || '',
                'vod_remarks': item.vod_remarks || '',
                'vod_score': item.vod_score || '0.0',
                'vod_year': item.vod_year || '',
                'vod_area': item.vod_area || '',
                'vod_actor': item.vod_actor || '',
                'vod_director': item.vod_director || '',
                'vod_content': item.vod_content || '',
                'type_id': item.type_id || '',
                'vod_time_add': item.vod_time_add || ''
            };
        });
        
        const result = {
            list: videos,
            total: videos.length
        };
        return JSON.stringify(result);
    } catch (error) {
        return JSON.stringify({
            list: [],
            error: '搜索过程出现错误：' + error.message
        });
    }
}

async function detail(id) {
    try {
        const response = await request(`${HOST}/video_detail?id=${id}`);
        if (!response) return JSON.stringify({ list: [] });
        const data = JSON.parse(response);
        if (data.code !== 1) return JSON.stringify({ list: [] });
        const item = data.data.vod_info;
        const vod = {
            vod_id: id,
            vod_name: item.vod_name || '',
            vod_pic: item.vod_pic || '',
            vod_year: item.vod_year || '',
            vod_area: item.vod_area || '',
            vod_remarks: item.vod_remarks || '',
            vod_actor: item.vod_actor || '',
            vod_director: item.vod_director || '',
            vod_content: item.vod_content || item.vod_blurb || '',
            type_name: item.vod_class || '',
            vod_lang: item.vod_lang || '',
            vod_play_from: '',
            vod_play_url: ''
        };
        if (item.vod_url_with_player && Array.isArray(item.vod_url_with_player)) {
            const prioritySources = ['4KCS', '高清B', '独家自建'];
            const sortedPlayers = [...item.vod_url_with_player].sort((a, b) => {
                const aName = a.name || a.code || '';
                const bName = b.name || b.code || '';
                const aIndex = prioritySources.indexOf(aName);
                const bIndex = prioritySources.indexOf(bName);
                if (aIndex !== -1 && bIndex !== -1) {
                    return aIndex - bIndex;
                }
                if (aIndex !== -1) return -1;
                if (bIndex !== -1) return 1;
                return 0;
            });
            const playFrom = [];
            const playUrl = [];
            sortedPlayers.forEach((player, index) => {
                const sourceName = player.name || player.code || `线路${index + 1}`;
                playFrom.push(sourceName);
                const episodes = [];
                const playerUrl = player.url || '';
                const parseApi = player.parse_api || '';
                if (playerUrl.includes('#')) {
                    const episodeGroups = playerUrl.split('#');
                    episodeGroups.forEach((group) => {
                        const [epName, epUrl] = group.split('$').map(part => part.trim());
                        if (epName && epUrl) {
                            const playParams = `${parseApi}|${epUrl}`;
                            episodes.push(`${epName}$${playParams}`);
                        }
                    });
                } else if (playerUrl.includes('$')) {
                    const [epName, epUrl] = playerUrl.split('$').map(part => part.trim());
                    if (epName && epUrl) {
                        const playParams = `${parseApi}|${epUrl}`;
                        episodes.push(`${epName}$${playParams}`);
                    }
                } else if (playerUrl) {
                    const playParams = `${parseApi}|${playerUrl}`;
                    episodes.push(`正片$${playParams}`);
                }
                playUrl.push(episodes.length > 0 ? episodes.join('#') : '');
            });
            vod.vod_play_from = playFrom.join('$$$');
            vod.vod_play_url = playUrl.join('$$$');
        } else {
            vod.vod_play_from = item.vod_play_from || '';
            vod.vod_play_url = item.vod_play_url || '';
        }
        return JSON.stringify({ list: [vod] });
    } catch (error) {
        return JSON.stringify({ 
            list: [], 
            error: `详情解析失败: ${error.message}` 
        });
    }
}
async function play(flag, id, flags) {
    try {
        if (id.includes('|')) {
            const [parseApi, actualUrl] = id.split('|').map(part => part.trim());
            if (!parseApi || parseApi === 'undefined' || parseApi === 'null') {
                return JSON.stringify({ parse: 0, url: actualUrl });
            }
            let requestUrl;
            if (parseApi.includes('?')) {
                requestUrl = `${parseApi}&url=${encodeURIComponent(actualUrl)}`;
            } else {
                requestUrl = `${parseApi}?url=${encodeURIComponent(actualUrl)}`;
            }
            const response = await request(requestUrl);
            if (response) {
                try {
                    const data = JSON.parse(response);
                    if (data.url) {
                        return JSON.stringify({ parse: 0, url: data.url });
                    } else if (data.code === 200 && data.data) {
                        const finalUrl = typeof data.data === 'string' ? data.data : data.data.url;
                        if (finalUrl) {
                            return JSON.stringify({ parse: 0, url: finalUrl });
                        }
                    }
                } catch (parseError) {
                    if (response.startsWith('http') || response.startsWith('//')) {
                        const finalUrl = response.startsWith('//') ? 'https:' + response : response;
                        return JSON.stringify({ parse: 0, url: finalUrl });
                    }
                }
            }
            return JSON.stringify({ parse: 0, url: actualUrl });
        }
        return JSON.stringify({ parse: 0, url: id });
    } catch (error) {
        return JSON.stringify({ parse: 0, url: id });
    }
}
export function __jsEvalReturn() {
    return {
        init: init,
        detail: detail,
        home: home,
        play: play,
        homeVod: homeVod,
        category: category,
        search: search
    };
}
