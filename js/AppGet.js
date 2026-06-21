/*
修改版本：250814-2
title: 'AppGet模板', author: '小可乐/v5.6.4'
说明：
ext参数标准格式:  域名$key$iv$deviceId$User-Agent|url变换开关$官源解析$自定义分类
如咖啡: "ext": "http://160.202.243.62:2566$qwertyuiopqwerty$qwertyuiopqwerty$|咖啡$1$1$https://jx.m3u8.tv/jiexi/?url=$电影&剧集>>电视剧&动漫"，支持base64格式，如:
"ext": "aHR0cDovLzE2MC4yMDIuMjQzLjYyOjI1NjYkcXdlcnR5dWlvcHF3ZXJ0eSRxd2VydHl1aW9wcXdlcnR5JHzlkpbllaEkMSQxJGh0dHBzOi8vangubTN1OC50di9qaWV4aS8/dXJsPSTnlLXlvbEm5Ymn6ZuGPj7nlLXop4bliacm5Yqo5ryr",
key和iv相同，iv可省略,没有deviceId,可以不写: 如:咖啡app可写为"ext": "http://160.202.243.62:2566$qwertyuiopqwerty|咖啡$$1"，
url变换开关主要针对类似咖啡的app，默认为关，设为1后打开，所有url会变为内置的第二组url,
官源解析不填播放会优先使用app自己的解析，填了官解后，播放会使用所填的官解，主要针对部分app自带官解不行的情况，爱优腾芒哔哔哔哔只设了一个通用官解位置，不需要不填
自定义分类按照所填的分类和顺序显示，用&分隔，如：电影&剧集&动漫，如想替换分类名，可以 电影>>高清影片&剧集>>电视剧&动漫
*/
import {Crypto} from 'assets://js/lib/cat.js';

let MOBILE_UA = "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36";
let def_header = {'User-Agent': MOBILE_UA};
let cachedPlayUrls = {};
let HOST;

let kparam = {
    host: '',
    headers: {'User-Agent': 'okhttp/3.10.0'}, // okhttp/3.14.9
    timeout: 5000,
    pgcount: 0,
    key: '',
    iv: '',
    urlRp: '',
    gparse: '',
    className: '',
    xurl: '/api.php/getappapi',
    initData: '',
    search_verify: 0,
    collation: [],  //线路排序规则
    LineName: '' //自定义替换线路名，留空则不替换，skey：使用key作为替换名
};

async function request(reqUrl, header, data, postType, tobase64) {
    try {
        let optObj = {
            headers: header || kparam.headers,
            method: postType ? 'post' : 'get',
            data: postType ? data : undefined,
            postType: postType || undefined,
            timeout: kparam.timeout || 5000,
        };
        if(tobase64){
            optObj.buffer = 2;
        }
        let res = await req(reqUrl, optObj);
        return res.content;
    } catch (e) {
        throw new Error();
    }
}

async function getdata(url, data, method,headers) {
    try {
        url = /^http/.test(url) ? url : `${kparam.host}${url}`;
        let kres = await request(url, headers || kparam.headers, data, method);
        if (!kres) {throw new Error('获取响应数据失败');}
        let kresObj = JSON.parse(kres);
        let kdata = kresObj.data || '';
        if (!kdata) {throw new Error();}
        let decrypted = decryptAes(kdata, kparam.key, kparam.iv);
        if (!decrypted) {throw new Error('解密失败');}
        return JSON.parse(decrypted);
    } catch (e) {
        return {};
    }
}

