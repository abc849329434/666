const axios = require("axios");

const HOST = "http://asp.xpgtv.com";
const HEADERS = {
  "User-Agent": "okhttp/3.12.11"
};

// 分类映射（原代码是动态获取的，这里可以保持动态，但提供默认映射）
const DEFAULT_CATEGORIES = new Map([
  ["1", "电影"],
  ["2", "电视剧"],
  ["3", "综艺"],
  ["4", "动漫"],
  ["5", "纪录片"],
  ["6", "国产剧"],
  ["7", "美剧"],
  ["8", "韩剧"],
  ["9", "日剧"],
  ["10", "港剧"],
  ["11", "台剧"],
  ["12", "泰剧"],
  ["13", "英剧"],
  ["14", "其他"],
  ["15", "微电影"]
]);

// 筛选条件映射
const FILTER_MAP = {
  "classes": "类型",
  "areas": "地区",
  "years": "年份", 
  "sortby": "排序"
};

// 排序选项
const SORT_OPTIONS = ["时间", "人气", "评分"];

// 首页
const _home = async () => {
  try {
    const { data } = await axios.get(`${HOST}/api.php/v2.vod/androidtypes`, {
      headers: HEADERS
    });

    const categories = [];
    const filters = {};

    data.data.forEach(item => {
      const typeId = item.type_id.toString();
      
      // 分类
      categories.push({
        type_id: typeId,
        type_name: item.type_name
      });

      // 筛选条件
      const filterArray = [];
      for (const key in FILTER_MAP) {
        if (item[key] && item[key].length > 1) {
          const values = [];
          item[key].forEach((val, idx) => {
            const vStr = val.toString().trim();
            if (vStr !== "") {
              values.push({
                n: key === "sortby" ? SORT_OPTIONS[idx] || vStr : vStr,
                v: vStr
              });
            }
          });
          
          // 修正键名
          const filterKey = key === "areas" ? "areaes" : (key === "years" ? "yeares" : key);
          filterArray.push({
            key: filterKey,
            name: FILTER_MAP[key],
            value: values
          });
        }
      }
      
      // 添加排序选项
      filterArray.push({
        key: "sortby",
        name: "排序",
        value: SORT_OPTIONS.map((opt, idx) => ({
          n: opt,
          v: ["updatetime", "hits", "score"][idx] || opt
        }))
      });

      filters[typeId] = filterArray;
    });

    return {
      class: categories,
      filters: filters,
      list: []
    };
  } catch (error) {
    console.error("首页数据获取失败:", error.message);
    return {
      class: Array.from(DEFAULT_CATEGORIES, ([type_id, type_name]) => ({
        type_id,
        type_name
      })),
      filters: {},
      list: []
    };
  }
};

// 首页推荐视频
const _homeVod = async () => {
  try {
    const { data } = await axios.get(`${HOST}/api.php/v2.main/androidhome`, {
      headers: HEADERS
    });

    const videos = [];
    if (data.data && data.data.list) {
      data.data.list.forEach(item => {
        if (item.list && Array.isArray(item.list)) {
          item.list.forEach(vod => {
            const remarks = vod.updateInfo ? `更新至${vod.updateInfo}` : (vod.score ? vod.score.toString() : "");
            videos.push({
              vod_id: vod.id.toString(),
              vod_name: vod.name,
              vod_pic: vod.pic,
              vod_remarks: remarks
            });
          });
        }
      });
    }

    return {
      list: videos
    };
  } catch (error) {
    console.error("首页推荐获取失败:", error.message);
    return { list: [] };
  }
};

// 分类分页
const _category = async ({ id, page, filter = {} }) => {
  const params = {
    page: page || 1,
    type: id,
    area: filter.areaes || "",
    year: filter.yeares || "",
    sortby: filter.sortby || "",
    class: filter.classes || ""
  };

  // 构建查询字符串
  const query = Object.keys(params)
    .filter(key => params[key] && params[key] !== "")
    .map(key => `${key}=${encodeURIComponent(params[key])}`)
    .join("&");

  try {
    const { data } = await axios.get(`${HOST}/api.php/v2.vod/androidfilter10086?${query}`, {
      headers: HEADERS
    });

    const list = [];
    if (data.data && Array.isArray(data.data)) {
      data.data.forEach(vod => {
        const remarks = vod.updateInfo ? `更新至${vod.updateInfo}` : (vod.score ? `评分:${vod.score}` : "");
        list.push({
          vod_id: vod.id.toString(),
          vod_name: vod.name,
          vod_pic: vod.pic,
          vod_remarks: remarks,
          vod_year: vod.year || "",
          vod_area: vod.area || "",
          vod_content: vod.note || ""
        });
      });
    }

    return {
      list,
      page: parseInt(page) || 1,
      pagecount: 9999, // 原代码固定值
      limit: 90,
      total: 999999
    };
  } catch (error) {
    console.error("分类数据获取失败:", error.message);
    return {
      list: [],
      page: parseInt(page) || 1,
      pagecount: 1,
      limit: 90,
      total: 0
    };
  }
};

