import pandas as pd
import os

CSV_DIR = './data/'

if __name__ == 'main':
    CSV_DIR = './../data/'

def file_list_maker():
    file_list = os.listdir(CSV_DIR)
    daum_news_list, naver_news_list, comment_list = [], [], []

    for file in file_list:
        if "csv" in file:
            if file.split("_")[2] == 'daum':
                daum_news_list.append(file)
            else:
                if file.split("_")[3] == 'comment':
                    comment_list.append(file)
                else:
                    naver_news_list.append(file)

    daum_news_to_dataframe(daum_news_list)
    naver_news_to_dataframe(naver_news_list)
    comment_to_dataframe(comment_list)

def daum_news_to_dataframe(daum_news_list):
    daum_news = pd.DataFrame()

    for daum_file in daum_news_list:
        daum_csv = pd.read_csv(CSV_DIR + daum_file)
        daum_news = pd.concat([daum_news, daum_csv])

    return daum_news

def naver_news_to_dataframe(naver_news_list):
    naver_news = pd.DataFrame()

    for naver_file in naver_news_list:
        naver_csv = pd.read_csv(CSV_DIR + naver_file)
        naver_news = pd.concat([naver_news, naver_csv])

    return naver_news

def comment_to_dataframe(comment_list):
    comment_df = pd.DataFrame()

    for comment_file in comment_list:
        comment_csv = pd.read_csv(CSV_DIR + comment_file)
        comment_df = pd.concat([comment_df, comment_csv])
    
    return comment_df