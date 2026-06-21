globalThis.h_ost = 'https://film.symx.club';

var rule = {
    title: '木兮',
    host: h_ost,
    url: '/api/film/category/list?fyfilter',
    detailUrl: '/api/film/detail?id=fyid',
    searchUrl: '/api/film/search?keyword=**&pageNum=fypage&pageSize=10',
    filter_url: 'categoryId=fyclass&language={{fl.lang}}&pageNum=2fypage&pageSize=15&sort={{fl.by or updateTime}}&year={{fl.year}}',
    searchable: 2,
    quickSearch: 1,
    filterable: 0,
    headers: {
        'User-Agent': 'MOBILE_UA'
    },
    play_parse: true,
    search_match: true,
    class_name: '电视剧&电影&动漫&综艺&短剧',
    class_url: '1&2&4&3&5',
    推荐: $js.toString(() => {
        let d = [];
        let html = request(input + '/api/film/category');
        let categories = JSON.parse(html)
            .data;

        categories.forEach(category => {
            category.filmList.forEach(item => {
                let title = item.name;
                if (!/名称|排除/.test(title)) {
                    d.push({
                        title: title,
                        desc: item.updateStatus,
                        img: item.cover,
                        url: item.id,
                        content: item.blurb,

                    });
                }
            });
        });

        setResult(d);
    }),
    一级: $js.toString(() => {
        let d = [];
        let html = request(input);
        let data = JSON.parse(html)
            .data.list;
        data.forEach(item => {
            let title = item.name;
            if (!/名称|排除/.test(title)) {
                d.push({
                    title: title,
                    desc: item.updateStatus,
                    img: item.cover,
                    url: item.id,
                    content: item.blurb,

                });
            }
        });
        setResult(d);
    }),

    二级: $js.toString(() => {
    let html = request(input);
    let data = JSON.parse(html).data;

    // 类型映射
    let categoryMap = {
        1: "电视剧",
        2: "电影",
        3: "综艺",
        4: "动漫",
        5: "短剧"
    };
    let categoryName = categoryMap[data.categoryId] || "未知";

    // 从 input 中提取 orId（假设是 ?id=123）
    let orId = input.split('id=')[1];

    VOD = {
        vod_id: orId,
        vod_name: data.name,
        type_name: categoryName,
        vod_pic: data.cover,
        vod_remarks: data.updateStatus,
        vod_content: data.blurb
    };

    let playlist = data.playLineList || [];
    let playFrom = [];
    let playUrl = [];

    playlist.forEach(line => {
        playFrom.push(line.playerName);
        let lines = line.lines || [];
        let lineUrls = lines.map(tag => {
            let title = tag.name;
            let url = tag.id;
            return `${title}$${url}`;
        });
        playUrl.push(lineUrls.join("#"));
    });

    VOD.vod_play_from = playFrom.join("$$$");
    VOD.vod_play_url = playUrl.join("$$$");
}),


    搜索: $js.toString(() => {
        let d = [];
        let html = request(input);
        let data = JSON.parse(html)
            .data.list;
        data.forEach(item => {
            let title = item.name;
            d.push({
                title: title,
                desc: item.updateStatus,
                img: item.cover,
                url: item.id,
            });
        });
        setResult(d);
    }),
    lazy: $js.toString(() => {
        let purl = 'https://film.symx.club/api/line/play/parse?lineId=' + input;
        let html = request(purl);
        let url = JSON.parse(html)
            .data;
        input = {
            parse: 0,
            url: url
        };
    }),

}