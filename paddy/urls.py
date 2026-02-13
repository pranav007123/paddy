"""paddy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.first, name='first'),
    path('index/',views.index, name='home'),
    path('register/',views.register, name='signup'),
    path('register/addreg',views.addreg),
    path('v_register/',views.v_register),
    path('login/',views.login, name='login'),
    path('login/addlogin',views.addlogin),
    path('logout/',views.logout, name='logout'),
    path('recent_diseases',views.recent_diseases),
    path('files',views.files, name='paddy_upload'),
    path('files2',views.files2, name='mango_upload'),
    path('addfile',views.addfile, name='add_paddy_file'),
    path('addfile_mango',views.addfile_mango, name='add_mango_file'),
    path('result',views.result, name='result'),
    path('account/',views.account, name='account'),
    path('shop/', include('shop.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
