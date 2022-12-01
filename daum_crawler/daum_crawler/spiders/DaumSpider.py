# -*- coding: utf-8 -*-
import scrapy
import json

from datetime import datetime
from scrapy.selector import Selector

from scrapy.http.response.text import TextResponse

from daum_crawler.items import DaumNewsCrawlerItem

from StickersCrawl import stickers_crawl

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
        1079: ('스포츠', 'e-스포츠')
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

        # json parsing
        jsonresponse = json.loads(response.text)
        item = DaumNewsCrawlerItem()

        # after for query
        after = jsonresponse['result']['contents'][-1]['searchId']
    
        for i in range(100):
            item['MainCategory'] = self.category[cate][0]
            item['SubCategory'] = self.category[cate][1]
            try:
                item['Title'] = jsonresponse['result']['contents'][i]['title']
                item['Content'] = jsonresponse['result']['contents'][i]['bodyText']
                item['URL'] = jsonresponse['result']['contents'][i]['contentUrl']
                item['Press'] = jsonresponse['result']['contents'][i]['cp']['cpName']

                # WritedAt (%Y-%m-%d %H:%M)
                body = jsonresponse['result']['contents'][i]['rawContent']['dmcf']
                date = Selector(text=body).xpath('//feedregdt/text()').get()
                item['WritedAt'] = datetime.strptime(date.split('.')[0], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M')

                # PhotoURL
                p = jsonresponse['result']['contents'][i]['media']
                if len(p) == 0:
                    item['PhotoURL'] = None
                else:
                    item['PhotoURL'] = str([p[j]['url'] for j in range(len(p))])
                
                # itemKey for Stickers
                itemKey = jsonresponse['result']['contents'][i]['metaData'][0]['values'][0]
                item['Stickers'] = stickers_crawl(itemKey)
                
                # 기자 이름이 없으면 언론사 이름으로 대체
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
    

    # def stickers_crawl(self, itemKey : str):
    #     '''
    #     스티커 크롤링 함수
    #     '''
    #     headers = {"authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjoxODQwNjExNSwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS9jSFVGa2FKX2FaMTAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi7J207Iqs6riwIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2Njk5MDQ1MDMsImF1dGhvcml0aWVzIjpbIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiJmNTkwYjAxZi1jZjBmLTQ2YzktYjUyYy03N2E5ZTVkYTk1Y2EiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.GJWFgTKX43CZeblHrm6PUx2sZNgGPA5zqaIetU8jePI"}
    #     reactionURL = 'https://action.daum.net/apis/v1/reactions/home?itemKey={}'.format(itemKey)
    #     response = TextResponse(url = reactionURL, headers = headers)

    #     reactionjson = json.loads(response.text)['item']['stats']

    #     reaction_dict = {
    #             '추천해요': reactionjson['RECOMMEND'],
    #             '좋아요': reactionjson['LIKE'],
    #             '감동이에요': reactionjson['IMPRESS'],
    #             '화나요': reactionjson['ANGRY'],
    #             '슬퍼요': reactionjson['SAD']
    #     }
    #     return reaction_dict


    