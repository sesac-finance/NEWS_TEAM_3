# 필요한 패키지 불러오기
import scrapy
import pandas as pd
from ..items import NewsURLItem, NewsItem, CommentItem
from datetime import datetime
import requests
import json
import re

# ----------------------------------------------------------------------------------------------------

# NaverNewsURLCrawler() 클래스 정의
class NaverNewsURLCrawler(scrapy.Spider):

    # 스파이더 이름 정의
    name = "NaverNewsURLCrawler"

    # 접근 차단을 막기 위한 시간 지연 설정
    download_delay = 0.15

    # 쿼리 스트링(Query String)을 제외한 기본 URL을 base_url에 할당
    base_url = "https://news.naver.com/main/list.naver"

    # 뉴스 기사 분류 코드를 담은 딕셔너리 categories 초기화
    categories = {
        731: ("IT/과학", "모바일"), 226: ("IT/과학", "인터넷/SNS"), 227: ("IT/과학", "통신/뉴미디어"), 230: ("IT/과학", "IT 일반"),
        732: ("IT/과학", "보안/해킹"), 283: ("IT/과학", "컴퓨터"), 229: ("IT/과학", "게임/리뷰"), 228: ("IT/과학", "과학 일반"),
        231: ("세계", "아시아/호주"), 232: ("세계", "미국/중남미"), 233: ("세계", "유럽"), 234: ("세계", "중동/아프리카"),
        322: ("세계", "세계 일반")
    }

    # ----------------------------------------------------------------------------------------------------

    # start_requests() 함수 정의
    def start_requests(self):
        """
        크롤링을 수행할 웹 페이지에 HTTPS 요청을 보내고 콜백 함수로서 news_locator() 함수를 호출하는 함수입니다.\n
        scrapy 모듈의 Request 클래스 객체를 반환합니다.
        """
        
        # date_range() 함수를 사용하여 수집할 한 달 간의 날짜를 담은 search_period 변수 초기화
        search_period =  pd.date_range("2022-11-01", "2022-11-30", freq = "D").strftime("%Y%m%d")

        # for 반복문을 사용해 뉴스 분류별로 순회
        for sub_category in self.categories.keys():

            # for 반복문을 사용해 각 날짜를 순회
            for date in search_period:

                # 처음 크롤링을 수행할 페이지를 담은 변수 page 초기화
                page = 1

                # 뉴스 대분류 정보를 담은 쿼리를 변수 main_category 할당 
                main_category = 105 if self.categories[sub_category][0] == "IT/과학" else 104

            # 쿼리 스트링(Query String)을 query_url에 할당
                query_url = "?mode=LS2D&sid2={0}&sid1={1}&mid=shm&date={2}&page={3}".format(sub_category, main_category, date, page)

            # 결과 값 반환
                yield scrapy.Request(url = self.base_url + query_url, callback = self.news_locator, cb_kwargs = dict(
                    sub_category = sub_category,
                    main_category = main_category,
                    date = date,
                    page = page
                ))

    # ----------------------------------------------------------------------------------------------------

    # news_locator() 함수 정의
    def news_locator(self, response, sub_category : int, main_category : int, date : str , page : int):
        """
        네이버 뉴스 웹 페이지에서 분류, 제목, URL을 추출하는 함수입니다.\n
        scrapy 모듈의 Item 클래스 객체와 Request 클래스 객체를 반환합니다.
        """

        # 현재 크롤링을 진행하고 있는 웹 페이지 주소를 출력
        url = response.url
        print(f">>> 다음 URL을 크롤링 중입니다: {url}\n")

        # NewsURLItem() 클래스를 가져와 변수 item에 할당
        item = NewsURLItem()
        
        # 크롤링 돌고 있는 현재 표시된 페이지
        current_page = int(response.xpath(f"//*[@id='main_content']/div[3]/strong/text()").get())

        # 링크에서 접근한 페이지와 현재 페이지로 표시된 페이지가 다른 경우 크롤링을 멈추고 안내 메시지를 출력
        if current_page != page:
            print(f">>> 더 이상의 뉴스 기사가 존재하지 않아 다음 URL의 크롤링을 종료합니다: {url}\n")
            return

        else:
            # for 반복문을 통해 한 페이지의 뉴스 10개로 구성된 2개 섹션을 순회
            for section_num in range(1, 3, 1):

                # for 반복문을 통해 각 섹션의 뉴스 기사를 순회
                for list_num in range(1, 11, 1):

                # 뉴스 기사의 대분류와 소분류를 딕셔너리 categories에서 가져와 할당
                    item["MainCategory"] = self.categories[sub_category][0]
                    item["SubCategory"]= self.categories[sub_category][1]

                    # 뉴스 기사에 사진이 없는 경우 제목과 URL을 추출해 각 열에 저장
                    if not response.xpath(f"//*[@id='main_content']/div[2]/ul[{section_num}]/li[{list_num}]/dl/dt[2]/a/text()").get():
                        item["Title"] = response.xpath(f"//*[@id='main_content']/div[2]/ul[{section_num}]/li[{list_num}]/dl/dt/a/text()").get().strip()
                        item["URL"] = response.xpath(f"//*[@id='main_content']/div[2]/ul[{section_num}]/li[{list_num}]/dl/dt/a/@href").get()
                        yield item

                    # 뉴스 기사에 사진이 있는 경우 제목과 URL을 추출해 각 열에 저장
                    else:
                        item["Title"] = response.xpath(f"//*[@id='main_content']/div[2]/ul[{section_num}]/li[{list_num}]/dl/dt[2]/a/text()").get().strip()
                        item["URL"] = response.xpath(f"//*[@id='main_content']/div[2]/ul[{section_num}]/li[{list_num}]/dl/dt[2]/a/@href").get()
                        yield item
            
            # 다음 페이지를 호출하기 위해 변수 page 조정
            page += 1
            query_url = "?mode=LS2D&sid2={0}&sid1={1}&mid=shm&date={2}&page={3}".format(sub_category, main_category, date, page)

            # 결과 값 반환
            yield scrapy.Request(url = self.base_url + query_url, callback = self.news_locator, cb_kwargs = dict(
                sub_category = sub_category,
                main_category = main_category,
                date = date,
                page = page
            ))

