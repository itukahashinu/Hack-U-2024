from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# REST frameworkのルーター設定
router = DefaultRouter()
router.register(r'surveys', views.SurveyViewSet, basename='survey')

app_name = 'polls'
urlpatterns = [
    # 従来のDjangoビュー用のURL
    path('', views.index, name='index'),
    path('<int:question_id>/', views.detail, name='detail'),
    path('<int:question_id>/results/', views.results, name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    
    # API用のURL
    path('api/', include(router.urls)),
    
    # アンケート作成API
    path('api/create-survey/', views.create_survey, name='create-survey'),
    path('api/questions/<int:question_id>/', views.question_detail, name='question-detail'),
    # アンケート一覧と詳細のエンドポイント
    path('api/surveys/', views.survey_list, name='survey_list'),
    path('api/surveys/<int:survey_id>/', views.survey_detail, name='survey_detail'),
]