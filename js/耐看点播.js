var rule = {
  title: '耐看点播',
  host: 'https://nkvod.me/',
  class_name: '电影&电视剧&综艺&动漫',
  class_url: '1&2&3&4',
  searchUrl: '/nk/**----------fypage---.html',
  searchable: 2,
  quickSearch: 0,
  headers: {
    'User-Agent': 'MOBILE_UA',
  },
  url: '/show/fyclass--------fypage---.html',
  filterable: 0,
  filter_url: '',
  filter: {},
  filter_def: {},
  detailUrl: '/index.php/vod/detail/id/fyid.html',
  play_parse: true,
  lazy: `js:
    let html = request(input);
    let iframeSrc = html.match(/iframe.*?src="(.*?)"/i)[1];
    if (iframeSrc.includes('nkvod2.php?url=')) {
      let encryptedUrl = iframeSrc.split('url=')[1];
      let contentUrl = HOST + 'content.php?url=' + encryptedUrl;
      let realUrl = request(contentUrl, { headers: { 'Referer': HOST } });
      input = { parse: 0, jx: 0, url: realUrl };
    } else {
      let hconf = html.match(/r player_.*?=(.*?)</)[1];
      let json = JSON5.parse(hconf);
      let url = json.url;
      if (json.encrypt == '1') {
        url = unescape(url);
      } else if (json.encrypt == '2') {
        url = unescape(base64Decode(url));
      }
      if (/\.(m3u8|mp4|m4a|mp3)/.test(url)) {
        input = { parse: 0, jx: 0, url: url };
      } else {
        input = url && url.startsWith('http') && tellIsJx(url) ? {parse:0,jx:1,url:url} : input;
      }
    }
  `,
  limit: 6,
  推荐: '.public-list-box;a&&title;img&&data-src;.public-list-subtitle&&Text;a&&href',
  一级: '.box-width .public-list-box;.time-title&&Text;img&&data-src;.public-list-subtitle&&Text;a&&href',
  二级: {
    title: '.slide-info-title&&Text;.slide-info-remarks:eq(3)&&Text',
    img: '.lazy&&data-src',
    desc: '.slide-info&&Text;.slide-info-remarks:eq(0)&&Text;.slide-info-remarks:eq(1)&&Text;.slide-info:eq(1)--strong&&Text;.info-parameter&&ul&&li:eq(3)&&Text',
    content: '#height_limit&&Text',
    tabs: '.anthology-tab a',
    tab_text: 'a--span&&Text',
    lists: '.anthology-list-play:eq(#id) li',
  },
  搜索: '.row-right .public-list-box;.thumb-txt.cor4&&Text;img&&data-src;.public-list-prb&&Text;a&&href',
};