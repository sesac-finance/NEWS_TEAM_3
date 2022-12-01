import json
import requests

def stickers_crawl(itemKey: str):
    '''
    스티커 크롤링 함수
    '''
    headers = {"authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb3J1bV9rZXkiOiJuZXdzIiwidXNlcl92aWV3Ijp7ImlkIjoxODQwNjExNSwiaWNvbiI6Imh0dHBzOi8vdDEuZGF1bWNkbi5uZXQvcHJvZmlsZS9jSFVGa2FKX2FaMTAiLCJwcm92aWRlcklkIjoiREFVTSIsImRpc3BsYXlOYW1lIjoi7J207Iqs6riwIn0sImdyYW50X3R5cGUiOiJhbGV4X2NyZWRlbnRpYWxzIiwic2NvcGUiOltdLCJleHAiOjE2Njk5MDE3NjgsImF1dGhvcml0aWVzIjpbIlJPTEVfREFVTSIsIlJPTEVfSURFTlRJRklFRCIsIlJPTEVfVVNFUiJdLCJqdGkiOiI3OGU2ZmExYi0zOGVkLTQ2MzUtYWYxNS05OTAyNTVjZTU3NjIiLCJmb3J1bV9pZCI6LTk5LCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgifQ.ZzQ_XtBLHh5XQK31OGRCBC5R31eJH-VUR538sIC0Ofc"}
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