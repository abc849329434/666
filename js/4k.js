/*
@header({
  searchable: 1,
  filterable: 0,
  quickSearch: 0,
  title: '4k影视'
})
*/

var rule = {
	title: '4k影视',
	host: 'https://4kvm.site',
	searchable: 1,
	quickSearch: 0,
	filterable: 0,
	url: '/movie/page/fypage/',
	class_name: "首页&电影&电视剧&高清电影&热门播放",
	class_url: "movie&tv&anime&variety",
	searchUrl: '/search/**/',
	play_parse: true,
	limit: 6,
	推荐: async function () {
        let {input,pdfa,pdfh,pd} = this;
        let html = await request(input);
        let d = [];
        let data = pdfa(html, '.movie-list .movie-item');
        data.forEach((it) => {
            d.push({
                title: pdfh(it, '.movie-title&&Text'),
                pic_url: pd(it, '.movie-poster&&src'),
                desc: pdfh(it, '.movie-info&&Text'),
                url: pd(it, 'a&&href'),
            })
        });
        return setResult(d)
    },
   一级: async function () {
        let {input,pdfa,pdfh,pd} = this;
        let html = await request(input);
        let d = [];
        let data = pdfa(html, '.movie-list .movie-item');
        data.forEach((it) => {
            d.push({
                title: pdfh(it, '.movie-title&&Text'),
                pic_url: pd(it, '.movie-poster&&src'),
                desc: pdfh(it, '.movie-info&&Text'),
                url: pd(it, 'a&&href'),
            })
        });
        return setResult(d)
    },
	二级: async function () {
        let {input,pdfa,pdfh,pd} = this;
        let html = await request(input);
        let VOD = {};
        VOD.vod_name = pdfh(html, '.movie-detail .title&&Text');
        VOD.vod_content = pdfh(html, '.movie-desc&&Text');
        let playlist = pdfa(html, '.play-list a')
        let  play_urls = []
        let  play_from = []
        playlist.map((item) => {                    
             play_urls.push(pdfh(item,'a&&title') + '$' + pdfh(item,'a&&href'));
             play_from.push(pdfh(item,'a&&title'))                       
            });             
        VOD.vod_play_from = play_from.join('$$$');         
        VOD.vod_play_url = play_urls.join('#');
        return VOD
    },
	lazy:async function (){
        let {input} = this;
        if(/pan.quark.cn/.test(input)){
            return {parse: 0,jx: 0,url: 'push://' + input}       
        }else{
            return {parse: 1,jx: 0,url: input}
        }
    },
	搜索: async function () {
        let {input,pdfa,pdfh,pd} = this;
        let html = await request(input);
        let d = [];
        let data = pdfa(html, '.search-result .movie-item');
        data.forEach((it) => {
            d.push({
                title: pdfh(it, '.movie-title&&Text'),
                pic_url: pd(it, '.movie-poster&&src'),
                desc: pdfh(it, '.movie-info&&Text'),
                url: pd(it, 'a&&href'),
                content: pdfh(it, '.movie-desc&&Text'),
            })
        });
        return setResult(d)
    }
}
