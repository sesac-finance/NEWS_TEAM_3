# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter
import pandas as pd
from scrapy.exceptions import DropItem

class DaumCrawlerPipeline:
    def process_item(self, item, spider):
        # 지정한 파일 이름의 CSV 파일을 생성 후 열기
        self.file = open(f"./../Data/news_3.csv", "wb")

        # CSV 파일로 내보내기 시작
        self.exporter = CsvItemExporter(self.file, encoding = "utf-8-sig")
        self.exporter.start_exporting()
        return item
