from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# REST frameworkのルーター設定
router = DefaultRouter()
router.register(r'surveys', views.SurveyViewSet, basename='survey')

app_name = 'polls'
urlpatterns = [
    # インデックスページのURL
    path('', views.index, name='index'),
    path('polls/', views.index, name='polls_index'),  # polls/へのアクセスも同じindexビューにマッピング
    
    # 従来のDjangoビュー用のURL
    path('polls/<int:question_id>/', views.detail, name='detail'),
    path('polls/<int:question_id>/results/', views.results, name='results'),
    path('polls/<int:question_id>/vote/', views.vote, name='vote'),
    
    # API用のURL
    path('api/', include(router.urls)),
    path('api/create-survey/', views.create_survey, name='create-survey'),
    path('api/questions/<int:question_id>/', views.question_detail, name='question-detail'),
    path('api/surveys/', views.survey_list, name='survey_list'),
    path('api/surveys/<int:survey_id>/', views.survey_detail, name='survey_detail'),
    
    # アンケート関連のURL
    path('surveys/<int:survey_id>/', views.survey_detail_view, name='survey_detail'),
    path('surveys/<int:survey_id>/response/', views.survey_response_view, name='survey_response'),
    path('api/surveys/<int:survey_id>/submit/', views.submit_survey_response, name='submit_survey_response'),
    path('surveys/create/', views.survey_create_view, name='survey_create'),
]