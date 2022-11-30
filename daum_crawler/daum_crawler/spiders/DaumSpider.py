# -*- coding: utf-8 -*-
import scrapy
from daum_crawler.items import DaumNewsCrawlerItem

import pandas as pd
import json

class DaumCrawlerSpider(scrapy.Spider):
    name = "daum_crawler"

    BASE_URL = 'https://sports.daum.net/media-api/harmony/contents.json'

    category = {
        1027: ('스포츠', '축구'),
        100032: ('스포츠', '해외축구'),
        1028: ('스포츠', '야구'),
        1015: ('스포츠', '해외야구'),
        5000: ('스포츠', '골프'),
        1029: ('스포츠', '농구'),
        100033: ('스포츠', '배구'),
        1031: ('스포츠', '일반'),
        1079: ('스포츠', '이스포츠')
    }

    def start_requests(self):
        createDt = '20221130000000~20221130235959'
        #createDt = '20221101000000~20221130235959'
        # 카테고리별로 뉴스기사 수집
        for cate in self.category.keys():
            query_url = r'?&consumerType=HARMONY&createDt={0}&discoveryTag%5B0%5D=%257B%2522group%2522%253A%2522media%2522%252C%2522key%2522%253A%2522defaultCategoryId3%2522%252C%2522value%2522%253A%2522{1}%2522%257D&size=100'.format(
                createDt,
                cate
            )
            yield scrapy.Request(url = self.BASE_URL + query_url, callback = self.parse, cb_kwargs = dict(
                createDt = createDt,
                cate = cate
            ))

    def parse(self, response, createDt : str, cate : int):

        jsonresponse = json.loads(response.text)
        item = DaumNewsCrawlerItem()
        # WritedAt = scrapy.Field()
        # Stickers = scrapy.Field()

        after = jsonresponse['result']['contents'][-1]['searchId']
    
        for i in range(100):
            item['MainCategory'] = self.category[cate][0]
            item['SubCategory'] = self.category[cate][1]

            try:
                item['Title'] = jsonresponse['result']['contents'][i]['title']
                item['Content'] = jsonresponse['result']['contents'][i]['bodyText']
                item['URL'] = jsonresponse['result']['contents'][i]['contentUrl']
                item['Press'] = jsonresponse['result']['contents'][i]['cp']['cpName']

                p = jsonresponse['result']['contents'][i]['media']
                if len(p) == 0:
                    item['PhotoURL'] = None
                else:
                    item['PhotoURL'] = str([p[j]['url'] for j in range(len(p))])
                    
                try:
                    item['Writer'] = jsonresponse['result']['contents'][i]['writers'][0]['name']
                except:
                    item['Writer'] = jsonresponse['result']['contents'][i]['cp']['cpName']
                yield item
            
            except:
                return

        query_url = r'?&consumerType=HARMONY&createDt={0}&discoveryTag%5B0%5D=%257B%2522group%2522%253A%2522media%2522%252C%2522key%2522%253A%2522defaultCategoryId3%2522%252C%2522value%2522%253A%2522{1}%2522%257D&size=100&after={2}'.format(
            createDt,
            cate,
            after
        )

        yield scrapy.Request(url = self.BASE_URL + query_url, callback = self.parse, cb_kwargs = dict(
            createDt = createDt,
            cate = cate
        ))