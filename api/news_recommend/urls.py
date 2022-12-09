app_name = 'news_recommend'

from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_news),
    path("<int:news_id>/", views.detail),
    path("popular/", views.list_popular),
    path("<int:news_id>/con_recom/", views.list_recommend),
]