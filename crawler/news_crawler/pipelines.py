# 필요한 패키지 불러오기
from scrapy.exporters import CsvItemExporter
import pandas as pd
from scrapy.exceptions import DropItem

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

            # 50,000개 데이터가 담길 수 있도록 지정한 파일 이름으로 여러 개의 CSV 파일을 생성 후 열기
            self.files = dict([(file_num, open(self.export_dir + f"news_3_{export_name}_{file_num}.csv", "wb")) for file_num in range(1, 4, 1)])

            # 각 CSV 파일로 내보내기 시작
            self.exporters = dict([(file_num, CsvItemExporter(self.files[file_num], encoding = "utf-8-sig")) for file_num in range(1, 4, 1)])
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
            self.files = dict([(file_num, open(self.export_dir + f"news_3_{export_name}_{file_num}.csv", "wb")) for file_num in range(1, 21, 1)])

            # 각 CSV 파일로 내보내기 시작
            self.exporters = dict([(file_num, CsvItemExporter(self.files[file_num], encoding = "utf-8-sig")) for file_num in range(1, 21, 1)])
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
                print(">>> 다음과 같이 크롤링한 데이터가 존재하지 않습니다: ", item)
                raise DropItem()

            # Item 객체를 CSV 파일로 내보내기
            self.exporter.export_item(item)

        # 여러 파일에 대해 내보내기를 하는 경우
        else:

            # Item 객체를 50,000개씩 각 CSV 파일로 내보내기
            self.item_cnt += 1
            list(self.exporters.values())[(self.item_cnt - 1) // 50000].export_item(item)

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