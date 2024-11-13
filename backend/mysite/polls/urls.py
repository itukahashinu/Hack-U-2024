from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# REST frameworkのルーター設定
router = DefaultRouter()
router.register(r'surveys', views.SurveyViewSet, basename='survey')

app_name = 'polls'
urlpatterns = [
    # メインページ
    path('', views.index, name='index'),
    
    # アンケート作成・管理
    path('surveys/create/', views.survey_create_view, name='survey_create'),
    
    # アンケート表示・回答
    path('surveys/<int:survey_id>/', views.survey_detail_view, name='survey_detail'),
    path('surveys/<int:survey_id>/response/', views.survey_response_view, name='survey_response'),
    
    # API エンドポイント
    path('api/', include(router.urls)),
    path('api/create-survey/', views.create_survey, name='create-survey'),
    path('api/questions/<int:question_id>/', views.question_detail, name='question-detail'),
    path('api/surveys/', views.survey_list, name='survey_list'),
    path('api/surveys/<int:survey_id>/', views.survey_detail, name='survey_detail'),
    path('api/surveys/<int:survey_id>/submit/', views.submit_survey_response, name='submit_survey_response'),
]