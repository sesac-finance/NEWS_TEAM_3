app_name = "articles"

from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_article),
    path("<int:article_id>/", views.detail)
]