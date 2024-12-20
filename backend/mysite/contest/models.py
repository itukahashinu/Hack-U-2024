from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.core.cache import cache

# デフォルトテーマ取得用の関数
def get_default_theme():
    default_theme = cache.get('default_theme')
    if not default_theme:
        default_theme, created = Theme.objects.get_or_create(
            title='デフォルトテーマ',
            description='デフォルトテーマの説明',
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2050, 12, 31),
        )
        cache.set('default_theme', default_theme)
    return default_theme

# テーマモデル
class Theme(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    def __str__(self):
        return self.title

    @classmethod
    def get_default_theme(cls):
        default_theme, created = cls.objects.get_or_create(
            title='デフォルトテーマ',
            description='デフォルトテーマの説明',
            start_date='2020-01-01',
            end_date='2050-12-31',
        )
        return default_theme

class Idea(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, default=Theme.get_default_theme)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_ideas', blank=True)
    
    def __str__(self):
        return self.title
