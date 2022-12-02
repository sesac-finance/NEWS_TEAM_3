import json
import requests

def stickers_crawl(itemKey: str):
    '''
    스티커 크롤링 함수
    '''
    headers = {"authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwiZ3JhbnRfdHlwZSI6ImFsZXhfY3JlZGVudGlhbHMiLCJzY29wZSI6W10sImV4cCI6MTY2OTk4Mzk0OCwiYXV0aG9yaXRpZXMiOlsiUk9MRV9DTElFTlQiXSwianRpIjoiY2M0NmY3YzQtOTZiOC00MmExLWFmM2QtMmIxYjg5YWJhOTJiIiwiZm9ydW1faWQiOi05OSwiY2xpZW50X2lkIjoiMjZCWEF2S255NVdGNVowOWxyNWs3N1k4In0.Z8uOoHxjjVoM9mjp_YM_bn76k51HB9khO37tIxY3jPM"}
    reactionURL = 'https://action.daum.net/apis/v1/reactions/home?itemKey={}'.format(itemKey)
    response = requests.get(url = reactionURL, headers = headers)
    reactionjson = json.loads(response.text)['item']['stats']

    reaction_dict = {
            '추천해요': reactionjson['RECOMMEND'],
            '좋아요': reactionjson['LIKE'],
            '감동이에요': reactionjson['IMPRESS'],
            '화나요': reactionjson['ANGRY'],
            '슬퍼요': reactionjson['SAD']
    }

    return reaction_dict