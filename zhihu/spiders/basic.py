# -*- coding: utf-8 -*-
import scrapy
import random

from zhihu.items import ZhihuItem
from scrapy import Request
from scrapy.selector import Selector
from login import isLogin
from login import login
import time
from scrapy.http import HtmlResponse
import urlparse
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import json
import re


class BasicSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["zhihu.com"]
    
    # Start on a property page
    start_urls = open('topics.txt').readlines()
    user_agent_list = [
        'User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko',
        'User-Agent:Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
        'User-Agent:Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
        'User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
        'User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
        'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
        'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
    ]
    def set_headers(self, url):
        # agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"
        agent = self.user_agent_list[random.randint(0,7)]
        # print (agent)
        headers = {
            "Host": "www.zhihu.com",
            'User-Agent': agent
        }
        headers['Referer'] = url
        return headers

    def start_requests(self):
        if isLogin():
            print('您已经登录')
        else:
            # account = input('请输入你的用户名\n>  ')
            # secret = input("请输入你的密码\n>  ")
            account = '15728689495'
            secret = 'q12345'
            login(secret, account)

        for url in self.start_urls:
            print '正在访问'+ url
            time.sleep(5)
            yield Request(
                url= url.strip('\n'),
                headers=self.set_headers('https://www.zhihu.com/topic'),
                cookies=cookielib.LWPCookieJar(filename='cookies'),
                callback=self.parse,
                meta={'page':1}
            )
    def parse(self, response):
        print '开始处理网页' + response.url 
        # Get the next index URLs and yield Requests

        #attention
        if response.meta['page'] < 10: 
            next_page = response.meta['page'] + 1
            pre_fix = '?page=' + str(next_page) 
            print '间隔3秒访问下一页'
            time.sleep(3)
            print '开始请求下一页'
            urlparse.urljoin(response.url, pre_fix)
            yield Request(url=urlparse.urljoin(response.url, pre_fix),
                headers=self.set_headers(response.url),
                cookies=cookielib.LWPCookieJar(filename='cookies'),
                callback=self.parse,
                meta = {'page':next_page}
                )
        print '生成问题列表'
        # Get item URLs and yield Requests
        item_selector = response.xpath('//*[@class="question_link"]/@href')
        # item_selector = response.xpath('//*[@class="feed-item"]/link/@href')
        for url in item_selector.extract():
            print '间隔2秒访问问题'
            time.sleep(2)
            print '开始访问问题'
            print urlparse.urljoin(response.url, url)
            yield Request(urlparse.urljoin(response.url, url),
                headers=self.set_headers(urlparse.urljoin(response.url, url)),
                cookies=cookielib.LWPCookieJar(filename='cookies'),
                callback=self.parse_item)

    def parse_item(self, response):
        item = ZhihuItem()
        item['topics'] = response.xpath('//*[@class="Tag-content"]/a/div/div/text()').extract()
        item['title'] = response.xpath('//*[@class="QuestionHeader-title"]/text()').extract()
        item['desc'] = response.xpath('//*[@class="RichText"]/text()').extract()
        time.sleep(2)
        return item

