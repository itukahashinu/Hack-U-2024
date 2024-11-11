from django.urls import path
<<<<<<< HEAD:backend/mysite/polls/urls.py
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:question_id>/', views.detail, name='detail'),
    path('<int:question_id>/results/', views.results, name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('question/<int:question_id>/', views.question_detail),

]
=======

from . import views

urlpatterns = [
    path("", views.index, name="index"),
]
>>>>>>> db00ff0bc5049755fb37bb82f30de6c5a81376e0:backend/survey_app/urls.py
