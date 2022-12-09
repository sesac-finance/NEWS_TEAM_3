from django.shortcuts import render, get_list_or_404, get_object_or_404, HttpResponse

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import TbNews, TbCount, TbRecommend
from .serializers import NewsSerializer

# Create your views here.
@api_view(['GET'])
def detail(request, news_id):
    news = get_object_or_404(TbNews, pk=news_id)
    serializer = NewsSerializer(news)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_news(request):
    news_many = TbNews.objects.all().order_by('-writedat')[:20]
    serializer = NewsSerializer(news_many, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_popular(request):
    populars = TbCount.objects.all().order_by('-count')[:20]
    # print([p.newsid for p in populars])
    serializer = NewsSerializer([p.newsid for p in populars], many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_recommend(request, news_id):
    reco = get_object_or_404(TbRecommend, pk=news_id)
    recom_list = reco.recommendation.replace('[', '').replace(']', '').split(',')
    news_list = TbNews.objects.filter(pk__in=recom_list)
    serializer = NewsSerializer(news_list, many=True)

    return Response(data = serializer.data, status = status.HTTP_200_OK)