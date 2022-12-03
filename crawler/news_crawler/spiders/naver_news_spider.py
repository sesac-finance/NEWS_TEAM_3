import pandas as pd
import scrapy
from datetime import datetime
from ..items import NewsURLItem, NewsItem, CommentItem
import requests
import json
import re

# IT/과학, 세계 관련 url 크롤링하기dff
class NaverNewsURLCrawler(scrapy.Spider):
    download_delay = 0.2
    name = 'NaverNewsURLCrawler'

    base_url = "https://news.naver.com/main/list.naver"

    # base_url 뒤에 들어가야할 숫자들
    it_sections = [731, 226, 227, 230, 732, 283, 229, 228]
    world_sections = [231, 232, 233, 234, 322]

    # it_sections = {731:"모바일", 226:"인터넷/SNS", 227:"통신/뉴미디어", 230: "IT 일반", 732: "보안/해킹",283: "컴퓨터", 229: "게임/리뷰", 228: "과학 일반"}
    # world_sections = {231 : "아시아/호주", 232 : "미국/중남미", 233:"유럽", 234 : "중동/아프리카", 322 : "세계 일반"}

    def start_requests(self):
        
        start_date = pd.to_datetime('20221101') # 시작 날짜
        end_date = pd.to_datetime('20221130') # 마지막 날짜
        period =  pd.date_range(start_date, end_date, freq='D').strftime('%Y%m%d') ## 일단위로 생성

        # for문을 돌면서 it에 관련된 뉴스 순회하기
        for it in self.it_sections[:3]: # 모바일, 인터넷/SNS 관련 뉴스
            # 기간만큼 순회
            for date in period[-1:]: # 크롤링할 기간 (마지막 11월 30일?)
                page = 1
                query_url = "?mode=LS2D&sid2={0}&sid1=105&mid=shm&date={1}&page={2}".format(it,date,page)

                yield scrapy.Request(url = self.base_url + query_url, callback=self.parse_it_news, cb_kwargs = dict(
                    it = it,
                    page = page,
                    date = date
                ))

        # for문을 돌면서 world에 관련된 뉴스 순회하기
        # for world in self.world_sections: # 아시아/호주,미국/중남미 관련 뉴스
        #     # 기간만큼 순회
        #     for date in period[:2]: # 크롤링할 기간 (이틀치)
        #         page = 1
        #         query_url = "?mode=LS2D&sid2={0}&sid1=104&mid=shm&date={1}&page={2}".format(world,date,page)

        #         yield scrapy.Request(url = self.base_url + query_url, callback=self.parse_world_news, cb_kwargs = dict(
        #             world = world,
        #             page = page,
        #             date = date
        #         ))

    def parse_it_news(self, response, it : int, date : str , page : int):
        item = NewsURLItem()
        
        # 크롤링 돌고 있는 현재 표시된 페이지
        current_page = int(response.xpath(f'//*[@id="main_content"]/div[3]/strong/text()').get())

        # 표시된 페이지와 +1 되는 페이지가 다르면 크롤링 멈춤
        if current_page != page:
            yield None

        else:
            # 한 페이지에 20개의 뉴스 url -> 사진이 없는 기사는 따로 처리
            for i in range(1, 11):
                if not response.xpath(f'//*[@id="main_content"]/div[2]/ul[1]/li[{i}]/dl/dt[2]/a/text()').extract():
                    item['maincategory'] = response.xpath(f'//*[@id="snb"]/h2/a/text()').extract()
                    item['subcategory']= response.xpath(f'//*[@id="main_content"]/div[1]/h3/text()').extract()
                    item['title'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[1]/li[{i}]/dl/dt/a/text()').extract()
                    item['url'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[1]/li[{i}]/dl/dt/a/@href').extract()
                    item['page'] = response.xpath(f'//*[@id="main_content"]/div[3]/strong/text()').extract()
                    yield item
                else:
                    item['maincategory'] = response.xpath(f'//*[@id="snb"]/h2/a/text()').extract()
                    item['subcategory']= response.xpath(f'//*[@id="main_content"]/div[1]/h3/text()').extract()
                    item['title'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[1]/li[{i}]/dl/dt[2]/a/text()').extract()
                    item['url'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[1]/li[{i}]/dl/dt[2]/a/@href').extract()
                    item['page'] = response.xpath(f'//*[@id="main_content"]/div[3]/strong/text()').extract()                  
                    yield item

            for i in range(1, 11):
                if not response.xpath(f'//*[@id="main_content"]/div[2]/ul[2]/li[{i}]/dl/dt[2]/a/text()').extract():
                    item['maincategory'] = response.xpath(f'//*[@id="snb"]/h2/a/text()').extract()
                    item['subcategory']= response.xpath(f'//*[@id="main_content"]/div[1]/h3/text()').extract()
                    item['title'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[2]/li[{i}]/dl/dt/a/text()').extract()
                    item['url'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[2]/li[{i}]/dl/dt/a/@href').extract()
                    item['page'] = response.xpath(f'//*[@id="main_content"]/div[3]/strong/text()').extract()
                    yield item
                else:
                    item['maincategory'] = response.xpath(f'//*[@id="snb"]/h2/a/text()').extract()
                    item['subcategory']= response.xpath(f'//*[@id="main_content"]/div[1]/h3/text()').extract()
                    item['title'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[2]/li[{i}]/dl/dt[2]/a/text()').extract()
                    item['url'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[2]/li[{i}]/dl/dt[2]/a/@href').extract()
                    item['page'] = response.xpath(f'//*[@id="main_content"]/div[3]/strong/text()').extract()                   
                    yield item
            
            page += 1
            query_url = "?mode=LS2D&sid2={0}&sid1=105&mid=shm&date={1}&page={2}".format(it,date,page)

            # 결과값 반환
            yield scrapy.Request(url = self.base_url + query_url, callback=self.parse_it_news, cb_kwargs = dict(
                it = it,
                page = page,
                date = date
            ))

    def parse_world_news(self, response, world : int, date : str , page : int):
        item = NewsURLItem()
        
        current_page = int(response.xpath(f'//*[@id="main_content"]/div[3]/strong/text()').get())
        # //*[@id="main_content"]/div[3]/strong
        if current_page != page:
            yield None

        else:
            
            # 한 페이지에 20개의 뉴스 url -> 사진이 없는 기사는 따로 처리
            for i in range(1, 11):
                if not response.xpath(f'//*[@id="main_content"]/div[2]/ul[1]/li[{i}]/dl/dt[2]/a/text()').extract():
                    item['maincategory'] = response.xpath(f'//*[@id="snb"]/h2/a/text()').extract()
                    item['subcategory']= response.xpath(f'//*[@id="main_content"]/div[1]/h3/text()').extract()
                    item['title'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[1]/li[{i}]/dl/dt/a/text()').extract()
                    item['url'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[1]/li[{i}]/dl/dt/a/@href').extract()
                    item['page'] = response.xpath(f'//*[@id="main_content"]/div[3]/strong/text()').extract()                   
                    yield item
                else:
                    item['maincategory'] = response.xpath(f'//*[@id="snb"]/h2/a/text()').extract()
                    item['subcategory']= response.xpath(f'//*[@id="main_content"]/div[1]/h3/text()').extract()   
                    item['title'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[1]/li[{i}]/dl/dt[2]/a/text()').extract()
                    item['url'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[1]/li[{i}]/dl/dt[2]/a/@href').extract()
                    item['page'] = response.xpath(f'//*[@id="main_content"]/div[3]/strong/text()').extract()                                    
                    yield item

            for i in range(1, 11):
                if not response.xpath(f'//*[@id="main_content"]/div[2]/ul[2]/li[{i}]/dl/dt[2]/a/text()').extract():
                    item['maincategory'] = response.xpath(f'//*[@id="snb"]/h2/a/text()').extract()
                    item['subcategory']= response.xpath(f'//*[@id="main_content"]/div[1]/h3/text()').extract()
                    item['title'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[2]/li[{i}]/dl/dt/a/text()').extract()
                    item['url'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[2]/li[{i}]/dl/dt/a/@href').extract()
                    item['page'] = response.xpath(f'//*[@id="main_content"]/div[3]/strong/text()').extract()               
                    yield item
                else:
                    item['maincategory'] = response.xpath(f'//*[@id="snb"]/h2/a/text()').extract()
                    item['subcategory']= response.xpath(f'//*[@id="main_content"]/div[1]/h3/text()').extract()
                    item['title'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[2]/li[{i}]/dl/dt[2]/a/text()').extract()
                    item['url'] = response.xpath(f'//*[@id="main_content"]/div[2]/ul[2]/li[{i}]/dl/dt[2]/a/@href').extract()
                    item['page'] = response.xpath(f'//*[@id="main_content"]/div[3]/strong/text()').extract()
                    yield item
            
            page += 1
            query_url = "?mode=LS2D&sid2={0}&sid1=104&mid=shm&date={1}&page={2}".format(world,date,page)

            # 결과값 반환
            yield scrapy.Request(url = self.base_url + query_url, callback=self.parse_world_news, cb_kwargs = dict(
                world = world,
                page = page,
                date = date
            ))

class NaverNewsCrawler(scrapy.Spider):
    download_delay = 0.15
    name = 'NaverNewsCrawler'

    # start_requests() 함수 정의
    def start_requests(self):

        # 크롤링을 위해 뉴스 URL을 담은 CSV 파일을 불러와 데이터프레임 생성
        get_news = pd.read_csv("/Users/jang-yunji/Desktop/Project/NEWS_TEAM_3/naverscraper/naverurl.csv", header = 0, encoding = "utf-8-sig")
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }

        # Nan 값이 있으면 행 없애기
        news_df = get_news.dropna(axis=0)
        
        # for 반복문을 사용하여 데이터프레임의 각 행을 순회
        for idx in news_df.index:
            title = news_df.loc[idx, "title"].strip()
            url = news_df.loc[idx, "url"]
            subcategory = news_df.loc[idx, "subcategory"]
            maincategory = news_df.loc[idx, "maincategory"]
                
            yield scrapy.Request(url = url, callback = self.news_parser, headers = headers, cb_kwargs = dict(
                title = title,
                maincategory = maincategory,
                subcategory= subcategory ))
                
                
    def news_parser(self, response, title : str, maincategory : str, subcategory : str):

        # 현재 크롤링을 진행하고 있는 웹 페이지 주소를 출력
        url = response.url
        print(f">>> 다음 URL을 크롤링 중입니다: {url}\n")

        # NewsContentCrawlingItem() 클래스를 가져와 변수 item에 할당
        item = NewsItem()
        item['URL'] = url
        item['MainCategory'] = maincategory
        item['SubCategory'] = subcategory
        item['Title'] = title


        full_text = response.css('#dic_area::text').extract()

        if not full_text:
            response.css('#dic_area .article::text').extract()

        # 본문
        # response.css('#dic_area .article::text').extract() -> 어떤거는 ..
        # full_text = response.css('#dic_area::text').extract()
        get_text = '' 
        for text in full_text:    
            get_text += (text.strip()+' ')
        item['Content'] = get_text

        # 언론사
        item['Press'] = response.css('.media_end_head_top a img::attr(title)').get()
        
        # 기자
        item['Writer'] = response.css('.media_end_head_journalist_layer_name::text').getall()
        
        # 사진 url
        item['PhotoURL'] = response.css('.nbd_im_w .nbd_a img::attr(data-src)').getall()
        
        # 시간
        time = response.css('.media_end_head_info_datestamp_time::attr(data-date-time)').get()
        writed_at = datetime.strptime(time, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
        item['WritedAt'] = writed_at

        # 이모티콘
        item['Stickers'] = StickerCrawl(url)
        yield item

    def StickerCrawl(input_url : str):
        base_url = 'https://news.like.naver.com/v1/search/contents'
        
        object_Id_first = input_url[-22:-19]
        object_Id_second = input_url[-18:-8]
        
        if input_url[-3:] == '105': # 라면 templateId = view_it
            query_url = f'?suppress_response_codes=true&callback=jQuery33107358087160083342_1669946908463&q=%5D%7CNEWS%5Bne_{object_Id_first}_{object_Id_second}%5D&isDuplication=false'
            res = requests.get(base_url+query_url , 
                headers = {
                        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                        'referer': f'https://n.news.naver.com/mnews/article/{object_Id_first}/{object_Id_second}?sid=105'
                })

        elif input_url[-3:] == '104' : #라면 templateId = view_world
            query_url = f'?suppress_response_codes=true&callback=jQuery33107358087160083342_1669946908463&q=%5D%7CNEWS%5Bne_{object_Id_first}_{object_Id_second}%5D&isDuplication=false'
            res = requests.get(base_url+query_url , 
                headers = {
                        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                        'referer': f'https://n.news.naver.com/mnews/article/{object_Id_first}/{object_Id_second}?sid=104'
                })


        raw_text = res.text
        m = re.search('\((.*?)\);', raw_text)
        final_json = m.group(1)

        get_sticker = json.loads(final_json)
            # print(get_sticker)
        a = get_sticker['contents']
        b = a[0]['reactionMap']


        reaction_dict = {'쏠쏠정보' : 0, '흥미진진' : 0, '공감백배' : 0, '분석탁월' : 0, '후속강추': 0}

        for k, v in b.items():
            if v['reactionType'] == 'useful':
                reaction_dict['쏠쏠정보'] += v['count']

            elif v['reactionType'] == 'wow':
                reaction_dict['흥미진진'] += v['count']
                
            elif v['reactionType'] == 'touched':
                reaction_dict['공감백배'] += v['count']

            elif v['reactionType'] == 'analytical':
                reaction_dict['분석탁월'] += v['count']

            elif v['reactionType'] == 'recommend':
                reaction_dict['후속강추'] += v['count']

            # result.append(reaction_dict)

        return reaction_dict

def CommentCrawl(input_url : str):
    base_url = 'https://cbox5.apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json'

    object_Id_first = input_url[-22:-19]
    object_Id_second = input_url[-18:-8]

    if input_url[-3:] == '105': # 라면 templateId = view_it
        query_url = f'?ticket=news&templateId=view_it&pool=cbox5&lang=ko&objectId=news{object_Id_first}%2C{object_Id_second}&pageSize=100&indexSize=10&pageType=more&page=1&replyPageSize=20'
        res = requests.get(base_url+query_url , 
            headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                'referer': f'https://n.news.naver.com/mnews/article/comment/{object_Id_first}/{object_Id_second}?sid=105'
            })

    elif input_url[-3:] == '104' : #라면 templateId = view_world
        query_url = f'?ticket=news&templateId=view_world&pool=cbox5&lang=ko&objectId=news{object_Id_first}%2C{object_Id_second}&pageSize=100&indexSize=10&pageType=more&page=1&replyPageSize=20'
        res = requests.get(base_url+query_url , 
            headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                'referer': f'https://n.news.naver.com/mnews/article/comment/{object_Id_first}/{object_Id_second}?sid=104'
            })

    raw_text = res.text
    m = re.search('\((.*?)\);', raw_text)
    final_json = m.group(1)
    get_comment = json.loads(final_json)['result']['commentList']

    comment_result = []
    for comment in get_comment:
        userId = comment['userIdNo']
        userName = comment['maskedUserName']
        contents = comment['contents']
        regtime = comment['regTime']
        date = regtime[:10]
        time = regtime[11:16]
        writedAt = date + ' ' + time

        comment_dict = {}
        comment_dict['userId'] = userId
        comment_dict['userName'] = userName
        comment_dict['content'] = contents
        comment_dict['writedAt'] = writedAt
        comment_result.append(comment_dict)

    return comment_result