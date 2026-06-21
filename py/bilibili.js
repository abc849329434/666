const axios = require("axios");
const querystring = require("querystring");

// 配置
const CONFIG = {
  HEADERS: {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
    "Referer": "https://www.bilibili.com"
  },
  API_BASE: "https://api.bilibili.com"
};

// 分类映射
const CATEGORIES = new Map([
  ["1", "番剧"],
  ["4", "国创"],
  ["2", "电影"],
  ["5", "电视剧"],
  ["7", "综艺"]
]);

// 复杂筛选配置
const FILTER_CONFIG = {
  "1": [
    { key: "season_version", name: "类型", value: [
      { v: '-1', n: "全部" }, { v: '1', n: "正片" }, { v: '2', n: "电影" }, { v: '3', n: "其他" }
    ]},
    { key: "area", name: "地区", value: [
      { v: '-1', n: "全部" }, { v: '2', n: "日本" }, { v: '3', n: "美国" },
      { v: "1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70", n: "其他" }
    ]},
    { key: "is_finish", name: "状态", value: [
      { v: '-1', n: "全部" }, { v: '1', n: "完结" }, { v: '0', n: "连载" }
    ]},
    { key: "copyright", name: "版权", value: [
      { v: '-1', n: "全部" }, { v: '3', n: "独家" }, { v: "1,2,4", n: "其他" }
    ]},
    { key: "season_status", name: "付费", value: [
      { v: '-1', n: "全部" }, { v: '1', n: "免费" }, { v: "2,6", n: "付费" }, { v: "4,6", n: "大会员" }
    ]},
    { key: "season_month", name: "季度", value: [
      { v: '-1', n: "全部" }, { v: '1', n: "1月" }, { v: '4', n: "4月" }, { v: '7', n: "7月" }, { v: '10', n: "10月" }
    ]},
    { key: "year", name: "年份", value: [
      { v: '-1', n: "全部" }, { v: "[2024,2025)", n: "2024" }, { v: "[2023,2024)", n: "2023" },
      { v: "[2022,2023)", n: "2022" }, { v: "[2021,2022)", n: "2021" }, { v: "[2020,2021)", n: "2020" },
      { v: "[2019,2020)", n: "2019" }, { v: "[2018,2019)", n: "2018" }, { v: "[2017,2018)", n: "2017" },
      { v: "[2016,2017)", n: "2016" }, { v: "[2015,2016)", n: "2015" }, { v: "[2010,2015)", n: "2014-2010" },
      { v: "[2005,2010)", n: "2009-2005" }, { v: "[2000,2005)", n: "2004-2000" }, { v: "[1990,2000)", n: "90年代" },
      { v: "[1980,1990)", n: "80年代" }, { v: "[,1980)", n: "更早" }
    ]},
    { key: "style_id", name: "风格", value: [
      { v: '-1', n: "全部" }, { v: '10010', n: "原创" }, { v: '10011', n: "漫画改" }, { v: '10012', n: "小说改" },
      { v: '10013', n: "游戏改" }, { v: '10102', n: "特摄" }, { v: '10015', n: "布袋戏" }, { v: '10016', n: "热血" },
      { v: '10017', n: "穿越" }, { v: '10018', n: "奇幻" }, { v: '10020', n: "战斗" }, { v: '10021', n: "搞笑" },
      { v: '10022', n: "日常" }, { v: '10023', n: "科幻" }, { v: '10024', n: "萌系" }, { v: '10025', n: "治愈" },
      { v: '10026', n: "校园" }, { v: '10027', n: "少儿" }, { v: '10028', n: "泡面" }, { v: '10029', n: "恋爱" },
      { v: '10030', n: "少女" }, { v: '10031', n: "魔法" }, { v: '10032', n: "冒险" }, { v: '10033', n: "历史" },
      { v: '10034', n: "架空" }, { v: '10035', n: "机战" }, { v: '10036', n: "神魔" }, { v: '10037', n: "声控" },
      { v: '10038', n: "运动" }, { v: '10039', n: "励志" }, { v: '10040', n: "音乐" }, { v: '10041', n: "推理" },
      { v: '10042', n: "社团" }, { v: '10043', n: "智斗" }, { v: '10044', n: "催泪" }, { v: '10045', n: "美食" },
      { v: '10046', n: "偶像" }, { v: '10047', n: "乙女" }, { v: '10048', n: "职场" }
    ]}
  ],
  "4": [
    { key: "season_version", name: "类型", value: [
      { v: '-1', n: "全部" }, { v: '1', n: "正片" }, { v: '2', n: "电影" }, { v: '3', n: "其他" }
    ]},
    { key: "area", name: "地区", value: [
      { v: '-1', n: "全部" }, { v: '2', n: "日本" }, { v: '3', n: "美国" },
      { v: "1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70", n: "其他" }
    ]},
    { key: "is_finish", name: "状态", value: [
      { v: '-1', n: "全部" }, { v: '1', n: "完结" }, { v: '0', n: "连载" }
    ]},
    { key: "copyright", name: "版权", value: [
      { v: '-1', n: "全部" }, { v: '3', n: "独家" }, { v: "1,2,4", n: "其他" }
    ]},
    { key: "season_status", name: "付费", value: [
      { v: '-1', n: "全部" }, { v: '1', n: "免费" }, { v: "2,6", n: "付费" }, { v: "4,6", n: "大会员" }
    ]},
    { key: "year", name: "年份", value: [
      { v: '-1', n: "全部" }, { v: "[2024,2025)", n: "2024" }, { v: "[2023,2024)", n: "2023" },
      { v: "[2022,2023)", n: "2022" }, { v: "[2021,2022)", n: "2021" }, { v: "[2020,2021)", n: "2020" },
      { v: "[2019,2020)", n: "2019" }, { v: "[2018,2019)", n: "2018" }, { v: "[2017,2018)", n: "2017" },
      { v: "[2016,2017)", n: "2016" }, { v: "[2015,2016)", n: "2015" }, { v: "[2010,2015)", n: "2014-2010" },
      { v: "[2005,2010)", n: "2009-2005" }, { v: "[2000,2005)", n: "2004-2000" }, { v: "[1990,2000)", n: "90年代" },
      { v: "[1980,1990)", n: "80年代" }, { v: "[,1980)", n: "更早" }
    ]},
    { key: "style_id", name: "风格", value: [
      { v: '-1', n: "全部" }, { v: '10010', n: "原创" }, { v: '10011', n: "漫画改" }, { v: '10012', n: "小说改" },
      { v: '10013', n: "游戏改" }, { v: '10014', n: "动态漫" }, { v: '10015', n: "布袋戏" }, { v: '10016', n: "热血" },
      { v: '10018', n: "奇幻" }, { v: '10019', n: "玄幻" }, { v: '10020', n: "战斗" }, { v: '10021', n: "搞笑" },
      { v: '10078', n: "武侠" }, { v: '10022', n: "日常" }, { v: '10023', n: "科幻" }, { v: '10024', n: "萌系" },
      { v: '10025', n: "治愈" }, { v: '10057', n: "悬疑" }, { v: '10026', n: "校园" }, { v: '10027', n: "少儿" },
      { v: '10028', n: "泡面" }, { v: '10029', n: "恋爱" }, { v: '10030', n: "少女" }, { v: '10031', n: "魔法" },
      { v: '10033', n: "历史" }, { v: '10035', n: "机战" }, { v: '10036', n: "神魔" }, { v: '10037', n: "声控" },
      { v: '10038', n: "运动" }, { v: '10039', n: "励志" }, { v: '10040', n: "音乐" }, { v: '10041', n: "推理" },
      { v: '10042', n: "社团" }, { v: '10043', n: "智斗" }, { v: '10044', n: "催泪" }, { v: '10045', n: "美食" },
      { v: '10046', n: "偶像" }, { v: '10047', n: "乙女" }, { v: '10048', n: "职场" }, { v: '10049', n: "古风" }
    ]}
  ],
  "2": [
    { key: "area", name: "地区", value: [
      { v: '-1', n: "全部" }, { v: '1', n: "中国大陆" }, { v: "6,7", n: "中国港台" }, { v: '3', n: "美国" },
      { v: '2', n: "日本" }, { v: '8', n: "韩国" }, { v: '9', n: "法国" }, { v: '4', n: "英国" },
      { v: '15', n: "德国" }, { v: '10', n: "泰国" }, { v: '35', n: "意大利" }, { v: '13', n: "西班牙" },
      { v: "5,11,12,14,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70", n: "其他" }
    ]},
    { key: "season_status", name: "付费", value: [
      { v: '-1', n: "全部" }, { v: '1', n: "免费" }, { v: "2,6", n: "付费" }, { v: "4,6", n: "大会员" }
    ]},
    { key: "style_id", name: "风格", value: [
      { v: '-1', n: "全部" }, { v: '10104', n: "短片" }, { v: '10050', n: "剧情" }, { v: '10051', n: "喜剧" },
      { v: '10052', n: "爱情" }, { v: '10053', n: "动作" }, { v: '10054', n: "恐怖" }, { v: '10023', n: "科幻" },
      { v: '10055', n: "犯罪" }, { v: '10056', n: "惊悚" }, { v: '10057', n: "悬疑" }, { v: '10018', n: "奇幻" },
      { v: '10058', n: "战争" }, { v: '10059', n: "动画" }, { v: '10060', n: "传记" }, { v: '10061', n: "家庭" },
      { v: '10062', n: "歌舞" }, { v: '10033', n: "历史" }, { v: '10032', n: "冒险" }, { v: '10063', n: "纪实" },
      { v: '10064', n: "灾难" }, { v: '10011', n: "漫画改" }, { v: '10012', n: "小说改" }
    ]},
    { key: "release_date", name: "年份", value: [
      { v: '-1', n: "全部" }, { v: "[2024-01-01 00:00:00,2025-01-01 00:00:00)", n: "2024" },
      { v: "[2023-01-01 00:00:00,2024-01-01 00:00:00)", n: "2023" },
      { v: "[2022-01-01 00:00:00,2023-01-01 00:00:00)", n: "2022" },
      { v: "[2021-01-01 00:00:00,2022-01-01 00:00:00)", n: "2021" },
      { v: "[2020-01-01 00:00:00,2021-01-01 00:00:00)", n: "2020" },
      { v: "[2019-01-01 00:00:00,2020-01-01 00:00:00)", n: "2019" },
      { v: "[2018-01-01 00:00:00,2019-01-01 00:00:00)", n: "2018" },
      { v: "[2017-01-01 00:00:00,2018-01-01 00:00:00)", n: "2017" },
      { v: "[2016-01-01 00:00:00,2017-01-01 00:00:00)", n: "2016" },
      { v: "[2010-01-01 00:00:00,2016-01-01 00:00:00)", n: "2015-2010" },
      { v: "[2005-01-01 00:00:00,2010-01-01 00:00:00)", n: "2009-2005" },
      { v: "[2000-01-01 00:00:00,2005-01-01 00:00:00)", n: "2004-2000" },
      { v: "[1990-01-01 00:00:00,2000-01-01 00:00:00)", n: "90年代" },
      { v: "[1980-01-01 00:00:00,1990-01-01 00:00:00)", n: "80年代" },
      { v: "[,1980-01-01 00:00:00)", n: "更早" }
    ]}
  ],
  "5": [
    { key: "area", name: "地区", value: [
      { v: '-1', n: "全部" }, { v: "1,6,7", n: "中国" }, { v: '2', n: "日本" }, { v: '3', n: "美国" },
      { v: '4', n: "英国" }, { v: '10', n: "泰国" },
      { v: "5,8,9,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70", n: "其他" }
    ]},
    { key: "season_status", name: "付费", value: [
      { v: '-1', n: "全部" }, { v: '1', n: "免费" }, { v: "2,6", n: "付费" }, { v: "4,6", n: "大会员" }
    ]},
    { key: "style_id", name: "风格", value: [
      { v: '-1', n: "全部" }, { v: '10021', n: "搞笑" }, { v: '10018', n: "奇幻" }, { v: '10058', n: "战争" },
      { v: '10078', n: "武侠" }, { v: '10079', n: "青春" }, { v: '10103', n: "短剧" }, { v: '10080', n: "都市" },
      { v: '10081', n: "古装" }, { v: '10082', n: "谍战" }, { v: '10083', n: "经典" }, { v: '10084', n: "情感" },
      { v: '10057', n: "悬疑" }, { v: '10039', n: "励志" }, { v: '10085', n: "神话" }, { v: '10017', n: "穿越" },
      { v: '10086', n: "年代" }, { v: '10087', n: "农村" }, { v: '10088', n: "刑侦" }, { v: '10050', n: "剧情" },
      { v: '10061', n: "家庭" }, { v: '10033', n: "历史" }, { v: '10089', n: "军旅" }, { v: '10023', n: "科幻" }
    ]},
    { key: "release_date", name: "年份", value: [
      { v: '-1', n: "全部" }, { v: "[2024-01-01 00:00:00,2025-01-01 00:00:00)", n: "2024" },
      { v: "[2023-01-01 00:00:00,2024-01-01 00:00:00)", n: "2023" },
      { v: "[2022-01-01 00:00:00,2023-01-01 00:00:00)", n: "2022" },
      { v: "[2021-01-01 00:00:00,2022-01-01 00:00:00)", n: "2021" },
      { v: "[2020-01-01 00:00:00,2021-01-01 00:00:00)", n: "2020" },
      { v: "[2019-01-01 00:00:00,2020-01-01 00:00:00)", n: "2019" },
      { v: "[2018-01-01 00:00:00,2019-01-01 00:00:00)", n: "2028" },
      { v: "[2017-01-01 00:00:00,2018-01-01 00:00:00)", n: "2017" },
      { v: "[2016-01-01 00:00:00,2017-01-01 00:00:00)", n: "2016" },
      { v: "[2010-01-01 00:00:00,2016-01-01 00:00:00)", n: "2015-2010" },
      { v: "[2005-01-01 00:00:00,2010-01-01 00:00:00)", n: "2009-2005" },
      { v: "[2000-01-01 00:00:00,2005-01-01 00:00:00)", n: "2004-2000" },
      { v: "[1990-01-01 00:00:00,2000-01-01 00:00:00)", n: "90年代" },
      { v: "[1980-01-01 00:00:00,1990-01-01 00:00:00)", n: "80年代" },
      { v: "[,1980-01-01 00:00:00)", n: "更早" }
    ]}
  ],
  "7": [
    { key: "season_status", name: "付费", value: [
      { v: '-1', n: "全部" }, { v: '1', n: "免费" }, { v: "2,6", n: "付费" }, { v: "4,6", n: "大会员" }
    ]},
    { key: "style_id", name: "风格", value: [
      { v: '-1', n: "全部" }, { v: '10040', n: "音乐" }, { v: '10090', n: "访谈" }, { v: '10091', n: "脱口秀" },
      { v: '10092', n: "真人秀" }, { v: '10094', n: "选秀" }, { v: '10045', n: "美食" }, { v: '10095', n: "旅游" },
      { v: '10098', n: "晚会" }, { v: '10096', n: "演唱会" }, { v: '10084', n: "情感" }, { v: '10051', n: "喜剧" },
      { v: '10097', n: "亲子" }, { v: '10100', n: "文化" }, { v: '10048', n: "职场" }, { v: '10069', n: "萌宠" },
      { v: '10099', n: "养成" }
    ]}
  ]
};

