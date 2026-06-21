package com.github.catvod.spider;

import android.content.Context;

import com.github.catvod.bean.Class;
import com.github.catvod.bean.Result;
import com.github.catvod.bean.Vod;
import com.github.catvod.crawler.Spider;
import com.github.catvod.net.OkHttp;
import com.github.catvod.utils.Util;

import org.json.JSONObject;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.net.URLDecoder;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * @author 花语
 */
//子子发布页https://ziziys.info/
public class Zzys extends Spider {

    private static String siteUrl = "https://www.ziziys.net";

    private Map<String, String> getHeader() {
        Map<String, String> header = new HashMap<>();
        header.put("User-Agent", Util.CHROME);
        return header;
    }

    @Override
    public void init(Context context, String extend) throws Exception {
        if (!extend.isEmpty()) 
        siteUrl = extend;
    }

    @Override
    public String homeContent(boolean filter) throws Exception {
        List<Class> classes = new ArrayList<>();
        List<String> typeIds = Arrays.asList("1", "2", "3");
        List<String> typeNames = Arrays.asList("电影", "剧集", "动漫");
        for (int i = 0; i < typeIds.size(); i++) classes.add(new Class(typeIds.get(i), typeNames.get(i)));
        String f = "{\"1\": [{\"key\": \"cateId\", \"name\": \"类型\", \"value\": [{\"n\": \"动作片\", \"v\": \"6\"}, {\"n\": \"剧情片\", \"v\": \"7\"}, {\"n\": \"喜剧片\", \"v\": \"8\"}, {\"n\": \"爱情片\", \"v\": \"9\"}, {\"n\": \"惊悚片\", \"v\": \"10\"}, {\"n\": \"奇幻片\", \"v\": \"11\"}, {\"n\": \"悬疑片\", \"v\": \"12\"}, {\"n\": \"动画片\", \"v\": \"23\"}, {\"n\": \"恐怖片\", \"v\": \"24\"}, {\"n\": \"传奇片\", \"v\": \"25\"}, {\"n\": \"战争片\", \"v\": \"26\"}, {\"n\": \"古装片\", \"v\": \"28\"}, {\"n\": \"纪录片\", \"v\": \"29\"}]}], \"2\": [{\"key\": \"cateId\", \"name\": \"类型\", \"value\": [{\"n\": \"国产剧\", \"v\": \"13\"}, {\"n\": \"美剧\", \"v\": \"14\"}, {\"n\": \"日韩剧\", \"v\": \"15\"}, {\"n\": \"泰国剧\", \"v\": \"16\"}]}], \"3\": [{\"key\": \"cateId\", \"name\": \"类型\", \"value\": [{\"n\": \"国漫\", \"v\": \"20\"}, {\"n\": \"日漫\", \"v\": \"21\"}, {\"n\": \"欧美\", \"v\": \"22\"}]}]}";
        JSONObject filterConfig = new JSONObject(f);
        Document doc = Jsoup.parse(OkHttp.string(siteUrl, getHeader()));
        Elements elements = doc.select(".module-item");
        int numElements = Math.min(elements.size(), 12);
        elements = new Elements(elements.subList(0, numElements));
        List<Vod> list = parseVodList(elements);
        return Result.string(classes, list, filterConfig);
    }

    public List<Vod> parseVodList(Elements items) {
        ArrayList<Vod> list = new ArrayList<>();
        for (Element li : items) {
            String vid = li.select(".module-item-titlebox >a").attr("href");
            String name = li.select(".module-item-titlebox >a").attr("title");
            String pic = li.select(".module-item-pic img").attr("data-src");
            String remark = li.select(".module-item-text").text();
            list.add(new Vod(vid, name, pic, remark));
        }
        return list;
    }

    @Override
    public String categoryContent(String tid, String pg, boolean filter, HashMap<String, String> extend) throws Exception {
        String cateId = extend.get("cateId") == null ? tid : extend.get("cateId");
        String cateUrl = siteUrl + String.format("/vodshow/%s--------%s---.html", cateId, pg);
        Document doc = Jsoup.parse(OkHttp.string(cateUrl, getHeader()));
        List<Vod> list = parseVodList(doc.select(".module-item"));
        return Result.string(list);
    }

