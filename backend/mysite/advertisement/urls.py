from django.urls import path
from .views import get_unanswered_surveys

app_name = 'advertisement'

urlpatterns = [
    path('unanswered-surveys/', get_unanswered_surveys, name='unanswered_surveys'),
]