// 移除HTML标签
const removeHtmlTags = (text) => {
  if (!text) return "";
  return text.replace(/<[^>]+>/g, "");
};

// 获取当前年份
const getCurrentYear = () => {
  return new Date().getFullYear();
};

// 首页分类
const _home = async (filter = false) => {
  const classes = Array.from(CATEGORIES, ([type_id, type_name]) => ({
    type_id,
    type_name
  }));

  const filters = {};
  
  if (filter) {
    // 复制筛选配置
    for (const [typeId, filterConfig] of Object.entries(FILTER_CONFIG)) {
      filters[typeId] = JSON.parse(JSON.stringify(filterConfig));
      
      // 动态添加年份
      const currentYear = getCurrentYear();
      for (const filterItem of filters[typeId]) {
        if (filterItem.key === 'year' || filterItem.key === 'release_date') {
          // 查找现有的最大年份
          let maxYear = 0;
          for (const value of filterItem.value) {
            if (value.n !== "全部" && value.n !== "更早") {
              const yearMatch = value.n.match(/^\d{4}$/);
              if (yearMatch) {
                const year = parseInt(yearMatch[0]);
                if (year > maxYear) {
                  maxYear = year;
                }
              }
            }
          }
          
          // 添加缺失的年份
          if (maxYear > 0 && maxYear < currentYear) {
            const maxYearIndex = filterItem.value.findIndex(v => v.n === maxYear.toString());
            if (maxYearIndex !== -1) {
              for (let year = currentYear; year > maxYear; year--) {
                if (filterItem.key === 'year') {
                  filterItem.value.splice(maxYearIndex, 0, {
                    v: `[${year},${year + 1})`,
                    n: year.toString()
                  });
                } else if (filterItem.key === 'release_date') {
                  filterItem.value.splice(maxYearIndex, 0, {
                    v: `[${year}-01-01 00:00:00,${year + 1}-01-01 00:00:00)`,
                    n: year.toString()
                  });
                }
              }
            }
          }
        }
      }
    }
  }

  return {
    class: classes,
    filters: filter ? filters : {},
    list: []
  };
};

