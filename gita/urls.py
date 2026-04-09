"""
URL configuration for gita project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('gita/', views.getRandomSloka, name="sloka"),
    path('getChapterName/', views.getChapterName, name="getChapterName"),
    path('getVerse/<int:chpt_no>/<int:verse_no>', views.getVerses, name="getVerse"),
    path('getRandomVerse/', views.getRandomVerse, name="getRandomVerse"),
    path('user/', include('user.urls')),
    path('manager/', include('manager.urls')),
    path('agent/', include('agent.urls')),
    path('', views.start, name="start")
]
