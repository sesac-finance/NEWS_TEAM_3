from django.shortcuts import HttpResponse, get_object_or_404, get_list_or_404, render
from .models import Article
import json
from .serializers import ArticleSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
def main(request):
    article = Article.objects.get()
    json.dumps(article)
    return HttpResponse(json.dumps(article))

@api_view(["GET"])
def detail(request, article_id):
    article = get_object_or_404(Article, pk = article_id)
    serializer = ArticleSerializer(article)
    return  Response(serializer.data, status = status.HTTP_200_OK)

@api_view(["GET", "POST"])
def list_article(request):
    if request.method == "GET":
        articles = get_list_or_404(Article)
        serializer = ArticleSerializer(articles, many = True)
        return  Response(serializer.data, status = status.HTTP_200_OK)
    if request.method == "POST":
        articles = get_list_or_404(Article)
        serializer = ArticleSerializer(articles, pk = 1)
        return  Response(serializer.data, status = status.HTTP_200_OK)

# def list_article(request):
#     try:
#         article_list = Article.objects.all()
#         if not request.query["age"]: return 500 # internal server errors

#         if not article_list:
#             return []

#         return article_list
#     except:
#         return 500 # internal server errors