// 首页推荐视频
const _homeVod = async () => {
  return await _category({ id: "1", page: 1, filter: {} });
};

// 分类分页
const _category = async ({ id, page, filter = {} }) => {
  try {
    const pageNum = parseInt(page) || 1;
    
    // 构建API参数
    const baseParams = {
      order: "2",  // 排序方式
      sort: "0",   // 排序字段
      pagesize: "20",  // 每页数量
      type: "1",  // 类型
      st: id,  // 分类ID
      season_type: id,  // 番剧类型
      page: pageNum
    };
    
    // 添加筛选参数
    const extParams = {};
    for (const [key, value] of Object.entries(filter)) {
      if (value && value !== '-1' && value !== '') {
        extParams[key] = value;
      }
    }
    
    // 构建URL
    const params = { ...baseParams, ...extParams };
    const queryString = Object.keys(params)
      .map(key => `${key}=${encodeURIComponent(params[key])}`)
      .join('&');
    
    const url = `${CONFIG.API_BASE}/pgc/season/index/result?${queryString}`;
    
    const { data } = await axios.get(url, {
      headers: CONFIG.HEADERS
    });

    if (data.code !== 0) {
      throw new Error(`API错误: ${data.message}`);
    }

    const videos = [];
    const vodList = data.data.list || [];
    
    for (const vod of vodList) {
      const seasonId = vod.season_id?.toString() || "";
      const title = removeHtmlTags(vod.title || "");
      const img = vod.cover || "";
      const remark = vod.index_show || "";
      
      videos.push({
        vod_id: seasonId,
        vod_name: title,
        vod_pic: img,
        vod_remarks: remark
      });
    }

    const hasNext = data.data.has_next === 1;
    const pageCount = hasNext ? pageNum + 1 : pageNum;
    const total = videos.length;

    return {
      list: videos,
      page: pageNum,
      pagecount: pageCount,
      limit: 20,
      total: total
    };
  } catch (error) {
    console.error("分类数据获取失败:", error.message);
    return {
      list: [],
      page: parseInt(page) || 1,
      pagecount: 1,
      limit: 20,
      total: 0
    };
  }
};