async function init(cfg) {
    try {
        if (!cfg.ext) {throw new Error();}
        let extValue = cfg.ext.trim();
        try {extValue = decodeBase64(extValue);} catch (e) {}
        try {
            let confgs = extValue.split('|')[1]?.split('$');
            kparam.urlRp = confgs?.[2] || '';
            kparam.gparse = confgs?.[3]?.trim() || '';
            kparam.className = confgs?.[4]?.trim() || '';
            if(!kparam.collation.length){kparam.collation = extValue.trim().split('线路排序:')?.[1]?.split('>') || [];}
            if(kparam.LineName === 'skey'){  kparam.LineName = cfg.skey || '';  }
            if (kparam.urlRp === '1') {kparam.xurl = kparam.xurl.replace('getappapi', 'qijiappapi');}

        } catch (e) {
        }
        let parts = extValue.split('|')[0].split('$');
        let host_ = parts[0].trim() || '';

        if(!/^https?:\/\/[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(:\d+)?(\/)?$/.test(host_)){
            let host__ = await request(host_,kparam.headers);
            kparam.host = host__.endsWith('/') ? host__.slice(0, -1) : host__;
        }else{
            kparam.host = host_;
        }

        if (!kparam.host.startsWith('http')) {throw new Error();}
        kparam.host = kparam.host.replace(/\/+$/,'');
        HOST = kparam.host;
        kparam.key = parts[1] || 'ENonBHeVBoYZhVUV';
        kparam.iv = parts[2] || kparam.key;
        let deviceId = parts[3] || '';
        let userAgent = parts[4] || 'okhttp/3.10.0';
        if (deviceId) { kparam.headers['app-user-device-id'] = deviceId; }
        kparam.headers['User-Agent'] = userAgent;
        kparam.initData = await getdata(kparam.xurl + '.index/initV119');
        kparam.search_verify = kparam.initData?.config?.system_search_verify_status || false;
    } catch (e) {
        throw new Error('初始化参数失败');
    }
}

async function home(filter) {
    try {
        let ktypeObj = kparam.initData;
        ktypeObj = filterClass('公告', ktypeObj);
        let arrclsNames = kparam.className.split('&');
        if(arrclsNames.length === 1 && arrclsNames[0] === ""){ktypeObj = filterClass('全部', ktypeObj);}
        let classes = ktypeObj.type_list.map((item) => { return {type_name: item.type_name, type_id: item.type_id}; });
        if (Array.isArray(arrclsNames) && arrclsNames.length) {
            try {
                let result = arrclsNames.map((item) => {
                    let arrNames = item.split('>>');
                    let oldName = arrNames[0];
                    let newName = arrNames[1] || oldName;
                    let targetIndex = classes.findIndex((cls) => cls.type_name === oldName);
                    if (targetIndex !== -1) { return {type_name: newName, type_id: classes[targetIndex].type_id}; }
                });
                let tclasses = result.filter((it) => it !== undefined);
                if (tclasses.length) {classes = tclasses;}
            } catch(e) {}
        }
        
        let filters = {};
        let nameObj = { class: 'class,剧情', area: 'area,地区', lang: 'lang,语言', year: 'year,年份', sort: 'by,排序' };
        for (let it of classes) {
            let idx = ktypeObj.type_list.findIndex((tls) => tls.type_id === it.type_id);
            let kflArr = ktypeObj.type_list[idx].filter_type_list;
            let filter_data = [];
            if (kflArr && kflArr.length) {
                filter_data = kflArr.map((jit) => {
                    let [kkey, kname] = nameObj[jit.name].split(',');
                    let kval = jit.list;
                    let kvalue = (kval && kval.length) ? kval.map((item) => { return {n: item, v: item}; }) : [];
                    return { key: kkey, name: kname, value: kvalue };
                });
            } else {
                filter_data = [];
            }
            filters[it.type_id] = filter_data.filter((item) => item.value.length > 0);
        }
        return JSON.stringify({ class: classes, filters: filters });
    } catch (e) {
        return JSON.stringify({ class: [], filters: {} });
    }
}

async function homeVod() {
    try {
        let khomeObj = kparam.initData;
        let VODS = khomeObj.recommend_list || [];
        khomeObj.type_list.forEach((item) => { if (Array.isArray(item.recommend_list) && item.recommend_list.length) { VODS = VODS.concat(item.recommend_list);}});
        VODS = filterSensitiveEntries(VODS);
        return JSON.stringify({ list: VODS });
    } catch (e) {
        return JSON.stringify({ list: [] });
    }
}

async function category(tid, pg, filter, extend) {
    try {
        pg = parseInt(pg, 10);
        if ( pg <= 0 || isNaN(pg) ) { pg = 1 }
        let fbody = {
            type_id: tid,
            class: extend?.class || '全部',
            area: extend?.area || '全部',
            lang: extend?.lang || '全部',
            year: extend?.year || '全部',
            sort: extend?.by || '最新',
            page: pg
        };
        let inputUrl = '/api.php/getappapi.index/typeFilterVodList';
        if (kparam.urlRp === '1') {inputUrl = inputUrl.replace('getappapi', 'qijiappapi');}
        let kcateObj = await getdata(inputUrl, fbody, 'form');
        let VODS = kcateObj.recommend_list || [];
        let pagecount = parseInt(kparam.pgcount, 10);
        if ( pagecount <= 0 || isNaN(pagecount) ) { pagecount = 0 }
        pagecount = pagecount || 999;
        return JSON.stringify({
            list: VODS,
            page: pg,
            pagecount: pagecount,
            limit: 30,
            total: 30*pagecount
        });
    } catch (e) {
        return JSON.stringify({
            list: [],
            page: 1,
            pagecount: 1,
            limit: 1,
            total: 1
        });
    }
}

async function search(wd, quick, pg) {
    try {
        pg = parseInt(pg, 10);
        if ( pg <= 0 || isNaN(pg) ) { pg = 1 }

        let fbody = {
            'keywords': wd,
            'type_id': 0,
            'page': pg,
        }

        if(kparam.search_verify){
            let verif = await Verification();
            if(!verif?.code){
                return { 'list': [] ,'error': '验证码获取失败-2'}
            }
            fbody.key = verif.uuid;
            fbody.code = verif.code;
        }

        let inputUrl = `/api.php/getappapi.index/searchList`;
        if (kparam.urlRp === '1') {inputUrl = inputUrl.replace('getappapi', 'qijiappapi');}
        let ksechObj = await getdata(kparam.host + inputUrl,fbody,'form',{...kparam.headers,'Content-Type': 'application/x-www-form-urlencoded'});

        let VODS = ksechObj.search_list || [];
        return JSON.stringify({
            list: VODS,
            page: pg,
            pagecount: 10,
            limit: 30,
            total: 300
        });
    } catch (e) {
        return JSON.stringify({
            list: [],
            page: 1,
            pagecount: 1,
            limit: 1,
            total: 1
        });
    }
}

async function detail(id) {
    try {
        let inputUrl = `/api.php/getappapi.index/vodDetail?vod_id=${id}`;
        if (kparam.urlRp === '1') {inputUrl = inputUrl.replace('getappapi', 'qijiappapi');}
        let kdetlObj = await getdata(inputUrl);
        let kvod = kdetlObj.vod;
        kdetlObj = sortByShowRules(kdetlObj);
        if (!kvod) {throw new Error();}
        let ktabs = kdetlObj.vod_play_list.map((it,idx) => { return /防走丢|群|www|官网|网站/i.test(it.player_info.show) ? `${kparam.LineName}超清${idx + 1}线` : it.player_info.show;});
        let countMap = {};
        ktabs.forEach((item, index) => {
            countMap[item] = (countMap[item] || 0) + 1;
            if (countMap[item] > 1) {
                ktabs[index] = `${item}${countMap[item]}`;
            }
        });

        let kurls = kdetlObj.vod_play_list.map((item) => {
            let parse_type = item?.player_info?.parse_type ?? '';
            let player_parse_type = item?.player_info?.player_parse_type ?? '';
            let kurl = item.urls.map((it) => { return `${it.name}$${it.from}@${it.url}@${it.token}@${item.player_info.parse}@${parse_type}@${player_parse_type}`; });
            return kurl.join('#');
        });

        let VOD = {
            vod_id: kvod.vod_id,
            vod_name: kvod.vod_name,
            vod_pic: kvod.vod_pic,
            type_name: kvod.vod_class || '未提供',
            vod_remarks: kvod.vod_remarks || '未提供',
            vod_year: kvod.vod_year || '20xx',
            vod_area: kvod.vod_area || '未提供',
            vod_lang: kvod.vod_lang || '未提供',
            vod_director: kvod.vod_director || '未提供',
            vod_actor: kvod.vod_actor || '未提供',
            vod_content: kvod.vod_content || '未提供',
            vod_play_from: ktabs.join('$$$'),
            vod_play_url: kurls.join('$$$')
        };
        return JSON.stringify({ list: [VOD] });
    } catch (e) {
        return JSON.stringify({ list: [] });
    }
}

async function getpurl(furl, fparse, ftoken) {
    try {
        furl = encodeURIComponent(encryptAes(furl));
        let inputUrl = `${HOST}/api.php/getappapi.index/vodParse?parse_api=${fparse}&url=${furl}&token=${ftoken}`;
        if (kparam.urlRp === '1') {inputUrl = inputUrl.replace('getappapi', 'qijiappapi');}
        furl = inputUrl;
        let fres = await request(furl);
        if (!fres) {throw new Error('获取播放响应数据失败');}
        let fresObj = JSON.parse(fres);
        let kdata = fresObj.data || '';
        if (!kdata) {throw new Error();}
        let decrypted = decryptAes(kdata);
        if (!decrypted) {throw new Error('解密失败');}
        kdata = JSON.parse(decrypted).json;
        return JSON.parse(kdata.replace(/\\/g,'')).url;
    } catch (e) {
        throw new Error()
    }
}

async function play(flag, id, flags) {
    try {
        let res = '', kp = 0;
        if (cachedPlayUrls[id]) {return cachedPlayUrls[id];}
        let [kfrom, kurl, ktoken, kparse, parse_type, player_parse_type] = id.split('@');
        if(parse_type === '0'){}
        else if(parse_type === '2'){kp = 1; kurl = kparse + kurl;}
        else if (/\.(m3u8|mp4|mkv)/.test(kurl)) {}
        else if (/zhibo|dplayer/.test(kfrom)) {}
        else if (/PTV/.test(kfrom)) {
            let [sid, nid] = kurl.match(/\d+/g);
            kurl = `https://m.jiabaide.cn/api/mw-movie/anonymous/v2/video/episode/url?clientType=3&id=${sid}&nid=${nid}`;
            let t = new Date().getTime();
            let sign = kurl.split('?')[1];
            sign = Crypto.SHA1(Crypto.MD5(`${sign}&key=cb808529bae6b6be45ecfab29a4889bc&t=${t}`).toString()).toString();
            res = await request(kurl, {
                'User-Agent': MOBILE_UA,
                't': t,
                'sign': sign
            });
            kurl = JSON.parse(res).data.list[0].url;
        } else if ((/qq|youku|iqiyi|mgtv|NBY|XB|bilibili/.test(kurl)) && kparam.gparse) {
            kurl = kparam.gparse + kurl;
            res = await request(kurl, def_header);
            kurl = JSON.parse(res).url;
        } else {
            if (!kparse) {
                kp = 1;
            } else if (player_parse_type === '2' && /^http/.test(kparse)) {
                kurl = kparse + kurl;
                res = await request(kurl, def_header);
                if (/<\s*html\s*([^>]*)>/i.test(res)){
                    print(res);
                    kp = 1;
                }
                kurl = JSON.parse(res).url;
            } else {
                kurl = await getpurl(kurl, kparse, ktoken);
            }
        }
        let playHeader = def_header;
        if(/mgtv\.com/.test(kurl)) {
            playHeader["User-Agent"] = 'MGDS/Android/2.0.5';
        }else if(/bilibili\.com/.test(kurl)) {
            playHeader.referrer = 'https://www.bilibili.com/';
            playHeader["User-Agent"] = MOBILE_UA;
        }else{
            playHeader["User-Agent"] = MOBILE_UA;
        }
        let playJson = JSON.stringify({ parse: kp, url: kurl, header: playHeader });
        cachedPlayUrls[id] = playJson;
        return playJson;
    } catch (e) {
        return JSON.stringify({ parse: 0, url: '', header: {} });
    }
}

function decodeBase64(str) {
    try {
        return Crypto.enc.Utf8.stringify(Crypto.enc.Base64.parse(str));
    } catch (e) {
        return str;
    }
}

function encryptAes(data, key, iv, typeHex) {
    try {
        typeHex = typeHex || false;
        key = key || kparam.key;
        iv = iv || kparam.iv;
        key = Crypto.enc.Utf8.parse(key);
        iv = Crypto.enc.Utf8.parse(iv);
        const encrypted = Crypto.AES.encrypt( data, key, {
            iv: iv,
            mode: Crypto.mode.CBC,
            padding: Crypto.pad.Pkcs7
        });
        return (typeHex) ? encrypted.ciphertext.toString(Crypto.enc.Hex) : encrypted.toString();
    } catch (e) {
        return null;
    }
}

function decryptAes(data, key, iv, typeHex) {
    try {
        typeHex = typeHex || false;
        key = key || kparam.key;
        iv = iv || kparam.iv;
        key = Crypto.enc.Utf8.parse(key);
        iv = Crypto.enc.Utf8.parse(iv);
        let kdata = (typeHex) ? {ciphertext: Crypto.enc.Hex.parse(data)} : data.replace(/^\uFEFF/,'').replace(/<.*>/g,'').replace(/[^A-Za-z0-9+/=]/g, '');
        const decrypted = Crypto.AES.decrypt( kdata, key, {
            iv: iv,
            mode: Crypto.mode.CBC,
            padding: Crypto.pad.Pkcs7
        });
        return decrypted.toString(Crypto.enc.Utf8);
    } catch (e) {
        return null;
    }
}

function sortByShowRules(data) {
    const rules = kparam.collation;
    const playList = data?.vod_play_list;
    if (!playList?.length || !rules?.length) return data;
    const ruleCache = Object.create(null);
    rules.forEach((rule, idx) => ruleCache[rule] = idx);
    const getPriority = show => {
        const matches = [];
        for (const [rule, idx] of Object.entries(ruleCache)) {
            if (show.includes(rule)) {matches.push(idx);}
        }
        if (matches.length > 0) {return Math.min(...matches);}
        return Number.MAX_SAFE_INTEGER;
    };
    playList.sort((a, b) => {
        const priorityA = getPriority(a.player_info.show);
        const priorityB = getPriority(b.player_info.show);
        return priorityA - priorityB;
    });

    return data;
}

function filterSensitiveEntries(list) {
    const sensitiveRegex = /广告|活动|破解版|用户必看|官网|网站|加[^群]群|防走丢/;
    if (!list || !Array.isArray(list)) {return list;}
    return list.filter(item => {
        if (item.vod_name && typeof item.vod_name === 'string') {
            return !sensitiveRegex.test(item.vod_name);
        }
        return true;
    });
}

function filterClass(rule, obj) {
    if (!obj || !Array.isArray(obj.type_list)) {return obj;}
    return {...obj, type_list: obj.type_list.filter(item => item.type_name !== rule)};
}

async function Verification() {
    const random_uuid = uuidv4();
    let base64Img = await request(`${kparam.host}${kparam.xurl}.verify/create?key=${random_uuid}`, kparam.headers,undefined,undefined,'tobase64');
    if (!base64Img) {return null;}
    let code = await request("https://api.nn.ci/ocr/b64/text",kparam.headers,base64Img,'raw');
    if (!code) {return null;}
    const cleanedCode = replace_code(code);
    if (!(cleanedCode.length === 4 && /^\d+$/.test(cleanedCode))) {return null;}
    return { uuid: random_uuid, code: cleanedCode };
}

function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function replace_code(text) {
    const replacements = { 'y': '9', '口': '0', 'q': '0', 'u': '0', 'o': '0', '>': '1', 'd': '0', 'b': '8','日':'8','已':'2','D':'0','五':'5'};
    if(text.length == 3) {text = text.replace('566', '5066');}
    return text.split('').map(c => replacements[c] || c).join('');
}

export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        homeVod: homeVod,
        category: category,
        search: search,
        detail: detail,
        play: play
    };
}
