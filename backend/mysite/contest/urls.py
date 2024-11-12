from django.urls import path
from . import views

app_name = 'contest'

urlpatterns = [
    path('', views.index, name='index'),
    path('submit/', views.submit_idea, name='submit_idea'),
    path('like/<int:idea_id>/', views.like_idea, name='like_idea'),
]