// 视频详情
const _detail = async ({ id }) => {
  try {
    const url = `${CONFIG.API_BASE}/pgc/view/web/season?season_id=${id}`;
    const { data } = await axios.get(url, {
      headers: CONFIG.HEADERS
    });

    if (data.code !== 0) {
      throw new Error(`API错误: ${data.message}`);
    }

    const result = data.result;
    if (!result) {
      throw new Error("未找到视频详情");
    }

    // 构建播放列表
    const episodes = result.episodes || [];
    let playUrl = "";
    
    for (const episode of episodes) {
      const eid = episode.id;
      const cid = episode.cid;
      const name = removeHtmlTags(episode.share_copy || "")
        .replace(/#/g, "-")
        .replace(/\$/g, "*");
      
      // 格式化时长
      let remark = "";
      if (episode.duration) {
        const durationSeconds = episode.duration / 1000;
        const hours = Math.floor(durationSeconds / 3600);
        const minutes = Math.floor((durationSeconds % 3600) / 60);
        const seconds = Math.floor(durationSeconds % 60);
        
        if (hours > 0) {
          remark = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        } else {
          remark = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
      }
      
      playUrl += `[${remark}]/${name}$${eid}_${cid}#`;
    }

    // 移除最后一个#
    if (playUrl.endsWith("#")) {
      playUrl = playUrl.slice(0, -1);
    }

    const vod = {
      vod_id: id,
      vod_name: removeHtmlTags(result.title || ""),
      vod_pic: result.cover || "",
      type_name: result.share_sub_title || "",
      vod_actor: (result.actors || "").replace(/\n/g, "，"),
      vod_content: removeHtmlTags(result.evaluate || ""),
      vod_play_from: "B站番剧",
      vod_play_url: playUrl
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
        vod_play_from: "B站番剧",
        vod_play_url: ""
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
    const url = `${CONFIG.API_BASE}/x/web-interface/search/type?search_type=media_bangumi&keyword=${encodeURIComponent(wd)}&page=${result.page}`;
    
    const { data } = await axios.get(url, {
      headers: CONFIG.HEADERS
    });

    if (data.code !== 0 || !data.data.result) {
      return result;
    }

    const vodList = data.data.result;
    const videos = [];
    
    for (const vod of vodList) {
      const seasonId = vod.season_id?.toString() || "";
      const title = removeHtmlTags(vod.title || "");
      
      // 简单的相关性检查
      if (!title.includes(wd) && title.toLowerCase().indexOf(wd.toLowerCase()) === -1) {
        continue;
      }
      
      const img = vod.eps?.[0]?.cover || "";
      const remark = removeHtmlTags(vod.index_show || "");
      
      videos.push({
        vod_id: seasonId,
        vod_name: title,
        vod_pic: img,
        vod_remarks: remark
      });
    }

    result.list = videos;
    result.total = videos.length;
    result.pagecount = Math.ceil(videos.length / 20) || 1;

    return result;
  } catch (error) {
    console.error("搜索失败:", error.message);
    return result;
  }
};

// 播放解析
const _play = async ({ id }, app) => {
  try {
    const [episodeId, cid] = id.split("_");
    
    if (!episodeId || !cid) {
      throw new Error("无效的播放ID格式");
    }

    const url = `${CONFIG.API_BASE}/pgc/player/web/playurl?ep_id=${episodeId}&cid=${cid}&qn=120&fnval=4048&fnver=0&fourk=1`;
    
    // 尝试获取播放地址
    const { data } = await axios.get(url, {
      headers: CONFIG.HEADERS
    });

    if (data.code !== 0) {
      throw new Error(`获取播放地址失败: ${data.message}`);
    }

    // 原代码通过代理服务器处理，这里简化处理
    const playUrl = `http://127.0.0.1:9978/proxy?do=py&type=mpd&url=${encodeURIComponent(url)}&aid=${episodeId}&cid=${cid}`;
    
    return {
      parse: 0,
      jx: 0,
      url: playUrl,
      header: CONFIG.HEADERS,
      format: "application/dash+xml"
    };
  } catch (error) {
    console.error("播放解析失败:", error.message);
    return {
      parse: 1,
      jx: 1,
      url: id,
      header: CONFIG.HEADERS
    };
  }
};

// 元数据
const meta = {
  key: "bilibili",
  name: "B站番剧[官]",
  type: 4,
  api: "/video/bilibili",
  searchable: 1,
  quickSearch: 1,
  changeable: 0,
  filterable: 1
};

// 主函数
module.exports = async (app, opt) => {
  app.get(meta.api, async (req, reply) => {
    const { 
      ac,      // 动作: detail, category, search
      t,       // 分类ID
      pg,      // 页码
      ids,     // 视频ID
      play,    // 播放ID (格式: episodeId_cid)
      wd,      // 搜索关键词
      page,    // 页码别名
      extend,  // 筛选参数
      filter   // 是否显示筛选条件
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
      const filterParams = extend ? JSON.parse(extend) : {};
      return await _category({ 
        id: t, 
        page: pg || page || 1,
        filter: filterParams
      });
    }
    
    // 视频详情
    if (ac === "detail" && ids) {
      return await _detail({ id: ids });
    }
    
    // 默认首页（分类+筛选条件）
    return await _home(filter === "1");
  });

  // 添加到站点列表
  if (opt && opt.sites) {
    opt.sites.push(meta);
  }
  
  return meta;
};
