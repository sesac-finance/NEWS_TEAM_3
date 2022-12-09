from rest_framework import serializers
from .models import TbNews, TbCount

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TbNews
        fields = ('id', 'maincategory', 'subcategory', 'title', 'content', 'writedat', 'url')

# class PopularSerializer(serializers.ModelSerializer):
#     news = NewsSerializer(
#         read_only=True,
#         # slug_field=('id', 'maincategory', 'subcategory', 'title', 'writedat')
#      )

#     class Meta:
#         model = TbCount
#         fields = ('news','count')

# class RecommendSerializer(serializers.ModelSerializer):
#     class Meta:
