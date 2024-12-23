from django.urls import path, include
from rest_framework.routers import DefaultRouter
from polls import views
from .views import get_active_surveys


app_name = 'polls'

# REST frameworkのルーター設定
router = DefaultRouter()
router.register(r'surveys', views.SurveyViewSet, basename='survey-api')

# 通常のユーザー向けURL
main_urlpatterns = [
    path('', views.index, name='index'),
    path('surveys/create/', views.create_survey, name='survey_create'),
    path('surveys/<int:survey_id>/', views.survey_detail_view, name='survey_detail'),
    path('surveys/<int:survey_id>/response/', views.survey_response_view, name='survey_response'),
    path('survey/<int:survey_id>/update-status/', views.update_survey_status, name='update_survey_status'),
    path('survey/<int:survey_id>/submit/', views.submit_survey, name='submit_survey'),

    path('get_active_surveys/', views.get_active_surveys, name='get_active_surveys'),
    path('submit_survey_response/<int:survey_id>/', views.submit_survey, name='submit_survey_response'),


    path('surveys/active/', views.get_active_surveys, name='active_surveys'),
    path('surveys/<int:survey_id>/results/', views.survey_results, name='survey_results'),
]
# API用URL
api_urlpatterns = [
    path('api/', include(router.urls)),
    path('api/create-survey/', views.create_survey, name='create-survey'),
    path('api/questions/<int:question_id>/', views.question_detail, name='question-detail'),
    path('api/surveys/', views.survey_list, name='survey_list'),
    path('api/surveys/<int:survey_id>/', views.survey_detail, name='api_survey_detail'),
    path('api/surveys/<int:survey_id>/submit/', views.submit_survey_response, name='submit_survey_response'),
]

# 両方のURLパターンを結合
urlpatterns = main_urlpatterns + api_urlpatterns + [
    path('surveys/<int:survey_id>/export/', views.export_survey_results, name='export_survey_results'),
]

