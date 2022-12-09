# 필요한 패키지 불러오기
import pandas as pd
import json
import pymysql
import warnings
import re
from konlpy.tag import Mecab

# ----------------------------------------------------------------------------------------------------

# ArticlePreprocessor() 클래스 정의
class ArticlePreprocessor():

    # 뉴스 기사의 ID, 제목, 본문을 담을 raw_data 데이터프레임 초기화
    raw_data = pd.DataFrame()

    # ----------------------------------------------------------------------------------------------------

    # __init__() 함수 정의
    def __init__(self):
        """
        클래스를 생성할 때 실행되는 생성자 함수로, 로컬 데이터베이스(Local Database)와 연결해 뉴스 기사의 ID, 제목, 본문을 불러옵니다.\n
        판다스(pandas) 데이터프레임(DataFrame)으로 변환해 raw_data 속성 값으로 저장합니다.
        """

        # 데이터베이스 설정 파일을 불러와 loads() 함수를 사용해 JSON 문자열을 객체로 변환
        with open("./preprocessor/db_config.json", "r", encoding = "utf-8") as file:
            db_config = json.load(file)

        # 불러온 설정을 활용해 데이터베이스와 연결
        connection = pymysql.connect(
            host = db_config["host"],
            user = db_config["user"],
            password = db_config["password"],
            database = db_config["database"],
            port = db_config["port"],
            charset = "utf8"
        )
        
        # filterwarnings() 함수를 사용해 UserWarning 경고문이 출력되지 않도록 설정
        warnings.filterwarnings(action = "ignore", category = UserWarning)

        # 뉴스 기사 테이블(Table)에서 뉴스 ID, 대분류, 제목, 내용을 불러오는 쿼리(Query)문을 sql에 할당
        sql =  "SELECT ID, Title, Content FROM tb_news"

        # read_sql() 함수를 사용해 필요한 데이터를 불러와 데이터프레임으로 변환
        self.raw_data = pd.read_sql(sql = sql, con = connection).loc[: 100000]

        # resetwarnings() 함수를 사용해 경고문 출력을 초기화
        warnings.resetwarnings()

    # ----------------------------------------------------------------------------------------------------

    # fit() 함수 정의
    def fit(self) -> pd.DataFrame:
        """
        데이터베이스에서 불러온 raw_data 속성 값을 활용해 전처리 작업을 수행하는 함수입니다.\n
        전처리된 뉴스 기사 제목 및 내용, 뉴스 기사 ID, 뉴스 기사 대분류가 담긴 판다스(pandas) 데이터프레임(Dataframe)을 반환합니다.
        """

        # 전처리된 결과를 담을 preprocessed_data 데이터프레임 초기화
        preprocessed_data = self.raw_data[["ID"]].copy()

        # text_cleanser() 함수를 호출해 불필요한 내용 제거 작업 수행 후 안내 메시지 출력
        preprocessed_data["Title"] = self.raw_data["Title"].copy().apply(lambda x: self.text_cleanser(x))
        preprocessed_data["Content"] = self.raw_data["Content"].copy().apply(lambda x: self.text_cleanser(x))
        print(">>> 뉴스기사 제목 및 내용의 클렌징 작업이 완료되었습니다.")

        # 각 함수를 호출해 형태소 분석, 품사 태깅, 불용어 제거 작업 수행 후 안내 메시지 출력
        preprocessed_data["Title"] = preprocessed_data["Title"].apply(lambda x: self.stopwords_remover(self.tag_selector(self.morpheme_analyzer(x))))
        preprocessed_data["Content"] = preprocessed_data["Content"].apply(lambda x: self.stopwords_remover(self.tag_selector(self.morpheme_analyzer(x))))
        print(">>> 뉴스기사 제목 및 내용의 전처리 작업이 완료되었습니다.")

        # fillna() 메서드를 사용해 결측값을 제거 후 안내 메시지 출력
        preprocessed_data.fillna("")
        print(">>> 결측값을 빈 문자열로 대체하였습니다.")

        # 결과 값 반환
        return preprocessed_data

    # ----------------------------------------------------------------------------------------------------

    # text_cleanser() 함수 정의
    def text_cleanser(self, news_text : str) -> str:
        """
        뉴스 기사의 제목 또는 내용이 담긴 문자열을 입력 받아 문장 부호와 불필요한 내용을 제거하는 함수입니다.\n
        전처리된 뉴스 기사 제목 또는 내용이 담긴 문자열(String)을 반환합니다.
        """

        # compile() 함수와 sub() 메서드를 사용해 괄호 안의 모든 문자, 한글을 제외한 모든 문자를 제거
        parenthesize_pattern = re.compile(r"\([^)]+\)|\[[^]]+\]|\<[^>]+\>|\{[^}]+\}|\〈[^〉]+\〉|\《[^》]+\》")
        no_korean_pattern = re.compile(r"[^가-힣ㄱ-ㅎㅏ-ㅣ ]")
        news_text = parenthesize_pattern.sub("", news_text).strip()
        news_text = no_korean_pattern.sub("", news_text).strip()

        # replace() 메서드를 사용해 줄바꿈을 제거
        news_text = news_text.replace("\n", "").replace("\t", "")

        # 결과 값 반환
        return news_text

    # ----------------------------------------------------------------------------------------------------

    # morpheme_analyzer() 함수 정의
    def morpheme_analyzer(self, news_text : str) -> list:
        """
        뉴스 기사의 제목 또는 내용이 담긴 문자열을 입력 받아 형태소 분석을 하는 함수입니다.\n
        형태소 분석의 결과가 담긴 리스트(List)를 반환합니다.
        """

        # Mecab 형태소 분석기를 tokenizer 변수에 할당
        tokenizer = Mecab()

        # morphs() 메서드를 사용해 형태소 분석을 한 결과를 news_token에 할당
        news_token = tokenizer.morphs(news_text)

        # 결과 값 반환
        return news_token
    
    # ----------------------------------------------------------------------------------------------------

    # tag_selector() 함수 정의
    def tag_selector(self, news_token : list) -> list:
        """
        형태소 분석의 결과가 담긴 리스트를 입력 받아 필요한 품사만 선택하는 함수입니다.\n
        특정 품사에 해당하는 형태소 목록만 담긴 리스트(List)를 반환합니다.
        """

        # 선택된 품사를 담은 딕셔너리 selected_tag 초기화
        selected_tag_dict = {"NNG": "일반명사", "NNP": "고유명사"}

        # Mecab 형태소 분석기를 tokenizer 변수에 할당
        tokenizer = Mecab()

        # pos() 메서드를 사용해 품사 태깅 작업을 수행한 결과를 pos_token에 할당
        pos_token = tokenizer.pos(" ".join(news_token))

        # 리스트 컴프리헨션(List Comprehension)을 사용해 선선택된 품사에 해당하고 글자 수 2개 이상인 형태소만 selected_token에 할당
        selected_token = [token[0] for token in pos_token if token[1] in selected_tag_dict.keys() and len(token[0]) != 1]

        # 결과 값 반환
        return selected_token

    # ----------------------------------------------------------------------------------------------------

    # stopwords_remover() 함수 정의
    def stopwords_remover(self, selected_token : list) -> str:
        """
        형태소 분석의 결과가 담긴 리스트를 입력 받아 불용어를 제거하는 함수입니다.\n
        불용어 목록을 불러와 불용어를 제거하고 리스트를 문자열로 병합해 반환합니다.
        """

        # 불용어 목록을 리스트 컴프리헨션(List Comprehension)으로 불러와 해당하는 단어를 제거
        with open("./preprocessor/korean_stopwords.txt", "r", encoding = "utf-8") as file:
            stopwords = [line.replace("\n", "") for line in file.readlines()]
            preprocessed_token = [token for token in selected_token if token not in stopwords]

        # join() 메서드를 사용해 각 단어 토큰을 하나의 문자열로 병합
        preprocessed_text = " ".join(preprocessed_token)

        # 결과 값 반환
        return preprocessed_text