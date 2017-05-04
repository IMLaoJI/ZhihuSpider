# -*- coding: utf-8 -*-
import scrapy
import random

from zhihu.items import ZhihuItem
from zhihu.topicitems import TopicItem
from scrapy import Request
from scrapy.selector import Selector
from login import isLogin
from login import login
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import json
import re

class LinksSpider(scrapy.Spider):

    name = "links"
    allowed_domains = ["zhihu.com"]

    # Start on a property page
    # start_urls = [i.strip() for i in open('/home/andrew/Desktop/topics.txt')] 
    start_urls = [
        'https://www.zhihu.com/topics#科技',
        'https://www.zhihu.com/topics#电影'
    ]
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
            yield Request(
                url = url,
                # url='https://www.zhihu.com/topics#'+url,
                headers=self.set_headers('https://www.zhihu.com'),
                cookies=cookielib.LWPCookieJar(filename='cookies'),
                dont_filter=True,
            )

    def parse(self, response):
        item = TopicItem()
        item['link'] = response.xpath('//*[@class="blk"]/a[1]/@href').extract()
        return item 
 