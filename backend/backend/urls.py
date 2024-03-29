"""
URL configuration for backend project.

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
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # frontend urls
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('login/', TemplateView.as_view(template_name='index.html'), name='index'),
    path('signup/', TemplateView.as_view(template_name='index.html'), name='index'),
    path('profile/', TemplateView.as_view(template_name='index.html'), name='index'),
    path('profile/<str:source>/', TemplateView.as_view(template_name='index.html'), name='index'),
    path('feed/', TemplateView.as_view(template_name='index.html'), name='index'),
    path('explore/', TemplateView.as_view(template_name='index.html'), name='index'),
    path('newpost/', TemplateView.as_view(template_name='index.html'), name='index'),
    path('lookup/', TemplateView.as_view(template_name='index.html'), name='index'),

    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    # Route all other URLs to React frontend
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
