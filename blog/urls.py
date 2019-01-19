from django.conf.urls import url
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/', views.search, name='category'),
    path('about-us/', views.about_us, name='about_us'),
    path('category/<slug:slug>', views.search, name='search'),
    path('<slug:cat_slug>/<slug:slug>-<int:pk>/', views.blog_detail, name='blog_detail'),
    url(r'^markdownx/', include('markdownx.urls')),
    url(r'mdeditor/', include('mdeditor.urls'))
]
