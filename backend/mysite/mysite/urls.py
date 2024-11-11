<<<<<<< HEAD:backend/mysite/mysite/urls.py
"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
=======
>>>>>>> db00ff0bc5049755fb37bb82f30de6c5a81376e0:backend/survey_project/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
<<<<<<< HEAD:backend/mysite/mysite/urls.py
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
]
=======
    path("survey_app/", include("survey_app.urls")),
    path("admin/", admin.site.urls),
]
>>>>>>> db00ff0bc5049755fb37bb82f30de6c5a81376e0:backend/survey_project/urls.py
