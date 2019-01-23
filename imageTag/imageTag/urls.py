"""imageTag URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include, re_path
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/',views.register, name='register'),
    path('', views.home, name='home' ), 
    path('login/',views.login, name='login'),
    path('upload/', views.upload, name='upload'),
    re_path(r'^searchusername/data=(?P<userName>\w+)/$', views.searchUser, name
        = 'searchusername'),
    re_path(r'searchhashtag/data=(?P<hashTag>\w+)/$', views.searchHashTag, name
        = 'searchHashTag'),
    re_path(r'^getuserimage/data=(?P<userName>\w+)\+id=(?P<idn>\d+)/$',
        views.getUserImage,name = 'getUserImage'),
    re_path(r'^gethashtag/data=(?P<hashTag>\w+)\+id=(?P<idn>\d+)/$',
        views.getHashTag, name = 'getHashTag'),
    path('sharetomsg/', views.shareImageViaPhone, name ='shareImageViaPhone')
]
