# 필요한 패키지 불러오기
from scrapy.exporters import CsvItemExporter
import requests
import json
import pandas as pd
from scrapy.exceptions import DropItem
import os

# ----------------------------------------------------------------------------------------------------

# MultiCSVItemPipeline() 클래스 정의
class MultiCSVItemPipeline(object):

    # 파일을 저장할 경로를 담은 문자열 export_dir 초기화
    export_dir = "./../data/"

    # 저장할 파일 이름을 담은 리스트 export_names 초기화
    export_names = ["daum_news", "naver_url", "naver_news", "naver_comment"]

    # Item 클래스 객체의 개수를 셀 변수 item_cnt 초기화
    item_cnt = 0

    # ----------------------------------------------------------------------------------------------------

    # open_spider() 함수 정의
    def open_spider(self, spider):
        """
        스파이더(Spider)가 열릴 때 실행되는 함수입니다.\n
        크롤링한 데이터를 CSV 파일로 내보내는 과정을 시작합니다.
        """

        # 스파이더가 열릴 때 item_cnt를 다시 초기화 
        self.item_cnt = 0

        # Spider 클래스 객체 이름이 "DaumNewsCrawler"인 경우
        if spider.name == "DaumNewsCrawler":

            # 저장할 파일 이름을 "daum_news"로 설정
            export_name = self.export_names[0]

            # 쿼리 스트링(Query String)을 제외한 기본 URL을 base_url에 할당
            base_url = "https://sports.daum.net/media-api/harmony/contents.json"

            # 수집할 한 달 간의 날짜를 담은 search_period 변수 초기화
            search_period = "20221101000000~20221130235959"

            # 쿼리 스트링(Query String)을 query_url에 할당
            query_url = r"?consumerType=HARMONY&createDt={0}&discoveryTag%5B0%5D=%257B%2522group%2522%253A%2522media%2522%252C%2522key%2522%253A%2522defaultCategoryId3%2522%252C%2522value%2522%253A%25221004%2522%257D&size=100".format(search_period)

            # get() 함수를 사용해 뉴스 기사 정보를 요청해 변수 res에 할당
            res = requests.get(url = base_url + query_url)

            # loads() 함수를 사용해 JSON 문자열을 객체로 변환하고 뉴스 수를 추출해 변수 total_cnt에 할당
            total_cnt = int(json.loads(res.text)["result"]["total"])

            # 50,000개 데이터가 담길 수 있도록 지정한 파일 이름으로 여러 개의 CSV 파일을 생성 후 열기
            self.files = dict([(file_num, open(self.export_dir + f"news_3_{export_name}_{file_num}.csv", "wb")) for file_num in range(1, total_cnt // 50000 + 2, 1)])

            # 각 CSV 파일로 내보내기 시작
            self.exporters = dict([(file_num, CsvItemExporter(self.files[file_num], encoding = "utf-8-sig")) for file_num in range(1, total_cnt // 50000 + 2, 1)])
            for csv_exporter in self.exporters.values():
                csv_exporter.fields_to_export = ["MainCategory", "SubCategory", "WritedAt", "Title", "Content", "URL", "PhotoURL", "Writer", "Press", "Stickers"] 
                csv_exporter.start_exporting()

        # Spider 클래스 객체 이름이 "NaverNewsURLCrawler"인 경우
        elif spider.name == "NaverNewsURLCrawler":

            # 저장할 파일 이름을 "naver_url"로 설정
            export_name = self.export_names[1]
    
            # 지정한 파일 이름의 CSV 파일을 생성 후 열기
            self.file = open(self.export_dir + f"news_3_{export_name}.csv", "wb")

            # CSV 파일로 내보내기 시작
            self.exporter = CsvItemExporter(self.file, encoding = "utf-8-sig")
            self.exporter.fields_to_export = ["MainCategory", "SubCategory", "Title", "URL"] 
            self.exporter.start_exporting()
    
        # Spider 클래스 객체 이름이 "NaverNewsCrawler"인 경우
        elif spider.name == "NaverNewsCrawler":

            # 저장할 파일 이름을 "naver_news"로 설정
            export_name = self.export_names[2]

            # 네이버 뉴스 URL을 담은 CSV 파일을 불러와 데이터프레임 생성
            news_df = pd.read_csv(self.export_dir + "news_3_naver_url.csv", header = 0, encoding = "utf-8-sig")

            # 50,000개 데이터가 담길 수 있도록 지정한 파일 이름으로 여러 개의 CSV 파일을 생성 후 열기
            self.files = dict([(file_num, open(self.export_dir + f"news_3_{export_name}_{file_num}.csv", "wb")) for file_num in range(1, len(news_df) // 50000 + 2, 1)])

            # 각 CSV 파일로 내보내기 시작
            self.exporters = dict([(file_num, CsvItemExporter(self.files[file_num], encoding = "utf-8-sig")) for file_num in range(1, len(news_df) // 50000 + 2, 1)])
            for csv_exporter in self.exporters.values():
                csv_exporter.fields_to_export = ["MainCategory", "SubCategory", "WritedAt", "Title", "Content", "URL", "PhotoURL", "Writer", "Press", "Stickers"] 
                csv_exporter.start_exporting()

        # Spider 클래스 객체 이름이 "NaverNewsCommentCrawler"인 경우
        else:

            # 저장할 파일 이름을 "naver_comment"로 설정
            export_name = self.export_names[3]

            # 네이버 뉴스 URL을 담은 CSV 파일을 불러와 데이터프레임 생성
            news_df = pd.read_csv(self.export_dir + "news_3_naver_url.csv", header = 0, encoding = "utf-8-sig")

            # 50,000개 데이터가 담길 수 있도록 지정한 파일 이름으로 여러 개의 CSV 파일을 생성 후 열기
            self.files = dict([(file_num, open(self.export_dir + f"news_3_{export_name}_{file_num}.csv", "wb")) for file_num in range(1, 101, 1)])

            # 각 CSV 파일로 내보내기 시작
            self.exporters = dict([(file_num, CsvItemExporter(self.files[file_num], encoding = "utf-8-sig")) for file_num in range(1, 101, 1)])
            for csv_exporter in self.exporters.values():
                csv_exporter.fields_to_export = ["URL", "UserID", "UserName", "WritedAt", "Content"] 
                csv_exporter.start_exporting()

    # ----------------------------------------------------------------------------------------------------

    # process_item() 함수 정의
    def process_item(self, item, spider):
        """
       파이프라인 과정의 모든 Item 클래스 객체에 대해 실행되는 함수입니다.\n
        scrapy 모듈의 Item 클래스 객체를 반환합니다.
        """

        # 하나의 파일에 대해 내보내기를 하는 경우
        if spider.name == "NaverNewsURLCrawler":

            # 값이 존재하지 않는 경우 파이프라인에서 해당 객체 제거 후 오류 메시지 출력
            if not all(item.values()):
                print(">>> 다음과 같이 크롤링한 데이터가 존재하지 않습니다: ", item, "\n")
                raise DropItem()

            # Item 객체를 CSV 파일로 내보내기
            self.exporter.export_item(item)

        # 여러 파일에 대해 내보내기를 하는 경우
        else:

            # Item 객체를 50,000개씩 각 CSV 파일로 내보내기
            self.item_cnt += 1
            list(self.exporters.values())[(self.item_cnt - 1) // 50000].export_item(item)

            # 크롤링 중인 객체 수를 알려주는 메시지 출력
            print(">>> {0}번째 데이터의 수집이 완료되었습니다.\n".format(self.item_cnt))

        # 결과 값 반환
        return item

    # ----------------------------------------------------------------------------------------------------

    # close_spider() 함수 정의
    def close_spider(self, spider):
        """
        스파이더(Spider)가 종료될 때 실행되는 함수입니다.\n
        크롤링한 데이터를 CSV 파일로 내보내는 과정을 종료합니다.
        """

        # 하나의 파일에 대해 내보내기를 하는 경우
        if spider.name == "NaverNewsURLCrawler":

            # CSV 파일로 내보내기 종료
            self.exporter.finish_exporting()

            # CSV 파일 종료
            self.file.close()

        # 여러 파일에 대해 내보내기를 하는 경우
        else:

            # 각 CSV 파일로 내보내기 종료
            [csv_exporter.finish_exporting() for csv_exporter in self.exporters.values()]

            # 각 CSV 파일 종료
            [csv_file.close() for csv_file in self.files.values()]

            # 코멘트 크롤러의 경우 빈 CSV 파일을 제거하는 blank_file_remover() 함수 실행
            if spider.name == "NaverNewsCommentCrawler":
                self.blank_file_remover()

    # ----------------------------------------------------------------------------------------------------

    # blank_file_remover() 함수 정의
    def blank_file_remover(self):
        """
        스파이더 종료 후 빈 CSV 파일을 제거하는 함수입니다.
        """

        # listdir() 함수를 사용해 CSV 파일의 경로에 담긴 파일 목록을 리스트 file_list에 할당
        file_list = os.listdir(self.export_dir)

        # 빈 CSV 파일을 담을 리스트 blank_csv_list 초기화
        blank_csv_list = []

        # for 반복문을 사용해 파일 목록에 담긴 각 파일을 순회
        for file in file_list:

            # 댓글을 담은 CSV 파일인 경우 불러오기 오류가 발생 시 해당 파일을 blank_csv_list에 추가
            if "naver_comment" in file:
                try:
                    blank_checker = pd.read_csv(self.export_dir + file)
                    del blank_checker
                except pd.errors.EmptyDataError:
                    blank_csv_list.append(file)

        # for 반복문을 사용해 빈 CSV 파일 목록을 순회하며 파일을 삭제
        for file in blank_csv_list:
            os.remove(self.export_dir + file)

        # 빈 CSV 파일 삭제를 알려주는 메시지 출력
        print(">>>빈 CSV 파일을 모두 삭제하였습니다.\n".format(self.item_cnt))