// 详情
const _detail = async ({ id }) => {
  try {
    const { data } = await axios.get(`${HOST}/api.php/v3.vod/androiddetail2?vod_id=${id}`, {
      headers: HEADERS
    });

    if (!data.data) {
      throw new Error("未找到视频详情");
    }

    const vodData = data.data;
    
    // 过滤掉包含"及时雨"的选集
    const filteredUrls = vodData.urls 
      ? vodData.urls.filter(item => !item.key.includes("及时雨"))
      : [];
    
    // 构建播放列表
    const playList = filteredUrls.map(item => 
      `${item.key}$${item.url}`
    ).join("#");

    const vod = {
      vod_id: id,
      vod_name: vodData.name,
      vod_year: vodData.year,
      vod_area: vodData.area,
      vod_lang: vodData.lang,
      vod_actor: vodData.actor,
      vod_director: vodData.director,
      vod_content: vodData.content || "暂无简介",
      vod_pic: vodData.pic || "",
      vod_remarks: vodData.updateInfo || "",
      vod_play_from: "书生精选线路",
      vod_play_url: playList
    };

    return {
      list: [vod]
    };
  } catch (error) {
    console.error("详情获取失败:", error.message);
    return {
      list: [{
        vod_id: id,
        vod_name: "视频信息获取失败",
        vod_content: "请检查视频ID是否正确",
        vod_play_from: "书生影视",
        vod_play_url: `全片$${HOST}/api.php/play/${id}`
      }]
    };
  }
};

// 搜索
const _search = async ({ page, wd }) => {
  const result = {
    list: [],
    page: parseInt(page) || 1,
    pagecount: 1,
    total: 0
  };

  try {
    const { data } = await axios.get(
      `${HOST}/api.php/v2.vod/androidsearch10086?page=${result.page}&wd=${encodeURIComponent(wd)}`,
      { headers: HEADERS }
    );

    if (data.data && Array.isArray(data.data)) {
      result.list = data.data.map(vod => ({
        vod_id: vod.id.toString(),
        vod_name: vod.name,
        vod_pic: vod.pic,
        vod_remarks: vod.updateInfo ? `更新至${vod.updateInfo}` : (vod.score ? `评分:${vod.score}` : ""),
        vod_year: vod.year || "",
        vod_content: vod.note || ""
      }));
      
      result.total = data.total || data.data.length;
      result.pagecount = Math.ceil(result.total / 90) || 1;
    }
  } catch (error) {
    console.error("搜索失败:", error.message);
  }

  return result;
};

// 播放解析
const _play = async ({ id }, app) => {
  // 播放地址处理
  let playUrl = id;
  if (!id.startsWith("http")) {
    playUrl = `http://c.xpgtv.net/m3u8/${id}.m3u8`;
  }

  // 1.5.7版本播放头
  const playHeader = {
    'user_id': 'XPGBOX',
    'token2': 'SnAXiSW8vScXE0Z9aDOnK5xffbO75w1+uPom3WjnYfVEA1oWtUdi2Ihy1N8=',
    'version': 'XPGBOX com.phoenix.tv1.5.7',
    'hash': 'd78a',
    'screenx': '2345',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'token': 'ElEDlwCVgXcFHFhddiq2JKteHofExRBUrfNlmHrWetU3VVkxnzJAodl52N9EUFS+Dig2A/fBa/V9RuoOZRBjYvI+GW8kx3+xMlRecaZuECdb/3AdGkYpkjW3wCnpMQxf8vVeCz5zQLDr8l8bUChJiLLJLGsI+yiNskiJTZz9HiGBZhZuWh1mV1QgYah5CLTbSz8=',
    'timestamp': '1743060300',
    'screeny': '1065',
    'Accept': '*/*',
    'Connection': 'keep-alive'
  };

  // 尝试使用解析器
  if (app && app.parse_fish) {
    try {
      const result = await app.parse_fish({ id: playUrl });
      if (result && result.url) {
        return {
          url: result.url,
          parse: 0,
          jx: 0,
          header: playHeader
        };
      }
    } catch (e) {
      console.error("解析器失败:", e.message);
    }
  }

  // 直接返回原始地址
  return {
    url: playUrl,
    parse: 0,
    jx: 1,
    header: playHeader
  };
};

// 元数据
const meta = {
  key: "xpg",
  name: "书生影视[官]",
  type: 4,
  api: "/video/xpg",
  searchable: 1,
  quickSearch: 1,
  changeable: 0,
  filterable: 1  // 支持筛选
};

// 主函数
module.exports = async (app, opt) => {
  app.get(meta.api, async (req, reply) => {
    const { 
      ac,      // 动作: detail, category, search
      t,       // 分类ID
      pg,      // 页码
      ids,     // 视频ID
      play,    // 播放ID
      wd,      // 搜索关键词
      page,    // 页码别名
      extend   // 筛选参数
    } = req.query;
    
    // 播放解析
    if (play) {
      return await _play({ id: play }, app);
    }
    
    // 搜索
    if (wd) {
      return await _search({ 
        page: pg || page || 1, 
        wd: decodeURIComponent(wd) 
      });
    }
    
    // 首页推荐
    if (ac === "home") {
      return await _homeVod();
    }
    
    // 分类列表（带筛选）
    if (ac === "detail" && t) {
      const filter = extend ? JSON.parse(extend) : {};
      return await _category({ 
        id: t, 
        page: pg || page || 1,
        filter 
      });
    }
    
    // 视频详情
    if (ac === "detail" && ids) {
      return await _detail({ id: ids });
    }
    
    // 默认首页（分类+筛选条件）
    return await _home();
  });

  // 添加到站点列表
  if (opt && opt.sites) {
    opt.sites.push(meta);
  }
  
  return meta;
};
