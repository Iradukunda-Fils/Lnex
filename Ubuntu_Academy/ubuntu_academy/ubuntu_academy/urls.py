"""
URL configuration for ubuntu_academy project.

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
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings

base_urls = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    # path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('welcome/', lambda request: HttpResponse('<center><h1 style="margin-top: 30%">Welcome to Ubuntu Academy!</h1></center>')),
]

# Handle media url files

media = []

if settings.DEBUG:
    media = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    

# App to be internationalized    

internalization_app_urls = i18n_patterns(
    path('',include("users.urls")), # Wrap your app's URLs
    path('home', include(('home.urls', 'index')))
)

# django-rozetta urls

rosetta = []

if 'rosetta' in settings.INSTALLED_APPS:
    rosetta = [
        re_path(r'^rosetta/', include('rosetta.urls'))
    ]


#Collecting the whole urls together

urlpatterns = [*base_urls, *rosetta, *media,  *internalization_app_urls] 