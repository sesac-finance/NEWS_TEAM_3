# 필요한 패키지 불러오기
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

# ----------------------------------------------------------------------------------------------------

# content_recommender() 함수 정의
def content_recommender(preprocessed_data : pd.DataFrame) -> pd.DataFrame:
    """
    콘텐츠 기반 필터링을 위해 전처리된 제목 및 내용이 담긴 데이터프레임을 입력 받아 콘텐츠 기반 필터링에 기초한 추천 알고리즘을 수행합니다.
    코사인 유사도(Cosine Similarity)가 높은 상위 5개 뉴스의 뉴스 ID가 담긴 판다스(pandas) 데이터프레임(Dataframe)을 반환합니다.
    """

    # preprocessed_data_importer() 함수를 호출해 doc2vec_data 데이터프레임 반환
    doc2vec_data = preprocessed_data_importer(preprocessed_data)

    # doc2vec_data_maker() 함수를 호출해 doc2vec_list, tagged_doc2vec_list 리스트 반환
    doc2vec_list = doc2vec_data_maker(doc2vec_data)
    tagged_doc2vec_list = doc2vec_data_maker(doc2vec_data, tagged_document = True)

    # doc2vec_model_maker() 함수를 호출해 모형을 저장
    doc2vec_model_maker(tagged_doc2vec_list)

    # load() 메서드를 사용해 모형을 불러와 model에 할당
    model = Doc2Vec.load("./data/newflix_content_model.doc2vec")

    # 모형 생성 완료를 알려주는 안내 메시지 출력
    print(f">>> Doc2Vec 모형 학습이 완료되었습니다.\n")

    # 추천 시스템에 의한 뉴스 추천 목록을 저장할 데이터프레임 reulst_df 초기화
    result_df = pd.DataFrame(columns = ["ID", "Recommendation"])

    # for 반복문을 사용해 각 뉴스 기사의 ID 값을 순회
    for news_id in preprocessed_data.loc["ID"]:

        # 코사인 유사도 계산 중인 뉴스 ID를 알려주는 안내 메시지 출력
        print(f">>> {news_id}번 뉴스의 코사인 유사도를 계산을 시작합니다.\n")

        # 코사인 유사도 점수를 담을 리스트 scores 초기화
        scores = []

        # for 반복문을 사용해 doc2vec_list의 각 태그를 순회
        for tags, _ in doc2vec_list:

            # 각 뉴스 기사와 다른 뉴스 기사의 코사인 유사도를 계산해 scores 리스트에 추가
            scores.append(cosine_similarity(model.dv[str(news_id)].reshape(-1, 128), model.dv[tags[0]].reshape(-1, 128)))

        # scores 리스트를 넘파이 배열로 변환
        scores = np.array(scores).reshape(-1)

        # 코사인 유사도가 가장 높은 뉴스 ID를 1위부터 5위까지 추출해 리스트로 변환
        recommended_news_id = (np.argsort(-scores)[1 : 6] + 1).tolist()

        # 뉴스 ID와 코사인 유사도가 가장 높은 뉴스 ID를 담은 데이터프레임 temp_df 생성
        temp_df = pd.DataFrame([news_id, recommended_news_id])

        # concat() 함수를 사용해 result_df에 temp_df 병합
        result_df = pd.concat([result_df, temp_df], axis = 0, ignore_index = True)

        # 코사인 유사도 계산이 완료된 뉴스 ID를 알려주는 안내 메시지 출력
        print(f">>> {news_id}번 뉴스의 코사인 유사도를 계산이 완료되었습니다.\n")

    # 코사인 유사도 계산 완료를 알려주는 안내 메시지 출력
    print(f">>> 코사인 유사도를 계산이 모두 완료되었습니다.\n")

    # 결과 값 반환
    return result_df

# ----------------------------------------------------------------------------------------------------