# ----------------------------------------------------------------------------------------------------

# NaverNewsCrawler() 클래스 정의
class NaverNewsCrawler(scrapy.Spider):

    # 스파이더 이름 정의
    name = "NaverNewsCrawler"

    # 접근 차단을 막기 위한 시간 지연 설정
    download_delay = 0.15

    # URL에 접속하기 위해 필요한 헤더(Header) 정보를 담은 딕셔너리 headers 초기화
    headers = {"user-agent": "'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

    # ----------------------------------------------------------------------------------------------------

    # start_requests() 함수 정의
    def start_requests(self):
        """
        크롤링을 수행할 웹 페이지에 HTTPS 요청을 보내고 콜백 함수로서 news_parser() 함수를 호출하는 함수입니다.\n
        scrapy 모듈의 Request 클래스 객체를 반환합니다.
        """

        # 크롤링을 위해 뉴스 URL을 담은 CSV 파일을 불러와 데이터프레임 생성
        news_df = pd.read_csv("./../data/news_3_naver_url.csv", header = 0, encoding = "utf-8-sig")
        
        # for 반복문을 사용하여 데이터프레임의 각 행을 순회
        for idx in news_df.index:

            # 분류, 제목, URL을 가져와 각 변수에 할당
            main_category = news_df.loc[idx, "MainCategory"]
            sub_category = news_df.loc[idx, "SubCategory"]
            title = news_df.loc[idx, "Title"].strip()
            url = news_df.loc[idx, "URL"]

            # 결과 값 반환
            yield scrapy.Request(url = url, callback = self.news_parser, headers = self.headers, cb_kwargs = dict(
                main_category = main_category,
                sub_category = sub_category,
                title = title
            ))

    # ----------------------------------------------------------------------------------------------------

    # news_parser() 함수 정의
    def news_parser(self, response, title : str, main_category : str, sub_category : str):
        """
        네이버 뉴스 웹 페이지에서 분류, 작성일자, 제목, 내용, URL, 사진 URL, 기자, 뉴스사, 스티커 반응을 추출하는 함수입니다.\n
        scrapy 모듈의 Item 클래스 객체를 반환합니다.
        """

        # 현재 크롤링을 진행하고 있는 웹 페이지 주소를 출력
        url = response.url
        print(f">>> 다음 URL을 크롤링 중입니다: {url}\n")

        # NewsItem() 클래스를 가져와 변수 item에 할당
        item = NewsItem()

        # 뉴스 기사의 대분류와 소분류, 제목, URL, 뉴스사, 기자, 사진 URL을 가져와 각 열에 할당
        item["MainCategory"] = main_category
        item["SubCategory"] = sub_category
        item["Title"] = title
        item["URL"] = url
        item["Press"] = response.css(".media_end_head_top a img::attr(title)").get()
        item["Writer"] = "".join(response.css(".media_end_head_journalist_layer_name::text").extract())
        item["PhotoURL"] = "".join(response.css(".nbd_im_w .nbd_a img::attr(data-src)").extract())

        # 뉴스 기사의 내용이 존재하는 두 가지 경우에 따라 내용을 가져와 할당
        if not response.css("#dic_area ::text").extract():
            item["Content"] = "".join(response.css("#dic_area .article ::text").extract())
        else:
            item["Content"] = "".join(response.css("#dic_area ::text").extract())

        # 뉴스 기사의 작성일자를 writed_at_transformer() 함수를 호출하여 저장
        item["WritedAt"] = self.writed_at_transformer(response.css(".media_end_head_info_datestamp_time::attr(data-date-time)").get())

        # 뉴스 기사의 스티커 반응을 stickers_crawler() 함수를 호출하여 저장
        item["Stickers"] = self.stickers_crawler(url)

        # 결과 값 반환
        yield item

    # ----------------------------------------------------------------------------------------------------

    # writed_at_transformer() 함수 정의
    def writed_at_transformer(self, time : str) -> str:
        """
        뉴스의 작성일자 문자열을 입력받아 작성일자를 추출해 변환하는 함수입니다.\n
        '연-월-일 시:분'으로 구성된 문자열(String) 객체를 반환합니다.
        """

        # ① strptime() 메서드를 사용해 datetime 객체로 변환
        # ② strftime() 메서드를 사용해 데이터베이스에 들어가야 할 양식의 문자열 객체로 변환해 변수 writed_at_date에 할당
        writed_at_date = datetime.strptime(time, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")

        # 결과 값 반환
        return writed_at_date

    # ----------------------------------------------------------------------------------------------------

    # stickers_crawler() 함수 정의
    def stickers_crawler(self, news_url : str) -> dict:
        """
        뉴스 기사의 URL을 입력 받아 해당 뉴스의 스티커 반응을 크롤링하여 추출하는 함수입니다.\n
        뉴스의 스티커 반응이 담긴 딕셔너리(Dictionary)를 반환합니다.
        """

        # 스티커 반응이 존재하는 쿼리 스트링 제거 URL을 stickers_base_url에 할당
        stickers_base_url = "https://news.like.naver.com/v1/search/contents"

        # 쿼리 스트링(Query String)에 사용할 값을 추출
        press_id = news_url.split("/")[5]
        article_id = news_url.split("/")[6].split("?")[0]

        # 딕셔너리 headers에 "referer" 값 추가
        self.headers["referer"] = news_url

        # 쿼리 스트링(Query String)을 stickers_query_url에 할당
        stickers_query_url = f"?callback=jQuery33107358087160083342_1669946908463&q=%5D%7CNEWS%5Bne_{press_id}_{article_id}%5D"

        # get() 함수를 사용해 스티커 반응 정보를 요청해 변수 res에 할당
        res = requests.get(stickers_base_url + stickers_query_url , headers = self.headers)

        # loads() 함수를 사용해 JSON 문자열을 객체로 변환해 json_res에 할당
        json_res = json.loads(re.search("\((.*?)\);", res.text).group(1))["contents"][0]["reactionMap"]

        # 딕셔너리 stickers_dict 초기화
        stickers_dict ={"쏠쏠정보": 0, "흥미진진": 0, "공감백배": 0, "분석탁월": 0, "후속강추": 0}

        # for 반복문을 사용해 딕셔너리 stickers_dict에 반응의 수를 값(Value)에 추가
        for value in json_res.values():
            if value["reactionType"] == "useful": stickers_dict["쏠쏠정보"] += value["count"]
            elif value["reactionType"] == "wow": stickers_dict["흥미진진"] += value["count"]
            elif value["reactionType"] == "touched": stickers_dict["공감백배"] += value["count"]
            elif value["reactionType"] == "analytical": stickers_dict["분석탁월"] += value["count"]
            elif value["reactionType"] == "recommend": stickers_dict["후속강추"] += value["count"]
            else: pass

        # 결과 값 반환
        return stickers_dict

# ----------------------------------------------------------------------------------------------------

# NaverNewsCommentCrawler() 클래스 정의
class NaverNewsCommentCrawler(scrapy.Spider):

    # 스파이더 이름 정의
    name = "NaverNewsCommentCrawler"

    # 접근 차단을 막기 위한 시간 지연 설정
    download_delay = 0.15

    # URL에 접속하기 위해 필요한 헤더(Header) 정보를 담은 딕셔너리 headers 초기화
    headers = {"user-agent": "'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

    # ----------------------------------------------------------------------------------------------------

    # start_requests() 함수 정의
    def start_requests(self):
        """
        크롤링을 수행할 웹 페이지에 HTTPS 요청을 보내고 콜백 함수로서 comment_parser() 함수를 호출하는 함수입니다.\n
        scrapy 모듈의 Request 클래스 객체를 반환합니다.
        """

        # 크롤링을 위해 뉴스 URL을 담은 CSV 파일을 불러와 데이터프레임 생성
        news_df = pd.read_csv("./../data/news_3_naver_url.csv", header = 0, encoding = "utf-8-sig")
        
        # for 반복문을 사용하여 데이터프레임의 각 행을 순회
        for idx in news_df.index:

            # URL을 가져와 각 변수에 할당
            url = news_df.loc[idx, "URL"]

            # 결과 값 반환
            yield scrapy.Request(url = url, callback = self.comment_parser, headers = self.headers)

    # ----------------------------------------------------------------------------------------------------

    # comment_parser() 함수 정의
    def comment_parser(self, response):
        """
        네이버 뉴스 웹 페이지에서 URL, 댓글을 단 유저 ID 및 닉네임, 댓글 작성일자, 댓글 내용을 추출하는 함수입니다.\n
        scrapy 모듈의 Item 클래스 객체를 반환합니다.
        """

        # 현재 크롤링을 진행하고 있는 웹 페이지 주소를 출력
        url = response.url
        print(f">>> 다음 URL을 크롤링 중입니다: {url}\n")

        # CommentItem() 클래스를 가져와 변수 item에 할당
        item = CommentItem()

        # 댓글이 존재하는 쿼리 스트링 제거 URL을 comment_base_url에 할당
        comment_base_url = "https://cbox5.apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json"

        # 쿼리 스트링(Query String)에 사용할 값을 추출 및 정의
        press_id = url.split("/")[5]
        article_id = url.split("/")[6].split("?")[0]
        section_id = url.split("=")[1]
        template_id = {"104": "view_world", "105": "view_it"}

        # 딕셔너리 headers에 "referer" 값 추가
        self.headers["referer"] = f"https://n.news.naver.com/mnews/article/comment/{press_id}/{article_id}?sid={section_id}"

        # 쿼리 스트링(Query String)을 comment_query_url에 할당
        comment_query_url = f"?ticket=news&templateId={template_id[section_id]}&pool=cbox5&lang=ko&objectId=news{press_id}%2C{article_id}&pageSize=100&pageType=more"

        # while 반복문을 사용해 각 댓글 페이지를 차례로 순회
        while True:
            
            # get() 함수를 사용해 스티커 반응 정보를 요청해 변수 res에 할당
            res = requests.get(comment_base_url + comment_query_url , headers = self.headers)

            # loads() 함수를 사용해 JSON 문자열을 객체로 변환해 json_res에 할당
            json_res = json.loads(re.search("\((.*?)\);", res.text).group(1))["result"]["commentList"]

            # for 반복문을 사용해 각 댓글을 순회
            for comment in json_res:

                # 뉴스 URL, 댓글을 단 유저 ID 및 닉네임, 작성일자, 내용을 가져와 각 열에 할당
                item["URL"] = url
                item["UserID"] = comment["userIdNo"]
                item["UserName"] = comment["maskedUserName"]
                item["WritedAt"] = self.writed_at_transformer(comment["regTime"])
                item["Content"] = comment["contents"]

                # 결과 값 반환
                yield item

            # 다음 댓글의 ID를 추출해 변수 next_comment에 할당
            next_comment = json.loads(re.search("\((.*?)\);", res.text).group(1))["result"]["morePage"]["next"]

            # 마지막 댓글의 ID를 추출해 변수 end_comment에 할당
            end_comment = json.loads(re.search("\((.*?)\);", res.text).group(1))["result"]["morePage"]["end"]

            # 다음 댓글과 마지막 댓글이 같을 경우 댓글 크롤링 중단
            if next_comment == end_comment:
                break

            # 다음 페이지의 쿼리 스트링(Query String)을 comment_query_url에 새로 할당
            comment_query_url = f"?ticket=news&templateId={template_id[section_id]}&pool=cbox5&lang=ko&objectId=news{press_id}%2C{article_id}&pageSize=100&pageType=more&moreParam.next={next_comment}"

    # ----------------------------------------------------------------------------------------------------

    # writed_at_transformer() 함수 정의
    def writed_at_transformer(self, time : str) -> str:
        """
        댓글의 작성일자 문자열을 입력받아 작성일자를 추출해 변환하는 함수입니다.\n
        '연-월-일 시:분'으로 구성된 문자열(String) 객체를 반환합니다.
        """

        # ① strptime() 메서드를 사용해 datetime 객체로 변환
        # ② strftime() 메서드를 사용해 데이터베이스에 들어가야 할 양식의 문자열 객체로 변환해 변수 writed_at_date에 할당
        writed_at_date = datetime.strptime(time.split('+')[0], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M")

        # 결과 값 반환
        return writed_at_date