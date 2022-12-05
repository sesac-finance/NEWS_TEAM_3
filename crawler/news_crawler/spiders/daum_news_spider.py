# 필요한 패키지 불러오기
import scrapy
import requests
from scrapy.selector import Selector
import json
from ..items import NewsItem
from datetime import datetime
from typing import Union

# ----------------------------------------------------------------------------------------------------

# DaumNewsCrawler() 클래스 정의
class DaumNewsCrawler(scrapy.Spider):

    # 스파이더 이름 정의
    name = "DaumNewsCrawler"

    # 쿼리 스트링(Query String)을 제외한 기본 URL을 base_url에 할당
    base_url = "https://sports.daum.net/media-api/harmony/contents.json"

    # 뉴스 기사 분류 코드를 담은 딕셔너리 categories 초기화
    categories = {
        1027: ("스포츠", "축구"), 100032: ("스포츠", "해외축구"), 1028: ("스포츠", "야구"), 1015: ("스포츠", "해외야구"), 5000: ("스포츠", "골프"),
        1029: ("스포츠", "농구"), 100033: ("스포츠", "배구"), 1031: ("스포츠", "일반"), 1079: ("스포츠", "e-스포츠")
    }

    # URL에 접속하기 위해 필요한 헤더(Header) 정보를 담은 딕셔너리 headers 초기화
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

    # ----------------------------------------------------------------------------------------------------

    # __init__() 함수 정의
    def __init__(self):
        """
        스파이더(Spider) 클래스를 생성할 때 실행되는 생성자 함수입니다.\n
        스티커 반응 URL에 접속하기 위해 필요한 'Authorization' 값을 가져옵니다.
        """

        # 인증 값을 가져오기 위한 임의의 뉴스 기사 url을 client_id_url에 할당 
        client_id_url = "https://v.daum.net/v/B8FE1zLZ2m"

        # 딕셔너리 headers에 "referer" 값 추가
        self.headers["referer"] = client_id_url

        # get() 함수를 사용해 스티커 반응 정보를 요청해 변수 res에 할당
        client_res = requests.get(url = client_id_url)

        # 클라이언트 ID를 추출해 변수 client_id에 할당
        client_id = Selector(text = client_res.text).css(".alex-actions").attrib["data-client-id"]

        # 추출한 클라이언트 ID를 넣어 token_url에 할당
        token_url = "https://alex.daum.net/oauth/token?grant_type=alex_credentials&client_id={}".format(client_id)

        # get() 함수를 사용해 토큰 정보를 요청해 변수 token_res에 할당
        token_res = requests.get(url = token_url, headers = self.headers)

        # loads() 함수를 사용해 JSON 문자열을 객체로 변환해 각 스티커 반응을 딕셔너리 stickers_dict에 할당
        access_token = json.loads(token_res.text)["access_token"]

        # 딕셔너리 headers에 "authorization" 값 추가 및 "referer" 값 삭제
        self.headers["authorization"] = "Bearer " + access_token
        del self.headers["referer"]

    # ----------------------------------------------------------------------------------------------------

    # start_requests() 함수 정의
    def start_requests(self):
        """
        크롤링을 수행할 웹 페이지에 HTTPS 요청을 보내고 콜백 함수로서 news_parser() 함수를 호출하는 함수입니다.\n
        scrapy 모듈의 Request 클래스 객체를 반환합니다.
        """

        # 수집할 한 달 간의 날짜를 담은 search_period 변수 초기화
        search_period = "20221101000000~20221130235959"

        # for 반복문을 사용해 뉴스 분류별로 순회
        for category in self.categories.keys():

            # 쿼리 스트링(Query String)을 query_url에 할당
            query_url = r"?consumerType=HARMONY&createDt={0}&discoveryTag%5B0%5D=%257B%2522group%2522%253A%2522media%2522%252C%2522key%2522%253A%2522defaultCategoryId3%2522%252C%2522value%2522%253A%2522{1}%2522%257D&size=100".format(
                search_period,
                category
            )

            # 결과 값 반환
            yield scrapy.Request(url = self.base_url + query_url, callback = self.news_parser, cb_kwargs = dict(
                search_period = search_period,
                category = category
            ))

    # ----------------------------------------------------------------------------------------------------

    # news_parser() 함수 정의
    def news_parser(self, response, search_period : str, category : int):
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
                # 뉴스 기사의 제목, 내용, URL, 뉴스사를 각 열에 저장
                item["Title"] = json_res["result"]["contents"][news]["title"]
                item["Content"] = json_res["result"]["contents"][news]["bodyText"]
                item["URL"] = json_res["result"]["contents"][news]["contentUrl"]
                item["Press"] = json_res["result"]["contents"][news]["cp"]["cpName"]

                # 뉴스 기사의 작성일자를 writed_at_transformer() 함수를 호출하여 저장
                item["WritedAt"] = self.writed_at_transformer(json_res["result"]["contents"][news]["rawContent"]["dmcf"])

                # 뉴스 기사의 사진 URL을 photo_url_extractor() 함수를 호출하여 저장
                item["PhotoURL"] = self.photo_url_extractor(json_res["result"]["contents"][news]["media"])

                # 뉴스 기사의 스티커 반응을 stickers_crawler() 함수를 호출하여 저장
                item["Stickers"] = self.stickers_crawler(json_res["result"]["contents"][news]["contentUrl"])
                
                #  뉴스 기사의 기자 이름을 저장하고, 없는 경우 뉴스사 이름으로 대체
                try:
                    item["Writer"] = json_res["result"]["contents"][news]["writers"][0]["name"]
                except:
                    item["Writer"] = json_res["result"]["contents"][news]["cp"]["cpName"]

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
        yield scrapy.Request(url = self.base_url + query_url, callback = self.news_parser, cb_kwargs = dict(
            search_period = search_period,
            category = category
        ))

    # ----------------------------------------------------------------------------------------------------

    # writed_at_transformer() 함수 정의
    def writed_at_transformer(self, xml_text : str) -> str:
        """
        뉴스의 작성일자가 포함된 XML 문자열을 입력받아 작성일자를 추출해 변환하는 함수입니다.\n
        '연-월-일 시:분'으로 구성된 문자열(String) 객체를 반환합니다.
        """

        # 뉴스의 작성일자가 포함된 xml_text에서 뉴스의 작성일자만 추출해 변수 xml_date에 할당
        xml_date = Selector(text = xml_text).xpath("//feedregdt/text()").get()

        # ① strptime() 메서드를 사용해 datetime 객체로 변환
        # ② strftime() 메서드를 사용해 데이터베이스에 들어가야 할 양식의 문자열 객체로 변환해 변수 writed_at_date에 할당
        writed_at_date = datetime.strptime(xml_date.split(".")[0], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M")

        # 결과 값 반환
        return writed_at_date

    # ----------------------------------------------------------------------------------------------------

    # photo_url_extractor() 함수 정의
    def photo_url_extractor(self, photo_list : list) -> Union[list, None]:
        """
        뉴스의 사진 URL이 포함된 리스트를 입력받아 사진 URL을 추출하는 함수입니다.\n
        사진 URL들로 구성된 리스트(List)를 반환하고, 만약 사진이 없다면 None 객체를 반환합니다.
        """

        # 뉴스의 사진이 존재하지 않는 경우 None 값 반환
        if len(photo_list) == 0: return None

        # 뉴스의 사진이 존재하는 경우 리스트 컴프리헨션(List Comprehension)을 사용해 사진 목록을 추출
        else:
            photo_urls = [photo_list[photo]["url"] for photo in range(len(photo_list))]

            # 결과 값 반환
            return photo_urls

    # ----------------------------------------------------------------------------------------------------

    # stickers_crawler() 함수 정의
    def stickers_crawler(self, news_url : str) -> dict:
        """
        뉴스의 스티커 반응을 크롤링하여 추출하는 함수입니다.\n
        뉴스의 스티커 반응이 담긴 딕셔너리(Dictionary)를 반환합니다.
        """

        # get() 함수를 사용해 뉴스 기사 URL를 요청해 변수 itemkey_res에 할당
        itemkey_res = requests.get(url = news_url)

        # 기사별로 부여된 고유한 ID를 추출해 변수 itemkey에 할당
        itemkey = Selector(text = itemkey_res.text).css(".alex-actions").attrib["data-item-key"]

        # 스티커 반응이 존재하는 링크를 stickers_url에 할당
        stickers_url = "https://action.daum.net/apis/v1/reactions/home?itemKey={}".format(itemkey)

        # get() 함수를 사용해 스티커 반응 정보를 요청해 변수 stickers_res에 할당
        stickers_res = requests.get(url = stickers_url, headers = self.headers)

        # loads() 함수를 사용해 JSON 문자열을 객체로 변환해 각 스티커 반응을 딕셔너리 stickers_dict에 할당
        stickers_dict = {
            "추천해요": json.loads(stickers_res.text)["item"]["stats"]["RECOMMEND"],
            "좋아요": json.loads(stickers_res.text)["item"]["stats"]["LIKE"],
            "감동이에요": json.loads(stickers_res.text)["item"]["stats"]["IMPRESS"],
            "화나요": json.loads(stickers_res.text)["item"]["stats"]["ANGRY"],
            "슬퍼요": json.loads(stickers_res.text)["item"]["stats"]["SAD"]
        }

        # 결과 값 반환
        return stickers_dict