# 필요한 패키지 불러오기
import scrapy
import json
from ..items import NewsItem
from scrapy.selector import Selector
from datetime import datetime
from StickersCrawl import stickers_crawl

# ----------------------------------------------------------------------------------------------------

# DaumNewsCrawler() 클래스 정의
class DaumNewsCrawler(scrapy.Spider):

    # 스파이더 이름 정의
    name = "DaumNewsCrawler"

    # 쿼리 스트링(Query String)을 제외한 기본 URL을 base_url에 할당
    base_url = "https://sports.daum.net/media-api/harmony/contents.json"

    # 뉴스 기사 분류 코드를 담은 딕셔너리 categories 초기화 
    categories = {
        1027: ("스포츠", "축구"),
        100032: ("스포츠", "해외축구"),
        1028: ("스포츠", "야구"),
        1015: ("스포츠", "해외야구"),
        5000: ("스포츠", "골프"),
        1029: ("스포츠", "농구"),
        100033: ("스포츠", "배구"),
        1031: ("스포츠", "일반"),
        1079: ("스포츠", "e-스포츠")
    }

    # ----------------------------------------------------------------------------------------------------

    # start_requests() 함수 정의
    def start_requests(self):
        """
        크롤링을 수행할 웹 페이지에 HTTPS 요청을 보내고 콜백 함수로서 news_parse() 함수를 호출하는 함수입니다.\n
        scrapy 모듈의 Request 클래스 객체를 반환합니다.
        """

        # 수집할 한 달 간의 날짜를 담은 search_period 변수 초기화
        search_period = "20221130000000~20221130235959"
        #search_period = "20221101000000~20221130235959"

        # for 반복문을 사용해 뉴스 분류별로 순회
        for category in self.categories.keys():

            # 쿼리 스트링(Query String)을 query_url에 할당
            query_url = r"?consumerType=HARMONY&createDt={0}&discoveryTag%5B0%5D=%257B%2522group%2522%253A%2522media%2522%252C%2522key%2522%253A%2522defaultCategoryId3%2522%252C%2522value%2522%253A%2522{1}%2522%257D&size=100".format(
                search_period,
                category
            )

            # 결과 값 반환
            yield scrapy.Request(url = self.base_url + query_url, callback = self.news_parse, cb_kwargs = dict(
                search_period = search_period,
                category = category
            ))

    # ----------------------------------------------------------------------------------------------------

    # news_parse() 함수 정의
    def news_parse(self, response, search_period : str, category : int):
        """
        JSON 페이지에서 분류, 작성일자, 제목, 내용, URL, 사진 URL, 기자, 뉴스사, 스티커 반응를 추출하고 다음 기사를 호출하는 함수입니다.\n
        scrapy 모듈의 Item 클래스 객체와 Request 클래스 객체를 반환합니다.
        """

        # 현재 크롤링을 진행하고 있는 웹 페이지 주소를 출력
        url = response.url
        print(f">>> 다음 URL을 크롤링 중입니다: {url}\n")

        # loads() 함수를 사용해 JSON 문자열을 객체로 변환해 변수 json_res에 할당
        json_res = json.loads(response.text)
        
        # NewsItem() 클래스를 가져와 변수 item에 할당
        item = NewsItem()

        # for 반복문을 사용해 페이지에 존재하는 100개의 뉴스 기사를 순회
        for news in range(100):

            # 뉴스 기사의 대분류와 소분류를 딕셔너리 categories에서 가져와 할당
            item["MainCategory"] = self.categories[category][0]
            item["SubCategory"] = self.categories[category][1]

            try:

                # 뉴스 기사의 제목, 내용, URL, 사진 URL, 기자, 뉴스사를 각 열에 저장
                item["Title"] = json_res["result"]["contents"][news]["title"]
                item["Content"] = json_res["result"]["contents"][news]["bodyText"]
                item["URL"] = json_res["result"]["contents"][news]["contentUrl"]
                item["Press"] = json_res["result"]["contents"][news]["cp"]["cpName"]

                # WritedAt (%Y-%m-%d %H:%M)
                body = json_res["result"]["contents"][news]["rawContent"]["dmcf"]
                date = Selector(text=body).xpath('//feedregdt/text()').get()
                item['WritedAt'] = datetime.strptime(date.split('.')[0], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M')

                # PhotoURL
                p = json_res['result']['contents'][news]['media']
                if len(p) == 0:
                    item['PhotoURL'] = None
                else:
                    item['PhotoURL'] = str([p[j]['url'] for j in range(len(p))])
                
                # itemKey for Stickers
                itemKey = json_res['result']['contents'][news]['metaData'][0]['values'][0]
                item['Stickers'] = stickers_crawl(itemKey)
                
                # 기자 이름이 없으면 언론사 이름으로 대체
                try:
                    item['Writer'] = json_res['result']['contents'][news]['writers'][0]['name']
                except:
                    item['Writer'] = json_res['result']['contents'][news]['cp']['cpName']

                # 결과 값 반환
                yield item
            
            # 100개 미만의 자료가 존재해 오류가 발생하는 경우 크롤링을 멈추고 안내 메시지를 출력
            except:
                print(f">>> 더 이상의 뉴스 기사가 존재하지 않아 다음 URL의 크롤링을 종료합니다: {url}\n")
                return

        # 쿼리 스트링(Query String)에 필요한 마지막 뉴스 ID를 last_news 변수에 할당
        last_news = json_res["result"]["contents"][-1]["searchId"]

        # 다음 페이지 정보를 담은 쿼리 스트링(Query String)을 query_url에 할당
        query_url = r"?&consumerType=HARMONY&createDt={0}&discoveryTag%5B0%5D=%257B%2522group%2522%253A%2522media%2522%252C%2522key%2522%253A%2522defaultCategoryId3%2522%252C%2522value%2522%253A%2522{1}%2522%257D&size=100&after={2}".format(
            search_period,
            category,
            last_news
        )

        # 결과 값 반환해 다음 페이지 호출
        yield scrapy.Request(url = self.base_url + query_url, callback = self.news_parse, cb_kwargs = dict(
            search_period = search_period,
            category = category
        ))