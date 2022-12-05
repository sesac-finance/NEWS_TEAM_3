# 필요한 패키지 불러오기
import os
import pandas as pd

# ----------------------------------------------------------------------------------------------------

# CSV 파일의 경로를 상수 CSV_DIR에 할당
CSV_DIR = "./../data/" if __name__ == "main" else "./data/"

# ----------------------------------------------------------------------------------------------------

# file_list_maker() 함수 정의
def file_list_maker() -> pd.DataFrame:
    """
    CSV 파일 경로에서 파일 목록을 가져와 네이버 뉴스, 댓글, 다음 뉴스를 분류해주는 함수입니다.\n
    또한, 각 파일 목록을 분류해서 담은 리스트를 가져와 dataframe_maker()함수를 호출합니다.\n
    판다스 데이터프레임 객체를 반환합니다.
    """

    # listdir() 함수를 사용해 CSV 파일의 경로에 담긴 파일 목록을 리스트 file_list에 할당하고 안내 메시지 출력
    file_list = os.listdir(CSV_DIR)
    print(">>> 파일 목록을 불러왔습니다.\n")

    # 각 파일 목록을 담을 daum_news_list, naver_news_list, naver_comment_list 초기화
    daum_news_list, naver_news_list, naver_comment_list = [], [], []

    # for 반복문을 사용해 파일 목록에 담긴 각 파일을 순회
    for file in file_list:

        # CSV 확장자 파일인 경우
        if ".csv" in file:

            # 다음 뉴스인 경우 해당 리스트에 추가
            if file.split("_")[2] == "daum":
                daum_news_list.append(file)
            
            else:
                # 네이버 뉴스인 경우 해당 리스트에 추가
                if file.split("_")[3] == "news":
                    naver_news_list.append(file)

                    # 네이버 뉴스 댓글인 경우 해당 리스트에 추가
                if file.split("_")[3] == "comment":
                    naver_comment_list.append(file)
    
    # 데이터프레임 변환 작업의 시작을 알리는 안내 메시지 출력
    print(">>> 판다스 데이터프레임으로 변환 작업을 시작합니다.\n")

    # 각 CSV 파일 목록을 데이터프레임으로 변환해 주는 to_dataframe() 함수를 실행해 데이터프레임으로 변환
    daum_news_df = dataframe_maker(daum_news_list)
    naver_news_df = dataframe_maker(naver_news_list)
    naver_comment_df = dataframe_maker(naver_comment_list)

    # 데이터프레임 변환 작업의 끝을 알리는 안내 메시지 출력
    print(">>> 판다스 데이터프레임으로 변환 작업이 완료되었습니다.\n")

    # 결과 값 반환
    return daum_news_df, naver_news_df, naver_comment_df

# ----------------------------------------------------------------------------------------------------

# to_dataframe() 함수 정의
def dataframe_maker(file_list : list) -> pd.DataFrame:
    """
    파일 목록을 입력 받아 판다스(pandas) 데이터프레임(Dataframe) 객체로 바꿔주는 함수입니다.\n
    판다스 데이터프레임 객체를 반환합니다.
    """

    # CSV 파일의 내용을 병합해 담을 데이터프레임 list_df 초기화 
    list_df = pd.DataFrame()

    # for 반복문을 사용해 각 파일 목록의 파일을 순회
    for file in file_list:

        # read_csv() 함수를 사용해 각 파일을 불러와 데이터프레임으로 변환
        csv_df = pd.read_csv(CSV_DIR + file, header = 0, encoding = "utf-8-sig")
        
        # concat() 함수를 사용해 각 파일의 내용을 하나의 데이터프레임으로 병합
        list_df = pd.concat([list_df, csv_df])

    # 결과 값 반환
    return list_df