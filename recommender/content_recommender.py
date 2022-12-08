# 필요한 패키지 불러오기
import pandas as pd
import numpy as np
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.metrics.pairwise import cosine_similarity

# ----------------------------------------------------------------------------------------------------

# doc2vec_model_maker() 함수 정의
def doc2vec_model_maker(tagged_data, tok, vector_size : int = 128, window : int = 3, epochs : int = 40, min_count : int = 0, workers : int = 4):

    model = Doc2Vec(tagged_data, vector_size = vector_size, window = window, epochs = epochs, min_count = min_count, workers = workers)
    model.save("./data/newflix_content_model.doc2vec")
#벡터 사이즈가 클수록 생성된 모델의 성능이 정교해지나 훈련 시간 및 메모리의 크기가 사이즈가 커진다는 단점이 있다

# ----------------------------------------------------------------------------------------------------

# preprocessed_data_importer() 함수 정의
def preprocessed_data_importer(preprocessed_data : pd.DataFrame) -> pd.DataFrame:
    
    doc2vec_data = preprocessed_data.copy()

    category_map_list = {
        "정치": 0, "경제": 1, "사회": 2, "생활/문화": 3, "문화": 3, "IT/과학": 4, "IT": 4,
        "세계": 5, "국제": 5, "연예": 6, "스포츠": 7
    }

    doc2vec_data["MainCategory"] = doc2vec_data["MainCategory"].map(category_map_list)
    doc2vec_data["TitleContent"] = doc2vec_data["Title"] + " " + doc2vec_data["Content"]
    doc2vec_data.drop(["Title", "Content"], axis = 1, inplace = True)

    # 결과 값 반환
    return doc2vec_data

# ----------------------------------------------------------------------------------------------------

# doc2vec_data_maker() 함수 정의
def doc2vec_data_maker(doc2vec_data : pd.DataFrame, column : str = "TitleContent", tagged_document = False):

    doc2vec_list = []

    for tag, doc in zip(doc2vec_data["ID"], doc2vec_data[column]):
        doc = doc.split(" ")
        doc2vec_list.append(([tag], doc))

    if tagged_document:
        tagged_doc2vec_list = [TaggedDocument(words = doc, tags = tags) for tags, doc in doc2vec_list]

        return tagged_doc2vec_list

    else:
        return doc2vec_list

# ----------------------------------------------------------------------------------------------------

# 코사인 유사도를 구행 5개 추천
def contents_recommender(user, doc2vec_list, model):

    scores = []

    for tags, doc in doc2vec_list:
        trained_doc_vec = model.docvecs[tags[0]]
        scores.append(cosine_similarity(user.reshape(-1, 128), trained_doc_vec.reshape(-1, 128)))

    scores = np.array(scores).reshape(-1)
    scores = np.argsort(-scores)[:5]
    
    return data.loc[scores, :]

# ----------------------------------------------------------------------------------------------------

# content vector 기반의 user history 를 평균해서 user embedding을 만들어주는 함수 
def make_user_embedding(index_list, data_doc, model):
    user = []
    user_embedding = []
    for i in index_list:
        user.append(data_doc[i][0][0])
    for i in user:
        user_embedding.append(model.docvecs[i])
    user_embedding = np.array(user_embedding)
    user = np.mean(user_embedding, axis = 0)
    return user

def view_user_history(data):
    print(data[['category', 'title_content']])






# #doc2vec 전처리
# data_doc_title_content_tag = make_doc2vec_data(data, 'title_content', t_document=True)
# data_doc_title_content = make_doc2vec_data(data, 'title_content')
# data_doc_tok_tag = make_doc2vec_data(data, 'mecab_tok', t_document=True)
# data_doc_tok = make_doc2vec_data(data, 'mecab_tok')
# #tag가 붙는 데이터는 doc2vec model 학습에 사용됨
# #없는 데이터는 user embeddinf, cosine similarity 를 구할때 사용




# #doc2vec학습/ 만들어 두었던 함수 사용
# #tok = True 로 보내면 각각 데이터에 맞게 doc2vec 모델에 저장됨


# make_doc2vec_models(data_doc_title_content_tag, tok=False)
# make_doc2vec_models(data_doc_tok_tag, tok=True)








# model_title_content = Doc2Vec.load('./datas/False_news_model.doc2vec')

# model_tok = Doc2Vec.load('./datas/True_news_model.doc2vec')

# #user 임베딩한 결과를 user에 넣는다 
# result = get_recommened_contents(user , data_doc_title_content, model_title_content)
# pd.DataFrame(result.loc[:,['category', 'title_content']])