    @Override
    public String detailContent(List<String> ids) throws Exception {
        Document doc = Jsoup.parse(OkHttp.string(siteUrl + ids.get(0), getHeader()));
        Elements sources = doc.select(".scroll-box-y");
        Elements circuits = doc.select(".module-tab-item");
        StringBuilder vod_play_url = new StringBuilder(); 
        StringBuilder vod_play_from = new StringBuilder();
        for (int i = 0; i < sources.size(); i++) {
            String spanText = circuits.get(i).select("span").text();
            String smallText = circuits.get(i).select("small").text();
            String playFromText = spanText + "(共" + smallText + "集)";
            vod_play_from.append(playFromText).append("$$$");
            Elements aElementArray = sources.get(i).select("a");
            for (int j = 0; j < aElementArray.size(); j++) {
                Element a = aElementArray.get(j);
                String href = a.attr("href");
                String text = a.text();
                vod_play_url.append(text).append("$").append(href);
                boolean notLastEpisode = j < aElementArray.size() - 1;
                vod_play_url.append(notLastEpisode ? "#" : "$$$");
            }
        }

        String title = doc.selectFirst(".video-info-header > .page-title").text();//片名
        String pic = doc.selectFirst(".module-item-pic img").attr("data-src");//图片
        String area = doc.select(".video-info-aux > a:nth-child(4)").text();//地区
        String type = doc.select(".video-info-aux > div > a").text();//类型
        String brief = doc.select(".video-info-content").text();//简介
        String director = doc.select(".video-info-main > div:nth-child(1) > .video-info-item > a").text();//导演
        String actor = doc.select(".video-info-main > div:nth-child(2) > .video-info-item > a").text();//主演
        String year = doc.select(".video-info-aux > a:nth-child(3)").text();//年份
        String remark = doc.select(".video-info-main > div:nth-child(4) > .video-info-item").text();//备注

        Vod vod = new Vod();
        vod.setVodId(ids.get(0));
        vod.setVodPic(pic);
        vod.setVodYear(year);
        vod.setVodName(title);
        vod.setVodArea(area);
        vod.setVodActor(actor);
        vod.setVodRemarks(remark);
        vod.setVodContent(brief);
        vod.setVodDirector(director);
        vod.setTypeName(type);
        vod.setVodPlayFrom(vod_play_from.toString());
        vod.setVodPlayUrl(vod_play_url.toString());
        return Result.string(vod);
    }

    public String playerContent(String flag, String id, List<String> vipFlags) throws Exception {
        Document doc = Jsoup.parse(OkHttp.string(siteUrl.concat(id), getHeader()));
        String src = doc.select("iframe").attr("src");
        String url = siteUrl + src;
        String content = OkHttp.string(url, getHeader());
        Matcher matcher = Pattern.compile("player_aaaa=(.*?)</script>").matcher(content);
        String json = matcher.find() ? matcher.group(1) : "";
        JSONObject player = new JSONObject(json);
        String realUrl = URLDecoder.decode(player.getString("url"));
        return Result.get().url(realUrl).header(getHeader()).string();
    }

    @Override
    public String searchContent(String key, boolean quick) throws Exception {
        String searchUrl = siteUrl + "/vsearch/--.html?wd=" + URLEncoder.encode(key);
        String html = OkHttp.string(searchUrl, getHeader());
        Elements items = Jsoup.parse(html).select(".module-search-item");
        List<Vod> list = new ArrayList<>();
        for (Element item : items) {
            String vodId = item.select(".video-info-header a").attr("href");
            String name = item.select(".video-info-header a").attr("title");
            String pic = item.select(".module-item-pic img").attr("data-src");
            String remark = "";
            Elements searchElements = item.select(".video-info-header a.video-serial");
            if (!searchElements.isEmpty()) {
                remark = searchElements.first().text();
            }
            list.add(new Vod(vodId, name, pic, remark));
        }
        return Result.string(list);
    }
}