# preprocessed_data_importer() 함수 정의
def preprocessed_data_importer(preprocessed_data : pd.DataFrame) -> pd.DataFrame:
    """
    콘텐츠 기반 필터링을 위해 전처리된 제목 및 내용이 담긴 데이터프레임을 불러와 Doc2Vec 모형에 사용할 수 있도록 가공하는 함수입니다.\n
    제목 및 내용을 하나의 열로 합친 판다스(pandas) 데이터프레임(Dataframe)을 반환합니다.
    """
    
    # copy() 메서드를 사용해 전처리된 데이터프레임을 데이터프레임 doc2vec_data에 복사
    doc2vec_data = preprocessed_data.copy()

    # 뉴스 제목과 본문의 내용을 합쳐 "TitleContent" 열에 추가
    doc2vec_data["TitleContent"] = doc2vec_data["Title"] + " " + doc2vec_data["Content"]

    # drop() 메서드를 사용해 기존 "Title" 열과 "Content" 열을 삭제
    doc2vec_data.drop(["Title", "Content"], axis = 1, inplace = True)

    # 결과 값 반환
    return doc2vec_data

# ----------------------------------------------------------------------------------------------------

# doc2vec_data_maker() 함수 정의
def doc2vec_data_maker(doc2vec_data : pd.DataFrame, tagged_document : bool = False) -> list:
    """
    제목 및 내용을 하나의 열로 합친 판다스(pandas) 데이터프레임(Dataframe) 객체에서 ID와 단어들을 추출하는 함수입니다.\n
    추출한 값을 리스트(List)로 바꾸고, 이를 다시 튜플(Tuple)로 묶인 리스트(List)로 반환합니다.\n
    Doc2Vec 모형에 사용할 TaggedDocument 객체를 반환받기 위해서는 'tagged_document' 인수를 'True'로 설정해야 합니다.
    """

    # 태그와 문서의 텍스트 내용을 담을 리스트 doc2vec_list 초기화
    doc2vec_list = []

    # for 반복문을 사용해 데이터프레임의 "ID" 열과 "TitleContent" 열을 각각 순회
    for tag, doc in zip(doc2vec_data["ID"], doc2vec_data["TitleContent"]):

        # split() 메서드를 사용해 "TitleContent" 열의 내용을 단어로 구성된 리스트로 변환
        doc = doc.split(" ")

        # 뉴스 기사 ID와 단어로 구성된 기사 내용을 튜플(Tuple)로 묶어 doc2vec_list에 추가
        doc2vec_list.append(([str(tag)], doc))

    # 'tagged_document' 인수가 'True'인 경우
    if tagged_document:

        # Doc2Vec 모형에 사용할 수 있도록 TaggedDocument 객체로 구성된 리스트 tagged_doc2vec_list 반환
        tagged_doc2vec_list = [TaggedDocument(words = doc, tags = tags) for tags, doc in doc2vec_list]

        # 결과 값 반환
        return tagged_doc2vec_list

    # 'tagged_document' 인수가 'False'인 경우
    else:

        # 결과 값 반환
        return doc2vec_list

# ----------------------------------------------------------------------------------------------------

# doc2vec_model_maker() 함수 정의
def doc2vec_model_maker(tagged_doc2vec_list, vector_size : int = 128, window : int = 3, epochs : int = 40, min_count : int = 1, workers : int = 4) -> Doc2Vec:
    """
    Doc2Vec 모형을 만들고, TaggedDocument 객체로 가공된 데이터로 학습을 수행하는 함수입니다.\n
    학습 수행의 결과를 담은 Doc2Vec 파일을 저장합니다.\n
    [인수 ①] vector_size: 임베딩 벡터의 크기\n
    [인수 ②] window: 학습 시 앞뒤로 고려하는 단어의 개수\n
    [인수 ③] epochs: 학습의 반복 횟수\n
    [인수 ④] min_count: 데이터에 등장하는 단어의 최소 빈도 수\n
    [인수 ⑤] workers: 모형에 사용할 스레드(Thread)의 개수
    """

    # 입력한 인수 값을 토대로 모형을 생성하고 학습을 수행
    model = Doc2Vec(
        documents = tagged_doc2vec_list,
        vector_size = vector_size,
        window = window,
        epochs = epochs,
        min_count = min_count,
        workers = workers
    )

    # save() 메서드를 사용해 모형을 저장
    model.save("./data/newflix_content_model.doc2vec")