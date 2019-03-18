from django.conf.urls import url
from django.urls import path, include

from blog.views import success_view
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/', views.search, name='category'),
    path('author/<slug:slug>-<int:pk>', views.authors, name='authors'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('category/<slug:slug>', views.search, name='search'),
    path('<slug:cat_slug>/<slug:slug>-<int:pk>/', views.blog_detail, name='blog_detail'),
    url(r'^markdownx/', include('markdownx.urls')),
    url(r'mdeditor/', include('mdeditor.urls')),
    path('success/', success_view, name='success'),
]
