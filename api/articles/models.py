from django.db import models

# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length = 32)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True) # 생성할 때 한 번만
    updated_at = models.DateTimeField(auto_now = True) # 계속 갱신