# Copyright © 2023 BAAI. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License")
import re
from collections import OrderedDict


###############################################################################
# 主要做了以下这些处理
# url 
# 全角字符
# 站点关键词
# 非正文关键词
# 重复文本
# 掐头去尾
# 异型字，同音字处理
# 结束词处理
# 群号处理
# 页面代码 <**> <a href= <script <INPUT <embed <bold
###############################################################################


class BooksRuleSet:
    def __init__(self):
        self.REGEX_MAP = self.group_regex()
        self.REGEX_PIPELINE = self.build_pipeline(self.REGEX_MAP)

    def build_pipeline(self, regex_map):
        REGEX_PIPELINE = []
        for cat, regex_group in regex_map.items():
            for regex_exp in regex_group:
                compiled_regex = re.compile(regex_exp, flags=re.I)
                REGEX_PIPELINE.append(compiled_regex)
        return REGEX_PIPELINE

    def group_regex(self):
        regex_map = OrderedDict()
        # 基于括号清除比较粗粒度，可大大提高召回率，但误杀也比较多
        regex_map["hot_keywords"] = [
                    '\(', '\)', '\[', '\]', '（', '）', '【', '】', '<', '>', '第.*?章', 
                    'txt', 'equb', 'mobi', '文学网', '中文网', '小说.*?下载', '小说.*?群', '小说资源', '小说网', '弹窗广告', '[无|免]广告', '最新章节',
                    '免费.*?小说', '更多.*?小说', '下载.*?小说', '正版.*?小说', '全文阅读', '免费阅读', '在线阅读', '没有广告', '提供.*?下载',
                    ]
        regex_map["url_hits"] = [
                    'w ?w ?w', 'w ?w', 'c ?o ?m', 'h ?t ?t ?p ?s?', '[.|。] ?c ?n', 'f ?t ?p', 's ?r ?c', 'h ?r ?e ?f', '//', '\/\/', '[.|。]ar', '[.|。] ?c ?c',
                    '[.|。]org', '[.|。]uk', '[.|。]ac', '[.|。]edu', '[.|。] ?n ?e ?t', '[.|。]php', r'[Ａ-Ｚ]', 'xml', 'json', 'html?', 'w ?a ?p', 
                    ]
        regex_map["unuse_content"] = [
                    'PS[1|2|3|4]?[：|:]', '月票', '推荐票', '正版订阅', '收藏数', '手机阅读', '最新章节', '推荐票', '打榜', '未完待续', '万字更新', '字数[:|：].*?字',
                    '小说.*?群', '加.*?群', '广告少', '无弹窗', '更新快', '签约作品', '精校', '上一章', '章节目录', '下一章', '加入书签', '新书推荐', '潇湘VIP',
                    '红袖VIP', '起点VIP', '晋江VIP', '更多小说', '双更', '爆更', '加更', '本章节', '增加一更', '用户上传之内容', 'VIP章节', '无用章节请删除',
                    '章节有误', '章节更多', '更多章节', '支持正版', '正版支持', '尽在.*?网', '盡在.*?網', '小說', '閱讀', '整理提供', '好书尽在', '小说尽在',
                    '由.*?免费提供', '单更', '一更', '两更', '双更', '三更', '四更', '五更', '六更', '七更', '八更', '九更', '追更', '断更', '【麻烦', '章更新',
                    '收藏.*?投票', '投票.*?收藏', 'VIP全本', '更新预告', '更新时间', 
                    '欲知详情', '新书', '书友', '打赏冲榜', '求收藏', '求打赏', '求鲜花', '求点赞', '求订阅', '求自动', '点击数', '严打', '更新.章', '屁爱死',
                    '电子书', '关于本书', '精校小说', '本章字数', 
                    ]
        regex_map["sign"] = [
                    '━━━━━', r'=====', '\+\+\+\+\+', r'----', r'————', r'____', r'~~~~', '\*\*\*\*\*', '`````', r'<<<', r'>>>', r'▲▲▲▲', r'[┃↙↘→&]'
                    ]
        regex_map["webset_domin"] = [
                    '80txt', 'zaihen', 'qiushu', 'mianhuatang', 'cmfu', 'uutxt', '27txt', 'paipaitxt', 'xiaoshuotxt', 'downshu', 'heihei', 'aiyousheng', '23us', 'wrshu',
                    'kanmaoxian', 'bqg5', 'myfreshnet', 'horou', '517z', 'dospy', 'junzitang', 'xiaoshuo510', '3zcn', '101du', '16k', 'wanjuan',
                    'feiku', 'qisuu', 'wenxin8', '2009w', 'yunxiaoge', '13800100', 'dajiadu', 'genduba', 'lnwow',  'aoye',  'neiyu',  'yunxuange', 
                     'jjwxc',  'zineworm',  'pashu8',  '555x',  'aishuzhe', '517z',
                    ]
        regex_map["webset_keywords"] = [
                    '星舞藏书', '知轩藏书', '飞卢小说', '棉花糖小说', '顶点小说', '田田小说', '520免费小说', '派派小说', '东方小说', '爱去小说', '无限小说', 
                    '笔趣阁', '词笔阁', '文心阁', '云霄阁', '有意思[書|书]院', '幽幽书盟', '悠悠书盟', '河洛中文社区', '起点中文社区', '八路中文社区', '3[z|Z]中文社区',
                    '大家读书院', '一手原创书城', '16K小说', '万卷书屋', '八零电子书', '沸腾文学', '梨花文学', '晋江文学', 
                    '千仙殿', '[求|有|奇|炫|爬]书网', '泡书吧', '君子堂', '杂志虫', '有意思书院', '安智网',
                    ]
        regex_map["claim_keywords"] = [
                    '支持正版', '版权归原?作者', '自互联网', '本站.*?资源', '仅供.*?试读', '24小时内删除', '拒绝盗版', '联系.*?删除', '提供预览', '不得.*?商业用途', '二十四小时内删除', 
                    '仅代表作者.*?观点', '删除处理', '阅读平台', '版权问题', '声明[：|:]'
                    ]
        regex_map["qq"] = [r'qq：|qq:|QQ：|QQ:|qQ：|qQ:|Qq：|Qq:|pp：|pp:|企鹅号|企鹅号',
                           r'群：|群:|群聊：|群聊:|企鹅群|Q群|q群|扣群|群号|进群|君羊']
        regex_map["qq_number"] = [r'[1-9](\d\D?){7,9}',]
        regex_map["email"] = [r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)',
                              r'(@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)']
        regex_map["code"] = [
                    r'<CENTER', r'<INPUT', r'<script', r'<PIXTEL', r'<strong', r'<bold',  # 前面匹配了<>符号，可忽略
                    ]
        regex_map["maybe_unuse_content"] = [
                    '追更', '打赏', '订阅', '点击数', '收藏', '推荐', '字数', '关注', '投票', '章节', '作者', '简介', '书签', '书友', '新书', '新作', '关注', '月票', '打榜', '一更', '加更', '单更', '两更', '双更', '三更', '四更', '五更', '六更', '手打', '精校',
                    '读者，连载，章节，修订本，番外，下本书，全本，主编，责编，责任编辑，定稿，本书，情节，断更，正文，电子书，关于本书，精校小说,支持,投票地址， 上一章 ← 章节目录 → 下一章，作者信息，内容简介，加入书签，新书推荐，关注一下']
        return regex_map
    

