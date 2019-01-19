from django.shortcuts import render
from django.utils import timezone

from .models import Blog, Category


def search(request, slug=''):
    categories = Category.objects.all()
    if slug is not '':
        category = categories.filter(slug=slug).get()
        posts = Blog.objects.filter(category=category.id, posted_on__lte=timezone.now()).order_by('posted_on')
    else:
        posts = ''

    return render(request, 'blog/search.html', {'posts': posts, 'categories': categories, 'cat_slug': slug})



def about_us(request):
    categories = Category.objects.all()[:4]
    return render(request, 'blog/about_us.html', {'categories': categories})


def blog_detail(request, cat_slug, slug, pk):
    categories = Category.objects.all()[:4]
    blog = Blog.increment_view(pk=pk)
    return render(request, 'blog/blog_detail.html', {'blog': blog, 'categories': categories})


def home(request):
    categories = Category.objects.all()[:4]
    carousel_blogs = Blog.objects.filter(posted_on__lte=timezone.now()).order_by('posted_on')[:3]
    popular_blogs = Blog.objects.filter(posted_on__lte=timezone.now()).order_by('views')[:6]
    return render(request, 'blog/home.html',
                  {'carousel_blogs': carousel_blogs, 'popular_blogs': popular_blogs, 'categories': categories})
